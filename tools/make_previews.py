# tools/make_previews.py
# One-page A4 landscape previews for Core / Deluxe / Color-Pop (Neon)
# Outputs → site/previews/{core,deluxe,neon}-preview.pdf

import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# fonts
REG="DejaVuSans"; BLD="DejaVuSans-Bold"
def reg(name, paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name,p)); return True
    return False
if not reg(REG, ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","DejaVuSans.ttf"]): REG="Helvetica"
if not reg(BLD, ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","DejaVuSans-Bold.ttf"]): BLD="Helvetica-Bold"

W,H = landscape(A4)

PALETTE = {
    "core":   [colors.Color(0.75,0.85,1.00), colors.Color(1.00,0.85,0.95), colors.Color(1.00,0.93,0.70), colors.Color(0.45,0.30,0.45)],
    "deluxe": [colors.white, colors.Color(0.96,0.80,0.20), colors.black, colors.Color(0.82,0.84,0.86)],
    "neon":   [colors.Color(1.00,0.82,0.12), colors.Color(1.00,0.60,0.85), colors.Color(0.10,0.95,0.35), colors.Color(0.20,0.55,1.00)],
}
LABEL  = {"core":"Core", "deluxe":"Deluxe", "neon":"Color-Pop (Neon)"}
SEASONS = ["Winter","Spring","Summer","Autumn"]
ZROW = "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓"

FEATURES = [
  "13-month calendar (includes all dates of the 12-month year) + one Year Day",
  "New Moons ○ & Full Moons ●",
  "Sun → sign entries",
  "Planet ingresses (Mercury → Pluto)",
  "Mercury retrograde: start/end",
  "Meteor showers: peak windows",
]

def draw_preview(path, kind):
    c = canvas.Canvas(path, pagesize=landscape(A4))
    # page bg
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)

    # title
    c.setFillColor(colors.black)
    c.setFont(BLD, 26)
    c.drawCentredString(W/2, H-2.8*cm, f"2026 Calendar · {LABEL[kind]}")
    c.setFont(REG, 13)
    c.drawCentredString(W/2, H-3.9*cm, "Astrological • clean • cute • readable")

    # zodiac ribbon
    c.setFont(BLD, 18)
    c.drawCentredString(W/2, H-5.0*cm, ZROW)

    # four season blocks (palette)
    x0 = 2.4*cm; gap = 0.7*cm
    boxW = (W-2*x0-3*gap)/4; boxH = 5.6*cm
    y0 = H/2 - boxH/2 + 0.6*cm
    cols = PALETTE[kind]
    for i,col in enumerate(cols):
        x = x0 + i*(boxW+gap)
        c.setFillColor(col); c.roundRect(x,y0,boxW,boxH,10,fill=1,stroke=0)
        # label text color
        tc = colors.white if col==colors.black else colors.black
        c.setFillColor(tc); c.setFont(BLD,12)
        c.drawCentredString(x+boxW/2, y0+boxH/2-6, SEASONS[i])

    # features list
    left = 2.4*cm; y = y0-0.9*cm
    c.setFillColor(colors.black)
    c.setFont(BLD,14); c.drawString(left, y, "What’s included"); y -= 0.6*cm
    c.setFont(REG,12)
    for f in FEATURES:
        c.drawString(left+0.3*cm, y, f); y -= 0.52*cm

    # footer
    c.setFont(REG,10)
    c.drawCentredString(W/2, 1.5*cm, "Preview page only — full 100% content delivered after purchase.")
    c.showPage(); c.save()

    print("Saved:", path)

if __name__ == "__main__":
    os.makedirs("site/previews", exist_ok=True)
    for k in ["core","deluxe","neon"]:
        draw_preview(f"site/previews/{k}-preview.pdf", k)
