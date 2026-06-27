"""
GUI Module
===========
Main application window.

Contains ONLY:
    * InventoryApp

This module assembles the camera panel, alert log, summary bar, and
inventory item cards into the complete desktop application. It does not
define ObjectDetector, CameraPanel, InventoryItem, StockBar, or any other
component — those are imported from their respective modules.
"""

import tkinter as tk

from config import (
    DARK_BG, CARD_BG, BORDER, ACCENT, ACCENT2, TEXT_MUTED,
    FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL,
)
from inventory import InventoryItem
from camera import CameraPanel
from alerts import AlertLog
from widgets import SummaryBar, ItemCard, AddItemDialog


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class InventoryApp(tk.Tk):
    """Top-level Tkinter application assembling all inventory system components."""

    def __init__(self):
        super().__init__()
        self.title("ESP32-CAM  ·  Inventory Management System")
        self.configure(bg=DARK_BG)
        self.geometry("1280x860")
        self.minsize(1100, 700)

        self.items = [
            InventoryItem("Item A", count=20, restock_threshold=10, max_capacity=100),
            InventoryItem("Item B", count=5,  restock_threshold=8,  max_capacity=50),
            InventoryItem("Item C", count=45, restock_threshold=15, max_capacity=100),
            InventoryItem("Item D", count=0,  restock_threshold=5,  max_capacity=30),
        ]
        self._cam_item_idx = 0
        self._build_ui()
        self._monitor_loop()

    def _build_ui(self):
        title_bar = tk.Frame(self, bg=DARK_BG)
        title_bar.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(title_bar, text="ESP32-CAM",
                 font=FONT_TITLE, bg=DARK_BG, fg=ACCENT).pack(side="left")
        tk.Label(title_bar, text="  INVENTORY  SYSTEM",
                 font=FONT_TITLE, bg=DARK_BG, fg=ACCENT2).pack(side="left")
        tk.Label(title_bar, text="v2.0  +detection", font=FONT_SMALL,
                 bg=DARK_BG, fg=TEXT_MUTED).pack(side="left", padx=8, pady=6)
        tk.Button(title_bar, text="+ ADD ITEM", font=FONT_BODY,
                  bg=ACCENT2, fg="white", relief="flat", cursor="hand2",
                  padx=12, command=self._open_add_dialog).pack(side="right")

        self.summary = SummaryBar(self)
        self.summary.pack(fill="x")

        content = tk.Frame(self, bg=DARK_BG)
        content.pack(fill="both", expand=True, padx=12, pady=10)

        left = tk.Frame(content, bg=DARK_BG)
        left.pack(side="left", fill="both", expand=True)

        self.cam = CameraPanel(left, on_count_cb=self._on_detection)
        self.cam.pack(fill="x")

        # Camera → item binding
        bind_row = tk.Frame(left, bg=DARK_BG)
        bind_row.pack(fill="x", pady=(4, 0))
        tk.Label(bind_row, text="Camera updates item:",
                 font=FONT_SMALL, bg=DARK_BG, fg=TEXT_MUTED).pack(side="left", padx=4)
        self.cam_item_var = tk.StringVar(value=self.items[0].name)
        self.cam_item_menu = tk.OptionMenu(bind_row, self.cam_item_var,
                                           *[i.name for i in self.items],
                                           command=self._update_cam_item)
        self.cam_item_menu.config(font=FONT_SMALL, bg=CARD_BG, fg=ACCENT,
                                  relief="flat", highlightthickness=0)
        self.cam_item_menu.pack(side="left", padx=4)
        tk.Label(bind_row,
                 text="← select which item the camera object count controls",
                 font=FONT_SMALL, bg=DARK_BG, fg=TEXT_MUTED).pack(side="left", padx=4)

        self.log = AlertLog(left)
        self.log.pack(fill="both", expand=True, pady=(8, 0))
        self.log.log("System started. Object detection ENABLED.", "SUCCESS")
        self.log.log("Tip: DRAG on camera feed to set shelf zone. Right-click to clear.", "MUTED")

        right_outer = tk.Frame(content, bg=DARK_BG, width=360)
        right_outer.pack(side="right", fill="both", padx=(12, 0))
        right_outer.pack_propagate(False)
        tk.Label(right_outer, text="INVENTORY", font=FONT_HEADING,
                 bg=DARK_BG, fg=ACCENT, pady=6).pack(anchor="w")

        canvas = tk.Canvas(right_outer, bg=DARK_BG, highlightthickness=0)
        sb = tk.Scrollbar(right_outer, orient="vertical",
                          command=canvas.yview, bg=BORDER)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.cards_frame = tk.Frame(canvas, bg=DARK_BG)
        win = canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.cards_frame.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._render_cards()
        self.summary.update(self.items)

    def _render_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        self._item_cards = []
        for item in self.items:
            card = ItemCard(self.cards_frame, item, self._on_item_change)
            card.pack(fill="x", pady=4, padx=2)
            tk.Frame(self.cards_frame, bg=BORDER, height=1).pack(fill="x")
            self._item_cards.append(card)

    def _on_item_change(self):
        self.summary.update(self.items)

    def _update_cam_item(self, name):
        for i, item in enumerate(self.items):
            if item.name == name:
                self._cam_item_idx = i
                break

    def _on_detection(self, count):
        if 0 <= self._cam_item_idx < len(self._item_cards):
            self._item_cards[self._cam_item_idx].set_count_from_camera(count)
            self.log.log(
                f"Camera detected {count} object(s) → '{self.items[self._cam_item_idx].name}'",
                "SUCCESS" if count > 0 else "WARN")

    def _open_add_dialog(self):
        AddItemDialog(self, self._add_item)

    def _add_item(self, item):
        self.items.append(item)
        self._render_cards()
        self.summary.update(self.items)
        menu = self.cam_item_menu["menu"]
        menu.delete(0, "end")
        for i in self.items:
            menu.add_command(label=i.name,
                             command=lambda n=i.name: (
                                 self.cam_item_var.set(n),
                                 self._update_cam_item(n)))
        self.log.log(f"Added item: {item.name}", "SUCCESS")

    def _monitor_loop(self):
        for item in self.items:
            if item.needs_restock and not item.alert_triggered:
                item.alert_triggered = True
                if item.count == 0:
                    self.log.log(f"OUT OF STOCK: {item.name}", "DANGER")
                else:
                    self.log.log(
                        f"LOW STOCK: {item.name} — {item.count} left "
                        f"(threshold ≤{item.restock_threshold})", "WARN")
            elif not item.needs_restock and item.alert_triggered:
                item.alert_triggered = False
                self.log.log(f"Restocked: {item.name} ✓", "SUCCESS")
        self.summary.update(self.items)
        self.after(1500, self._monitor_loop)
