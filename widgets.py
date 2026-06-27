"""
Widgets Module
================
Custom Tkinter widgets.

Contains ONLY:
    * StockBar
    * PulseBadge
    * ItemCard
    * SummaryBar
    * AddItemDialog

No application/orchestration logic lives in this module.
"""

import math
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

from config import (
    DARK_BG, CARD_BG, BORDER, ACCENT, WARN, DANGER, SUCCESS,
    TEXT_PRIMARY, TEXT_MUTED,
    FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_MONO,
)
from inventory import InventoryItem


# ══════════════════════════════════════════════════════════════════════════════
#  ANIMATED STOCK BAR
# ══════════════════════════════════════════════════════════════════════════════
class StockBar(tk.Canvas):
    """Animated horizontal bar showing an item's fill percentage."""

    def __init__(self, parent, item, **kw):
        super().__init__(parent, height=12, bg=CARD_BG, highlightthickness=0, **kw)
        self.item      = item
        self._anim_pct = 0.0
        self.bind("<Configure>", lambda e: self._draw())
        self._tick()

    def _tick(self):
        target = self.item.fill_pct
        diff   = target - self._anim_pct
        if abs(diff) > 0.001:
            self._anim_pct += diff * 0.12
            self._draw()
        self.after(30, self._tick)

    def _draw(self):
        w = self.winfo_width()
        if w < 2: return
        self.delete("all")
        self.create_rectangle(0, 2, w, 10, fill="#1e2235", outline="")
        fw = max(0, int(w * self._anim_pct))
        if fw > 2:
            c = self.item.status_color
            r = min(255, int(c[1:3], 16) + 40)
            g = min(255, int(c[3:5], 16) + 40)
            b = min(255, int(c[5:7], 16) + 40)
            glow = f"#{r:02x}{g:02x}{b:02x}"
            # soft outer glow halo behind the fill (glassmorphism accent)
            self.create_rectangle(0, 0, fw, 12, fill=c, outline="", stipple="gray25")
            self.create_rectangle(0, 2, fw, 10, fill=c, outline="")
            self.create_rectangle(0, 2, fw, 5, fill=glow, outline="")
            if fw > 6:
                # rounded leading edge — soft pill-style cap
                self.create_oval(fw-6, 2, fw, 10, fill=glow, outline="")


# ══════════════════════════════════════════════════════════════════════════════
#  PULSE BADGE
# ══════════════════════════════════════════════════════════════════════════════
class PulseBadge(tk.Canvas):
    """Small pulsing indicator badge used to signal active alerts."""

    def __init__(self, parent, **kw):
        super().__init__(parent, width=14, height=14, bg=CARD_BG,
                         highlightthickness=0, **kw)
        self._phase  = 0.0
        self._active = False
        self._color  = DANGER
        self._tick()

    def activate(self, color=DANGER):
        self._active = True
        self._color  = color

    def deactivate(self):
        self._active = False
        self.delete("all")

    def _tick(self):
        if self._active:
            self._phase = (self._phase + 0.08) % (2 * math.pi)
            self.delete("all")
            r = 5 + int(2 * abs(math.sin(self._phase)))
            # soft outer glow halo (glassmorphism accent)
            self.create_oval(7-r-3, 7-r-3, 7+r+3, 7+r+3,
                             outline=self._color, width=1, stipple="gray25")
            self.create_oval(7-r, 7-r, 7+r, 7+r, outline=self._color, width=1)
            self.create_oval(3, 3, 11, 11, fill=self._color, outline="")
        self.after(40, self._tick)


