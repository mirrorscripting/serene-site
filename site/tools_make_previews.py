# tools_make_previews.py
# Generates six one-page A4 landscape previews (compact layout).
# Output: site/previews/*.pdf

import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------- fonts ----------------
FONT = "DejaVuSans"
FONT_B = "DejaVuSans-Bold"

def _reg(name, paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
            return True
    return False

if not _reg(FONT, [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/local/share/fonts/DejaVuSans.ttf",
    "DejaVuSans.ttf",
]): FONT = "Helvetica"

if not _reg(FONT_B, [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
]): FONT_B = "Helvetica-Bold"

# ---------------- constants ----------------
ZROW = "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓"
STYLE_TITLE = {"core":"Core", "deluxe":"Deluxe", "neon":"Color Pop"}
SEASONS = ["Winter", "Spring", "Summer", "Autumn"]

# palettes (Winter, Spring, Summer, Autumn)
PALETTE = {
    "core": [
        colors.Color(0.75,0.85,1.00),     # winter blue
        colors.Color(1.00,0.85,0.95),     # spring pink
        colors.Color(1.00,0.93,0.70),     # summer gold
        colors.Color(0.45,0.30,0.45),     # autumn plum
    ],
    "deluxe": [
        colors.white,                     # winter white
        colors.Color(0.96,0.80,0.20),     # spring gold
        colors.black,                     # summer black
        colors.Color(0.82,0.84,0.86),     # autumn silver
    ],
    "neon": [
        colors.Color(1.00,0.82,0.12),     # winter yellow
        colors.Color(1.00,0.60,0.85),     # spring pink
        colors.Color(0.10,0.95,0.35),     # summer green
        colors.Color(0.20,0.55,1.00),     # autumn blue
    ],
}

INCLUDES_13 = [
    "Thirteen month calendar with one Year Day",
    "Includes all dates of the twelve month year",
    "Moon daily sign for all three hundred sixty five days",
    "New Moons ○ and Full Moons ●",
    "Sun sign entries",
    "Planet ingresses Mercury to Pluto",
    "Mercury retrograde start and end",
    "Meteor showers peak windows",
]
INCLUDES_12 = [
    "Twelve month calendar",
    "Moon daily sign for all three hundred sixty five days",
    "New Moons ○ and Full Moons ●",
    "Sun sign entries",
    "Planet ingresses Mercury to Pluto",
    "Mercury retrograde start and end",
    "Meteor showers peak windows",
]

# ---------------- drawing helpers ----------------
def chip_shadow(c, x, y, w, h, r=14, opacity=0.10):
    c.saveState()
    c.setFillColor(colors.Color(0,0,0,opacity))
    c.roundRect(x+0.14*cm, y-0.14*cm, w, h, r, fill=1, stroke=0)
    c.restoreState()

def draw_preview(path, cal_type, style):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = canvas.Canvas(path, pagesize=landscape(A4))
    W, H = landscape(A4)

    # background and frame
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    m = 1.4*cm
    c.setStrokeColor(colors.Color(0,0,0,0.10))
    c.setLineWidth(1.8)
    c.roundRect(m, m, W-2*m, H-2*m, 12, stroke=1, fill=0)

    # header (more compact)
    title = f"2026 Calendar · {STYLE_TITLE[style]}"
    c.setFillColor(colors.black)
    c.setFont(FONT_B, 28); c.drawCentredString(W/2, H-2.6*cm, title)
    c.setFont(FONT, 14);   c.drawCentredString(W/2, H-3.7*cm, "Astrological · clean · cute · readable")
    c.setFont(FONT_B, 18); c.drawCentredString(W/2, H-4.8*cm, ZROW)

    # color chips smaller and tighter
    chips = PALETTE[style]
    chip_w, chip_h = 4.4*cm, 4.4*cm   # smaller
    gap = 0.9*cm                      # tighter
    total_w = 4*chip_w + 3*gap
    left_x = (W - total_w)/2
    base_y = H - 10.3*cm              # higher up to save space

    for i, (label, col) in enumerate(zip(SEASONS, chips)):
        x = left_x + i*(chip_w + gap)
        chip_shadow(c, x, base_y, chip_w, chip_h, r=14, opacity=0.10)
        c.setFillColor(col); c.roundRect(x, base_y, chip_w, chip_h, 14, fill=1, stroke=0)
        c.setFillColor(colors.black); c.setFont(FONT_B, 11.5)
        c.drawCentredString(x + chip_w/2, base_y - 0.45*cm, label)

    # content columns sit higher and narrower
    left_col_x = 2.2*cm
    right_col_x = W - 9.0*cm - 2.2*cm
    top_y = base_y - 1.2*cm

    # What's included
    c.setFillColor(colors.black)
    c.setFont(FONT_B, 16); c.drawString(left_col_x, top_y, "What’s included")
    c.setFont(FONT, 11.8)
    y = top_y - 0.9*cm
    items = INCLUDES_13 if cal_type == "13" else INCLUDES_12
    for line in items:
        c.drawString(left_col_x, y, f"• {line}")
        y -= 0.66*cm

    # Details card (smaller)
    card_w, card_h = 9.0*cm, 4.0*cm
    card_x, card_y = right_col_x, top_y - 0.2*cm - card_h
    c.setFillColor(colors.Color(0,0,0,0.04))
    c.roundRect(card_x, card_y, card_w, card_h, 10, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONT_B, 13); c.drawString(card_x+0.8*cm, card_y+card_h-1.2*cm, "Details")
    c.setFont(FONT, 11.8)
    tag = "Thirteen month" if cal_type == "13" else "Twelve month"
    c.drawString(card_x+0.8*cm, card_y+card_h-2.1*cm, f"Edition: {tag}")
    c.drawString(card_x+0.8*cm, card_y+card_h-2.9*cm, "Size: A4 landscape")
    c.drawString(card_x+0.8*cm, card_y+card_h-3.7*cm, "Print friendly and screen friendly")

    # footer copy (no hyphens)
    c.setFillColor(colors.Color(0,0,0,0.70)); c.setFont(FONT, 10.5)
    c.drawCentredString(W/2, 1.95*cm, "Preview page only  full one hundred percent content delivered after purchase.")
    c.setFillColor(colors.black); c.setFont(FONT, 9.5)
    c.drawCentredString(W/2, 1.35*cm, "© 2026 Serene. All rights reserved.")

    c.showPage(); c.save()
    print("Saved:", path)

def main():
    targets = [
        ("13","core","site/previews/13-core-preview.pdf"),
        ("13","deluxe","site/previews/13-deluxe-preview.pdf"),
        ("13","neon","site/previews/13-neon-preview.pdf"),
        ("12","core","site/previews/12-core-preview.pdf"),
        ("12","deluxe","site/previews/12-deluxe-preview.pdf"),
        ("12","neon","site/previews/12-neon-preview.pdf"),
    ]
    for t, s, p in targets:
        draw_preview(p, t, s)

if __name__ == "__main__":
    main()
