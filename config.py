"""
Configuration Module
=====================
Central configuration for the ESP32-CAM Inventory Management System.

Contains ONLY:
    * Theme colors
    * Fonts
    * Window / layout constants

NO LOGIC lives in this module — values only.

Design system
-------------
Premium dark / glassmorphism theme inspired by Apple HIG, Linear, Stripe,
Arc, Raycast, Notion and Vercel dashboards. The previous revision kept the
same color *families* as the original (cyan stayed cyan, violet stayed
violet) which read as "almost the same." This revision deliberately shifts
to a different hue family on a neutral graphite base — modeled on Apple's
Dark Mode system palette (sapphire blue / vivid purple / orange / red /
green) — so the change is obvious at a glance rather than a subtle tint
shift.

NOTE: The original token names (DARK_BG, PANEL_BG, CARD_BG, ACCENT, ACCENT2,
WARN, DANGER, SUCCESS, TEXT_PRIMARY, TEXT_MUTED, BORDER, FONT_TITLE,
FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_MONO) are preserved exactly so
that inventory.py, alerts.py, detector.py, widgets.py, camera.py and gui.py
continue to work unmodified — only their VALUES were upgraded. New tokens
below are additive and used only for the optional glow/hover enhancements.
"""

# ══════════════════════════════════════════════════════════════════════════════
#  THEME — CORE SURFACES  (neutral graphite, not navy — clearer card lift)
# ══════════════════════════════════════════════════════════════════════════════
DARK_BG: str      = "#0A0B10"   # root window background — near-black graphite
PANEL_BG: str     = "#14161D"   # camera panel / alert log surface
CARD_BG: str      = "#1D2029"   # item cards, summary cards — clearly lifted off bg
BORDER: str       = "#2E323F"   # crisp, visible hairline border on cards/panels

# ══════════════════════════════════════════════════════════════════════════════
#  THEME — BRAND / SEMANTIC ACCENTS  (Apple Dark Mode system palette)
# ══════════════════════════════════════════════════════════════════════════════
ACCENT: str       = "#0A84FF"   # primary accent — sapphire blue (was cyan)
ACCENT2: str      = "#BF5AF2"   # secondary accent — vivid purple (was blue-violet)
WARN: str         = "#FF9F0A"   # warning — true orange (was amber)
DANGER: str       = "#FF453A"   # danger — true red (was rose-pink)
SUCCESS: str      = "#30D158"   # success — vivid green (was mint-teal)

# ══════════════════════════════════════════════════════════════════════════════
#  THEME — TEXT HIERARCHY
# ══════════════════════════════════════════════════════════════════════════════
TEXT_PRIMARY: str = "#F5F6FA"   # headings / key values
TEXT_MUTED: str   = "#8E94A6"   # secondary / muted labels

# ══════════════════════════════════════════════════════════════════════════════
#  THEME — EXTENDED TOKENS  (additive — used for glow / hover / depth only)
# ══════════════════════════════════════════════════════════════════════════════
ACCENT3: str      = "#FF375F"   # tertiary accent — system pink (gradients/glow)
CARD_HOVER: str   = "#262A36"   # slightly brighter surface for hover/active
BORDER_SOFT: str  = "#23262F"   # softer hairline for inner dividers
GLOW_CYAN: str    = "#7AB8FF"   # outer glow ring color (blue)
GLOW_PURPLE: str  = "#D9A6FF"   # outer glow ring color (purple)
HOVER: str        = "#1F2330"   # generic hover surface
ACTIVE: str       = "#2A2F3D"   # generic pressed/active surface
DISABLED: str     = "#3A3F4C"   # disabled controls

# ══════════════════════════════════════════════════════════════════════════════
#  TYPOGRAPHY
# ══════════════════════════════════════════════════════════════════════════════
# Premium dashboards (Linear/Stripe/Vercel) pair a clean display sans for
# headings/UI chrome with a monospace face reserved for technical data
# (timestamps, IP/URL fields, numeric entries) — preserved here via
# FONT_MONO so the "IIoT/terminal" character of the dashboard remains.
FONT_TITLE   = ("Segoe UI", 26, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 10)