# ══════════════════════════════════════════════════════════════════════════════
#  ITEM CARD
# ══════════════════════════════════════════════════════════════════════════════
class ItemCard(tk.Frame):
    """Card widget showing a single inventory item with live controls."""

    def __init__(self, parent, item, on_change_cb, **kw):
        super().__init__(parent, bg=CARD_BG, **kw)
        self.item      = item
        self.on_change = on_change_cb
        self._build()
        self._refresh_loop()

    def _build(self):
        self.config(padx=14, pady=10)
        top = tk.Frame(self, bg=CARD_BG)
        top.pack(fill="x")

        left = tk.Frame(top, bg=CARD_BG)
        left.pack(side="left", fill="x", expand=True)

        self.badge = PulseBadge(left)
        self.badge.pack(side="left", padx=(0, 6))

        tk.Label(left, text=self.item.name.upper(), font=FONT_HEADING,
                 bg=CARD_BG, fg=TEXT_PRIMARY).pack(side="left")

        self.lbl_count = tk.Label(top, text=str(self.item.count),
                                  font=("Courier New", 22, "bold"),
                                  bg=CARD_BG, fg=ACCENT)
        self.lbl_count.pack(side="right", padx=4)
        tk.Label(top, text="units", font=FONT_SMALL,
                 bg=CARD_BG, fg=TEXT_MUTED).pack(side="right")

        self.bar = StockBar(self, self.item)
        self.bar.pack(fill="x", pady=(6, 4))

        ctrl = tk.Frame(self, bg=CARD_BG)
        ctrl.pack(fill="x")

        btn_s = dict(font=FONT_BODY, bg=BORDER, fg=TEXT_PRIMARY,
                     activebackground=ACCENT, activeforeground=DARK_BG,
                     relief="flat", cursor="hand2", width=3)
        tk.Button(ctrl, text="−",   **btn_s, command=lambda: self._change(-1)).pack(side="left", padx=(0,2))
        tk.Button(ctrl, text="+",   **btn_s, command=lambda: self._change(+1)).pack(side="left", padx=(0,8))
        tk.Button(ctrl, text="−10", **btn_s, command=lambda: self._change(-10)).pack(side="left", padx=(0,2))
        tk.Button(ctrl, text="+10", **btn_s, command=lambda: self._change(+10)).pack(side="left", padx=(0,8))

        tk.Label(ctrl, text="Restock @", font=FONT_SMALL,
                 bg=CARD_BG, fg=TEXT_MUTED).pack(side="left")
        self.thresh_var = tk.StringVar(value=str(self.item.restock_threshold))
        ent = tk.Entry(ctrl, textvariable=self.thresh_var, width=4,
                       font=FONT_MONO, bg=BORDER, fg=WARN,
                       insertbackground=WARN, relief="flat", justify="center")
        ent.pack(side="left", padx=4)
        ent.bind("<Return>",   self._apply_threshold)
        ent.bind("<FocusOut>", self._apply_threshold)
        tk.Label(ctrl, text="units", font=FONT_SMALL,
                 bg=CARD_BG, fg=TEXT_MUTED).pack(side="left")

        self.lbl_status = tk.Label(self, text="", font=FONT_SMALL,
                                   bg=CARD_BG, fg=TEXT_MUTED)
        self.lbl_status.pack(anchor="w", pady=(4, 0))

    def _change(self, delta):
        self.item.set_count(self.item.count + delta)
        self._refresh()
        self.on_change()

    def _apply_threshold(self, _=None):
        try:
            self.item.set_threshold(int(self.thresh_var.get()))
            self._refresh()
            self.on_change()
        except ValueError:
            self.thresh_var.set(str(self.item.restock_threshold))

    def _refresh(self):
        self.lbl_count.config(text=str(self.item.count), fg=self.item.status_color)
        if self.item.needs_restock:
            if self.item.count == 0:
                self.badge.activate(DANGER)
                self.lbl_status.config(text="⚠  OUT OF STOCK — restock immediately!", fg=DANGER)
            else:
                self.badge.activate(WARN)
                self.lbl_status.config(
                    text=f"⚡  LOW STOCK — only {self.item.count} left (threshold: {self.item.restock_threshold})",
                    fg=WARN)
        else:
            self.badge.deactivate()
            self.lbl_status.config(
                text=f"✓  Stock OK  ({int(self.item.fill_pct*100)}% full)", fg=SUCCESS)

    def _refresh_loop(self):
        self._refresh()
        self.after(500, self._refresh_loop)

    def set_count_from_camera(self, count):
        """Called by object detection to update count automatically."""
        self.item.set_count(count)
        self._refresh()
        self.on_change()


