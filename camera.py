"""
Camera Module
==============
ESP32-CAM communication panel.

Contains ONLY:
    * CameraPanel

Everything related to ESP32 streaming, snapshot capture, HTTP communication,
and the threading used to keep the GUI responsive is preserved exactly as in
the original implementation.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import math
import io
from datetime import datetime

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

import urllib.request
import urllib.error

from config import (
    PANEL_BG, BORDER, ACCENT, ACCENT2, WARN, DANGER, SUCCESS,
    TEXT_PRIMARY, TEXT_MUTED, CARD_BG,
    FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_MONO,
)
from detector import ObjectDetector


# ══════════════════════════════════════════════════════════════════════════════
#  CAMERA PANEL
# ══════════════════════════════════════════════════════════════════════════════
class CameraPanel(tk.Frame):
    """ESP32-CAM live view panel: streaming, snapshot capture, and detection overlay."""

    def __init__(self, parent, on_count_cb, **kw):
        super().__init__(parent, bg=PANEL_BG, **kw)
        self.on_count_cb   = on_count_cb
        self.ip_var        = tk.StringVar(value="10.50.151.178")
        self.stream_url    = tk.StringVar(value="http://10.50.151.178/stream")
        self.snapshot_url  = tk.StringVar(value="http://10.50.151.178/capture")
        self._probe_urls   = [
            "http://10.50.151.178/stream",
            "http://10.50.151.178:81/stream",
            "http://10.50.151.178/",
            "http://10.50.151.178:80/stream",
            "http://10.50.151.178/mjpeg/1",
        ]
        self.is_streaming  = False
        self._last_frame   = None
        self._thread       = None
        self._mode         = "none"
        self.detector      = ObjectDetector()
        self.detect_enabled = tk.BooleanVar(value=True)
        self._last_count   = -1
        self._build()
        self._render_placeholder()

    def _build(self):
        hdr = tk.Frame(self, bg=BORDER)
        hdr.pack(fill="x")
        tk.Label(hdr, text="◉ LIVE CAMERA FEED  —  ESP32-CAM",
                 font=FONT_HEADING, bg=BORDER, fg=ACCENT, padx=12, pady=6).pack(side="left")
        self.lbl_det = tk.Label(hdr, text="DETECTED: 0",
                                font=FONT_HEADING, bg=BORDER, fg=SUCCESS)
        self.lbl_det.pack(side="right", padx=16)
        self.lbl_status = tk.Label(hdr, text="● OFFLINE",
                                   font=FONT_SMALL, bg=BORDER, fg=DANGER)
        self.lbl_status.pack(side="right", padx=12)

        self.canvas = tk.Canvas(self, bg="#060810", width=640, height=360,
                                highlightthickness=1, highlightbackground=BORDER,
                                cursor="crosshair")
        self.canvas.pack()

        # Zone drawing via mouse drag
        self._drag_start = None
        self._drag_rect  = None
        self.canvas.bind("<ButtonPress-1>",   self._zone_start)
        self.canvas.bind("<B1-Motion>",        self._zone_drag)
        self.canvas.bind("<ButtonRelease-1>",  self._zone_end)
        self.canvas.bind("<ButtonPress-3>",    self._zone_clear)  # right-click clears

        row1 = tk.Frame(self, bg=PANEL_BG)
        row1.pack(fill="x", padx=10, pady=(6, 2))
        tk.Label(row1, text="ESP32 IP:", font=FONT_SMALL,
                 bg=PANEL_BG, fg=TEXT_MUTED).pack(side="left")
        ip_ent = tk.Entry(row1, textvariable=self.ip_var, width=16,
                          font=FONT_MONO, bg=CARD_BG, fg=ACCENT,
                          insertbackground=ACCENT, relief="flat")
        ip_ent.pack(side="left", padx=6)
        ip_ent.bind("<Return>",   self._apply_ip)
        ip_ent.bind("<FocusOut>", self._apply_ip)
        tk.Button(row1, text="Apply IP", font=FONT_SMALL, bg=BORDER,
                  fg=TEXT_MUTED, relief="flat", cursor="hand2",
                  padx=8, command=self._apply_ip).pack(side="left", padx=2)
        tk.Label(row1, text="  Stream URL:", font=FONT_SMALL,
                 bg=PANEL_BG, fg=TEXT_MUTED).pack(side="left")
        tk.Entry(row1, textvariable=self.stream_url, width=28,
                 font=FONT_MONO, bg=CARD_BG, fg=ACCENT,
                 insertbackground=ACCENT, relief="flat").pack(side="left", padx=4)

        row2 = tk.Frame(self, bg=PANEL_BG)
        row2.pack(fill="x", padx=10, pady=(0, 4))
        self.btn_connect = tk.Button(
            row2, text="▶  CONNECT STREAM", font=FONT_BODY,
            bg=ACCENT2, fg="white", relief="flat", cursor="hand2",
            padx=12, command=self._toggle_stream)
        self.btn_connect.pack(side="left", padx=(0, 6))
        tk.Button(row2, text="📷  SNAPSHOT", font=FONT_BODY,
                  bg=BORDER, fg=TEXT_PRIMARY, relief="flat", cursor="hand2",
                  padx=10, command=self._take_snapshot).pack(side="left", padx=(0, 6))
        tk.Button(row2, text="DEMO MODE", font=FONT_BODY,
                  bg=BORDER, fg=TEXT_MUTED, relief="flat", cursor="hand2",
                  padx=10, command=self._start_demo).pack(side="left", padx=(0, 10))
        tk.Checkbutton(row2, text="AUTO DETECT", variable=self.detect_enabled,
                       font=FONT_SMALL, bg=PANEL_BG, fg=SUCCESS,
                       selectcolor=CARD_BG, activebackground=PANEL_BG).pack(side="left", padx=(0, 8))
        tk.Label(row2, text="Min size:", font=FONT_SMALL,
                 bg=PANEL_BG, fg=TEXT_MUTED).pack(side="left")
        self.sens_var = tk.StringVar(value="800")
        sens_ent = tk.Entry(row2, textvariable=self.sens_var, width=5,
                            font=FONT_MONO, bg=CARD_BG, fg=WARN,
                            insertbackground=WARN, relief="flat", justify="center")
        sens_ent.pack(side="left", padx=4)
        sens_ent.bind("<Return>",   self._apply_sensitivity)
        sens_ent.bind("<FocusOut>", self._apply_sensitivity)
        tk.Label(row2, text="px²",
                 font=FONT_SMALL, bg=PANEL_BG, fg=TEXT_MUTED).pack(side="left")
        tk.Button(row2, text="✕ CLEAR ZONE", font=FONT_SMALL,
                  bg=DANGER, fg="white", relief="flat", cursor="hand2",
                  padx=8, command=self._zone_clear).pack(side="left", padx=(10,0))

    def _apply_ip(self, _=None):
        ip = self.ip_var.get().strip()
        self.stream_url.set(f"http://{ip}/stream")
        self.snapshot_url.set(f"http://{ip}/capture")
        self._probe_urls = [
            f"http://{ip}/stream",
            f"http://{ip}:81/stream",
            f"http://{ip}/",
            f"http://{ip}:80/stream",
            f"http://{ip}/mjpeg/1",
        ]

    def _apply_sensitivity(self, _=None):
        try:
            self.detector.min_area = int(self.sens_var.get())
        except ValueError:
            self.sens_var.set(str(self.detector.min_area))

    def _set_status(self, text, color):
        self.lbl_status.after(0, lambda: self.lbl_status.config(text=text, fg=color))

    def _show_frame(self, img):
        if self.detect_enabled.get() and HAS_CV2:
            annotated, count = self.detector.detect(img)
            if count != self._last_count:
                self._last_count = count
                self.lbl_det.after(0, lambda c=count: self.lbl_det.config(
                    text=f"DETECTED: {c}",
                    fg=SUCCESS if c > 0 else TEXT_MUTED))
                self.on_count_cb(count)
            display = annotated
        else:
            display = img
        display = display.resize((640, 360))
        photo   = ImageTk.PhotoImage(display)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=photo)
        self.canvas._photo = photo

    # ── Zone drawing ─────────────────────────────────────────────────────────
    def _zone_start(self, e):
        self._drag_start = (e.x, e.y)
        if self._drag_rect:
            self.canvas.delete(self._drag_rect)
            self._drag_rect = None

    def _zone_drag(self, e):
        if not self._drag_start: return
        if self._drag_rect:
            self.canvas.delete(self._drag_rect)
        x0, y0 = self._drag_start
        self._drag_rect = self.canvas.create_rectangle(
            x0, y0, e.x, e.y,
            outline="#00e5ff", width=2, dash=(6, 3))

    def _zone_end(self, e):
        if not self._drag_start: return
        x0, y0 = self._drag_start
        x1, y1 = e.x, e.y
        cw, ch = 640, 360
        # Convert pixel coords to 0.0-1.0 fractions
        self.detector.set_zone(
            x0/cw, y0/ch, x1/cw, y1/ch)
        self._drag_start = None

    def _zone_clear(self, e=None):
        self.detector.clear_zone()
        if self._drag_rect:
            self.canvas.delete(self._drag_rect)
            self._drag_rect = None

    def _render_placeholder(self):
        self.canvas.delete("all")
        w, h = 640, 360
        for y in range(0, h, 4):
            self.canvas.create_line(0, y, w, y, fill="#0a0d18")
        cx, cy = w//2, h//2
        # soft neon glow halo behind the target circle (glassmorphism accent)
        self.canvas.create_oval(cx-72, cy-72, cx+72, cy+72,
                                outline=ACCENT, width=2, stipple="gray25")
        self.canvas.create_oval(cx-60, cy-60, cx+60, cy+60, outline=ACCENT, width=2)
        self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill=ACCENT, outline="")
        for a in range(0, 360, 45):
            r = math.radians(a)
            self.canvas.create_line(cx+70*math.cos(r), cy+70*math.sin(r),
                                    cx+82*math.cos(r), cy+82*math.sin(r), fill=TEXT_MUTED)
        self.canvas.create_text(cx, cy+110,
                                text="NO SIGNAL  —  Set ESP32 IP and press CONNECT STREAM",
                                fill=TEXT_MUTED, font=FONT_SMALL)

    def _mjpeg_loop(self):
        url = self.stream_url.get()
        try:
            req  = urllib.request.Request(url, headers={"User-Agent": "ESP32Viewer"})
            resp = urllib.request.urlopen(req, timeout=10)
            self._set_status("● LIVE (MJPEG)", SUCCESS)
            buf = b""
            SOI, EOI = b"\xff\xd8", b"\xff\xd9"
            while self.is_streaming:
                buf += resp.read(4096)
                while True:
                    s = buf.find(SOI)
                    e = buf.find(EOI, s+2)
                    if s == -1 or e == -1: break
                    jpeg = buf[s:e+2]
                    buf  = buf[e+2:]
                    try:
                        img = Image.open(io.BytesIO(jpeg))
                        img.load()
                        self._last_frame = img.convert("RGB")
                    except Exception:
                        pass
        except urllib.error.URLError as e:
            self._set_status(f"● CONN ERR: {e.reason}", DANGER)
            self._snapshot_loop()
        except Exception as e:
            self._set_status(f"● ERROR: {e}", DANGER)

    def _snapshot_loop(self):
        self._set_status("● SNAPSHOT MODE", WARN)
        url = self.snapshot_url.get()
        while self.is_streaming:
            try:
                data = urllib.request.urlopen(url, timeout=5).read()
                img  = Image.open(io.BytesIO(data)).convert("RGB")
                self._last_frame = img
                self._set_status("● LIVE (snapshot)", SUCCESS)
            except Exception as e:
                self._set_status(f"● ERR: {e}", DANGER)
            time.sleep(0.1)

    def _cv2_loop(self):
        try:
            cap = cv2.VideoCapture(self.stream_url.get())
            if not cap.isOpened(): raise RuntimeError("failed")
            self._set_status("● LIVE (cv2)", SUCCESS)
            while self.is_streaming:
                ret, frame = cap.read()
                if ret:
                    self._last_frame = Image.fromarray(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                else:
                    time.sleep(0.03)
            cap.release()
        except Exception:
            self._mjpeg_loop()

    def _render_loop(self):
        if not self.is_streaming: return
        if self._last_frame is not None:
            self._show_frame(self._last_frame)
        self.after(33, self._render_loop)

    def _toggle_stream(self):
        if self.is_streaming:
            self.is_streaming = False
            self._mode = "none"
            self.btn_connect.config(text="▶  CONNECT STREAM", bg=ACCENT2)
            self._set_status("● OFFLINE", DANGER)
            self._last_frame = None
            self._render_placeholder()
        else:
            self._connect()

    def _connect(self):
        if not HAS_PIL:
            messagebox.showerror("Missing", "pip install pillow")
            return
        self.is_streaming = True
        self._mode = "stream"
        self._last_frame = None
        self.btn_connect.config(text="■  DISCONNECT", bg=DANGER)
        self._set_status("● CONNECTING…", WARN)

        def _run():
            if HAS_CV2:
                self._cv2_loop()
            else:
                self._mjpeg_loop()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        self._render_loop()

    def _take_snapshot(self):
        if not HAS_PIL:
            messagebox.showerror("Missing", "pip install pillow")
            return
        def _fetch():
            try:
                data = urllib.request.urlopen(self.snapshot_url.get(), timeout=5).read()
                img  = Image.open(io.BytesIO(data)).convert("RGB")
                self._last_frame = img
                self.canvas.after(0, lambda: self._show_frame(img))
                self._set_status("● SNAPSHOT OK", SUCCESS)
            except Exception as e:
                self._set_status(f"● SNAP ERR: {e}", DANGER)
        threading.Thread(target=_fetch, daemon=True).start()

    def _start_demo(self):
        if self.is_streaming:
            self._toggle_stream()
        self.is_streaming = True
        self._mode = "demo"
        self._set_status("● DEMO", WARN)
        self.btn_connect.config(text="■  STOP DEMO", bg=DANGER)
        self._demo_frame = 0
        self._demo_tick()

    def _demo_tick(self):
        if not self.is_streaming or self._mode != "demo": return
        self._draw_demo()
        self.after(33, self._demo_tick)

    def _draw_demo(self):
        self.canvas.delete("all")
        t = self._demo_frame * 0.04
        w, h = 640, 360
        for y in range(0, h, 3):
            lum = int(8 + 4 * math.sin(y * 0.02 + t))
            self.canvas.create_line(0, y, w, y,
                                    fill=f"#{lum:02x}{lum+2:02x}{lum+6:02x}")
        labels = ["BOX A", "BOTTLE", "CAN", "BAG", "PART"]
        for i in range(5):
            bx = 60 + i*118 + int(8*math.sin(t+i))
            by = h//2 + int(10*math.cos(t*0.7+i*1.2))
            bw = 55 + int(5*math.sin(t+i*0.5))
            self.canvas.create_rectangle(bx-bw//2, by-40, bx+bw//2, by+40,
                                         fill="#1a2a3a", outline="#00e5ff44", width=2)
            self.canvas.create_text(bx, by-10, text=f"#{i+1}", fill=SUCCESS, font=FONT_SMALL)
            self.canvas.create_text(bx, by+8,  text=labels[i], fill=ACCENT,  font=FONT_SMALL)
        self.canvas.create_rectangle(0, 0, 200, 28, fill="#000000")
        self.canvas.create_text(6, 14, anchor="w", text="OBJECTS DETECTED: 5",
                                fill=ACCENT, font=FONT_SMALL)
        self.canvas.create_text(w-6, 14, anchor="e",
                                text=datetime.now().strftime("%H:%M:%S"),
                                fill=ACCENT, font=FONT_SMALL)
        self._demo_frame += 1
