"""
Inventory Module
=================
Inventory business logic.

Contains ONLY:
    * InventoryItem

NO GUI. NO OpenCV. NO Camera code lives in this module.
"""

from config import ACCENT, DANGER, SUCCESS, WARN


class InventoryItem:
    """Represents a single inventory item with stock-level business logic."""

    def __init__(self, name, count=0, restock_threshold=10, max_capacity=100):
        self.name              = name
        self.count             = count
        self.restock_threshold = restock_threshold
        self.max_capacity      = max_capacity
        self.needs_restock     = False
        self.alert_triggered   = False
        self._update_status()

    def _update_status(self):
        self.needs_restock = self.count <= self.restock_threshold

    def set_count(self, val):
        self.count = max(0, min(val, self.max_capacity))
        self._update_status()

    def set_threshold(self, val):
        self.restock_threshold = max(0, val)
        self._update_status()

    @property
    def fill_pct(self):
        return self.count / self.max_capacity if self.max_capacity else 0

    @property
    def status_color(self):
        if self.count == 0:       return DANGER
        if self.needs_restock:    return WARN
        if self.fill_pct > 0.7:   return SUCCESS
        return ACCENT