# ══════════════════════════════════════════════════════════════════════════════
#  SUMMARY BAR
# ══════════════════════════════════════════════════════════════════════════════
class SummaryBar(tk.Frame):
    """Top-level dashboard summary showing aggregate inventory statistics."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BORDER, **kw)
        self._cards = {}
        for key, label, color in [
            ("total", "TOTAL UNITS",  TEXT_PRIMARY),
            ("items", "ITEM TYPES",   ACCENT),
            ("ok",    "STOCKED OK",   SUCCESS),
            ("low",   "LOW STOCK",    WARN),
            ("out",   "OUT OF STOCK", DANGER),
        ]:
            f = tk.Frame(self, bg=BORDER)
            f.pack(side="left", padx=20, pady=8)
            tk.Label(f, text=label, font=FONT_SMALL, bg=BORDER, fg=TEXT_MUTED).pack()
            lbl = tk.Label(f, text="—", font=("Courier New", 18, "bold"),
                           bg=BORDER, fg=color)
            lbl.pack()
            self._cards[key] = lbl
        self.lbl_time = tk.Label(self, font=FONT_MONO, bg=BORDER, fg=TEXT_MUTED)
        self.lbl_time.pack(side="right", padx=20)
        self._tick()

    def _tick(self):
        self.lbl_time.config(text=datetime.now().strftime("%a  %d %b %Y   %H:%M:%S"))
        self.after(1000, self._tick)

    def update(self, items):
        self._cards["total"].config(text=str(sum(i.count for i in items)))
        self._cards["items"].config(text=str(len(items)))
        self._cards["ok"].config(text=str(sum(1 for i in items if not i.needs_restock)))
        self._cards["low"].config(text=str(sum(1 for i in items if i.needs_restock and i.count > 0)))
        self._cards["out"].config(text=str(sum(1 for i in items if i.count == 0)))


# ══════════════════════════════════════════════════════════════════════════════
#  ADD ITEM DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class AddItemDialog(tk.Toplevel):
    """Modal dialog for creating a new InventoryItem."""

    def __init__(self, parent, on_add_cb):
        super().__init__(parent)
        self.on_add = on_add_cb
        self.title("Add Inventory Item")
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        self.grab_set()
        tk.Label(self, text="NEW ITEM", font=FONT_HEADING,
                 bg=DARK_BG, fg=ACCENT, pady=12).pack()
        fields = [
            ("Item name",         "name",      "New Item"),
            ("Initial stock",     "count",     "50"),
            ("Restock threshold", "threshold", "10"),
            ("Max capacity",      "max",       "100"),
        ]
        self.vars = {}
        for label, key, default in fields:
            row = tk.Frame(self, bg=DARK_BG)
            row.pack(fill="x", padx=20, pady=3)
            tk.Label(row, text=label, width=18, anchor="w",
                     font=FONT_BODY, bg=DARK_BG, fg=TEXT_MUTED).pack(side="left")
            var = tk.StringVar(value=default)
            tk.Entry(row, textvariable=var, font=FONT_MONO, bg=CARD_BG,
                     fg=ACCENT, insertbackground=ACCENT,
                     relief="flat", width=14).pack(side="left", padx=6)
            self.vars[key] = var
        btn_row = tk.Frame(self, bg=DARK_BG)
        btn_row.pack(pady=16)
        tk.Button(btn_row, text="ADD", font=FONT_BODY, bg=SUCCESS,
                  fg=DARK_BG, relief="flat", cursor="hand2",
                  padx=16, command=self._submit).pack(side="left", padx=6)
        tk.Button(btn_row, text="CANCEL", font=FONT_BODY, bg=BORDER,
                  fg=TEXT_PRIMARY, relief="flat", cursor="hand2",
                  padx=16, command=self.destroy).pack(side="left", padx=6)

    def _submit(self):
        try:
            item = InventoryItem(
                name=self.vars["name"].get() or "Unnamed",
                count=int(self.vars["count"].get()),
                restock_threshold=int(self.vars["threshold"].get()),
                max_capacity=int(self.vars["max"].get()),
            )
            self.on_add(item)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.", parent=self)
