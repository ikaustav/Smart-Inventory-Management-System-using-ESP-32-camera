"""
Alerts Module
==============
Alert logging widget.

Contains ONLY:
    * AlertLog
"""

from datetime import datetime
import tkinter as tk

from config import (
    PANEL_BG, CARD_BG, TEXT_PRIMARY, TEXT_MUTED, ACCENT,
    DANGER, WARN, SUCCESS, FONT_HEADING, FONT_SMALL,
)


# ══════════════════════════════════════════════════════════════════════════════
#  ALERT LOG
# ══════════════════════════════════════════════════════════════════════════════
class AlertLog(tk.Frame):
    """Scrollable, color-coded timestamped log of inventory alerts."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=PANEL_BG, **kw)
        tk.Label(self, text="ALERT LOG", font=FONT_HEADING,
                 bg=PANEL_BG, fg=ACCENT, padx=10, pady=6).pack(anchor="w")
        self.text = tk.Text(self, font=FONT_SMALL, bg=CARD_BG, fg=TEXT_PRIMARY,
                            relief="flat", state="disabled", height=7,
                            wrap="word", padx=8, pady=4)
        self.text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.text.tag_configure("DANGER",  foreground=DANGER)
        self.text.tag_configure("WARN",    foreground=WARN)
        self.text.tag_configure("SUCCESS", foreground=SUCCESS)
        self.text.tag_configure("MUTED",   foreground=TEXT_MUTED)

    def log(self, msg, level="MUTED"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.text.config(state="normal")
        self.text.insert("end", f"[{ts}]  ", "MUTED")
        self.text.insert("end", f"{msg}\n", level)
        self.text.see("end")
        self.text.config(state="disabled")
