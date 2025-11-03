# tools/make_previews.py
# Build single-page A4 landscape preview PDFs for the 3 styles.
# Output: site/previews/{core,deluxe,neon}-preview.pdf

import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Fonts
FONT = "DejaVuSans"; FONTB = "DejaVuSans-Bold"
def reg(name, paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
            return True
    return False
if not reg(FONT,  ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","DejaVuSans.ttf"]): FONT="Helvetica"
if not reg(FONTB, ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","DejaVuSans-Bold.ttf"]): FONTB="Helvetica-Bold"

W,H = landscape(A4)

# palettes (match your calendar)
PALETTE = {
    "core":   [colors.Color(0.75,0.85,1.00), colors.Color(1.00,0.85,0.95), colors.Color(1.00,0.93,0.70), colors.Color(0.45,0.30,0.45)],
    "deluxe": [colors.white, colors.Color(0.96,0.80,0.20), colors.black, colors.Color(0.82,0.84,0.86)],
    "neon":   [colors.Color(1.00,0.82,0.12), colors.Color(1.00,0.60,0.85), colors.Color(0.10,0.95,0.35), colors.Color(0.20,0.55,1.00)],
}
LABEL  = {"core":"Core (Seasonal)","deluxe":"Deluxe (White • Gold • Black • Silver)","neon":"Color Pop (Neon)"}

def paint_preview(path, kind):
    c = canvas.Canvas(path, pagesize=landscape(A4))
    # white page
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)

    # Title
    c.setFillColor(colors.black)
    c.setFont(FONTB, 28)
    c.drawCentredString(W/2, H-3.0*cm, f"2026 Calendar · {LABEL[kind]}")
    c.setFont(FONT, 14)
    c.drawCentredString(W/2, H-4.3*cm, "Single-page preview (sample)")

    # Four color blocks = Winter/Spring/Summer/Autumn
    x0 = 3*cm; gap = 0.8*cm; boxW = (W-2*x0-3*gap)/4; boxH = 6.0*cm
    y0 = H/2 - boxH/2 + 0.4*cm
    seasons = ["Winter","Spring","Summer","Autumn"]
    for i, col in enumerate(PALETTE[kind]):
        x = x0 + i*(boxW+gap)
        c.setFillColor(col); c.roundRect(x, y0, boxW, boxH, 10, fill=1, stroke=0)
        c.setFillColor(colors.black if col != colors.black else colors.white)
        c.setFont(FONTB, 13)
        c.drawCentredString(x+boxW/2, y0+boxH/2-6, seasons[i])

    # Footer note
    c.setFillColor(colors.black)
    c.setFont(FONT, 11)
    c.drawCentredString(W/2, 1.65*cm, "© 2026 Serene • This is a preview. Full calendar delivers after purchase.")
    c.showPage(); c.save()
    print("Saved:", path)

if __name__ == "__main__":
    os.makedirs("site/previews", exist_ok=True)
    for k in ["core","deluxe","neon"]:
        paint_preview(f"site/previews/{k}-preview.pdf", k)
