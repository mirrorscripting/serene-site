# tools_make_previews.py
# Elegant, centered preview layout — "What’s included" now sits visually under Winter/Spring

import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ----- fonts -----
REG = "DejaVuSans"
BOLD = "DejaVuSans-Bold"
def _reg(name, paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
            return True
    return False
if not _reg(REG, ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","DejaVuSans.ttf"]):
    REG = "Helvetica"
if not _reg(BOLD, ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","DejaVuSans-Bold.ttf"]):
    BOLD = "Helvetica-Bold"

# ----- constants -----
ZROW = "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓"
STYLE_TITLE = {"core": "Core", "deluxe": "Deluxe", "neon": "Color Pop"}
SEASONS = ["Winter", "Spring", "Summer", "Autumn"]

PALETTE = {
    "core": [
        colors.Color(0.75,0.85,1.00),
        colors.Color(1.00,0.85,0.95),
        colors.Color(1.00,0.93,0.70),
        colors.Color(0.45,0.30,0.45),
    ],
    "deluxe": [
        colors.white,
        colors.Color(0.96,0.80,0.20),
        colors.black,
        colors.Color(0.82,0.84,0.86),
    ],
    "neon": [
        colors.Color(1.00,0.82,0.12),
        colors.Color(1.00,0.60,0.85),
        colors.Color(0.10,0.95,0.35),
        colors.Color(0.20,0.55,1.00),
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

# ----- helper -----
def shadow(c, x, y, w, h, r=10, a=0.10):
    c.saveState()
    c.setFillColor(colors.Color(0,0,0,a))
    c.roundRect(x+0.12*cm, y-0.12*cm, w, h, r, fill=1, stroke=0)
    c.restoreState()

def draw_preview(out_path, cal_type, style):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    c = canvas.Canvas(out_path, pagesize=landscape(A4))
    W, H = landscape(A4)

    m = 1.3*cm
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setStrokeColor(colors.Color(0,0,0,0.12)); c.setLineWidth(1.6)
    c.roundRect(m,m,W-2*m,H-2*m,12,fill=0,stroke=1)

    # header
    c.setFillColor(colors.black)
    c.setFont(BOLD, 21)
    c.drawCentredString(W/2, H-2.2*cm, f"2026 Calendar · {STYLE_TITLE[style]}")
    c.setFont(REG, 12)
    c.drawCentredString(W/2, H-3.05*cm, "Astrological · clean · cute · readable")
    c.setFont(BOLD, 14.5)
    c.drawCentredString(W/2, H-3.8*cm, ZROW)

    # color chips
    chips = PALETTE[style]
    chip_w, chip_h = 3.2*cm, 3.2*cm
    gap = 0.65*cm
    total = 4*chip_w + 3*gap
    left = (W - total)/2
    base_y = H - 8.2*cm

    for i, (name, col) in enumerate(zip(SEASONS, chips)):
        x = left + i*(chip_w+gap)
        shadow(c,x,base_y,chip_w,chip_h,10,0.10)
        c.setFillColor(col); c.roundRect(x,base_y,chip_w,chip_h,10,fill=1,stroke=0)
        c.setFillColor(colors.black); c.setFont(BOLD,10.2)
        c.drawCentredString(x+chip_w/2,base_y-0.33*cm,name)

    # realignment: “What’s included” now under Winter/Spring area
    include_x = left - 0.3*cm
    content_top = base_y - 2.1*cm

    c.setFillColor(colors.black)
    c.setFont(BOLD, 13.5)
    c.drawString(include_x, content_top, "What’s included")
    c.setFont(REG, 10.4)
    y = content_top - 0.65*cm
    line_h = 0.50*cm
    items = INCLUDES_13 if cal_type == "13" else INCLUDES_12
    for item in items:
        c.drawString(include_x, y, f"• {item}")
        y -= line_h

    # Details card stays right but lower for balance
    right_w = 7.8*cm
    right_x = W - m - 1.0*cm - right_w
    card_h = 3.8*cm
    card_y = content_top - 0.2*cm - card_h

    c.setFillColor(colors.Color(0,0,0,0.045))
    c.roundRect(right_x,card_y,right_w,card_h,10,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(BOLD,12.2)
    c.drawString(right_x+0.70*cm,card_y+card_h-1.05*cm,"Details")
    c.setFont(REG,10.2)
    tag = "Thirteen month" if cal_type=="13" else "Twelve month"
    c.drawString(right_x+0.70*cm,card_y+card_h-1.85*cm,f"Edition: {tag}")
    c.drawString(right_x+0.70*cm,card_y+card_h-2.55*cm,"Size: A4 landscape")
    c.drawString(right_x+0.70*cm,card_y+card_h-3.25*cm,"Print friendly and screen friendly")

    # footer
    c.setFillColor(colors.Color(0,0,0,0.72)); c.setFont(REG,9.6)
    c.drawCentredString(W/2,m+0.55*cm,"Preview page only  full one hundred percent content delivered after purchase.")
    c.setFillColor(colors.black); c.setFont(REG,9.0)
    c.drawCentredString(W/2,m+0.10*cm,"© 2026 Serene. All rights reserved.")

    c.showPage(); c.save()
    print("Saved:", out_path)

def main():
    targets = [
        ("13","core","site/previews/13-core-preview.pdf"),
        ("13","deluxe","site/previews/13-deluxe-preview.pdf"),
        ("13","neon","site/previews/13-neon-preview.pdf"),
        ("12","core","site/previews/12-core-preview.pdf"),
        ("12","deluxe","site/previews/12-deluxe-preview.pdf"),
        ("12","neon","site/previews/12-neon-preview.pdf"),
    ]
    for t,s,p in targets:
        draw_preview(p,t,s)

if __name__=="__main__":
    main()

