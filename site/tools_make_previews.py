# tools_make_previews.py
# One-page PREVIEW PDFs (white). Hearts as bullets, grey "Details" box
# sized only as needed, with the "Details" heading above the box.

import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT_DIR = "site/previews"

# -------- fonts --------
FONT = "DejaVuSans"
for p in (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/local/share/fonts/DejaVuSans.ttf",
    "DejaVuSans.ttf",
):
    if os.path.exists(p):
        pdfmetrics.registerFont(TTFont(FONT, p))
        break
else:
    FONT = "Helvetica"

# -------- theme data --------
ZODIAC_ROW = "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓"
HEART = "♥"

CORE   = [colors.Color(0.75,0.85,1.00), colors.Color(1.00,0.85,0.95),
          colors.Color(1.00,0.93,0.70), colors.Color(0.45,0.30,0.45)]
DELUXE = [colors.white, colors.Color(0.96,0.80,0.20),
          colors.black, colors.Color(0.82,0.84,0.86)]
NEON   = [colors.Color(1.00,0.82,0.12), colors.Color(1.00,0.60,0.85),
          colors.Color(0.10,0.95,0.35), colors.Color(0.20,0.55,1.00)]

# -------- drawing helpers --------
def draw_title_block(c, W, top_y, heading):
    c.setFillColor(colors.black)
    c.setFont(FONT, 22)
    c.drawCentredString(W/2, top_y, heading)
    c.setFont(FONT, 11.5)
    c.drawCentredString(W/2, top_y - 0.9*cm, "All colors are included")
    c.setFont(FONT, 14)
    c.drawCentredString(W/2, top_y - 1.8*cm, ZODIAC_ROW)

def quad_swatch(c, x, y, size, cols):
    r = 14
    c.setLineWidth(1.2)
    c.setStrokeColor(colors.Color(0,0,0,0.15))
    c.roundRect(x, y, size, size, r, stroke=True, fill=False)

    half = size/2.0
    # 4 color quadrants
    c.setFillColor(cols[0]); c.roundRect(x,            y+half, half+0.4, half+0.4, r, stroke=False, fill=True)
    c.setFillColor(cols[1]); c.roundRect(x+half-0.4,   y+half, half+0.4, half+0.4, r, stroke=False, fill=True)
    c.setFillColor(cols[2]); c.roundRect(x,            y,      half+0.4, half+0.4, r, stroke=False, fill=True)
    c.setFillColor(cols[3]); c.roundRect(x+half-0.4,   y,      half+0.4, half+0.4, r, stroke=False, fill=True)

def palette_tile(c, x_center, y_bottom, label, cols):
    tile_size = 3.6*cm
    x = x_center - tile_size/2.0
    y = y_bottom
    quad_swatch(c, x, y, tile_size, cols)
    c.setFillColor(colors.black); c.setFont(FONT, 12.5)
    c.drawCentredString(x_center, y - 0.5*cm, label)

def bullets(kind):
    heart = HEART
    if kind == "13":
        whats = [
            f"{heart} Thirteen month calendar with one Year Day",
            f"{heart} Includes all dates of the twelve month year",
            f"{heart} Moon daily sign for all three hundred sixty five days",
            f"{heart} New Moons ○ and Full Moons ●",
            f"{heart} Sun sign entries",
            f"{heart} Planet ingresses Mercury to Pluto",
            f"{heart} Mercury retrograde start and end",
            f"{heart} Meteor showers peak windows",
            f"{heart} Information page with explanations",
            f"{heart} Own ingress page",
        ]
        details = ["Edition: Thirteen month", "Size: A4 landscape", "Print friendly and screen friendly"]
    else:
        whats = [
            f"{heart} Twelve month calendar",
            f"{heart} Moon daily sign for all three hundred sixty five days",
            f"{heart} New Moons ○ and Full Moons ●",
            f"{heart} Sun sign entries",
            f"{heart} Planet ingresses Mercury to Pluto",
            f"{heart} Mercury retrograde start and end",
            f"{heart} Meteor showers peak windows",
            f"{heart} Information page with explanations",
            f"{heart} Own ingress page",
        ]
        details = ["Edition: Twelve month", "Size: A4 landscape", "Print friendly and screen friendly"]
    return whats, details

def draw_text_block(c, left_x, right_x, top_y, whats, details):
    # top divider
    c.setStrokeColor(colors.Color(0,0,0,0.10)); c.setLineWidth(1)
    c.line(left_x, top_y, right_x, top_y)

    lh   = 0.58*cm
    size = 11
    col_gap = 1.2*cm
    col_w   = (right_x - left_x - col_gap)/2.0
    L = left_x
    R = left_x + col_w + col_gap

    # left heading + list
    c.setFillColor(colors.black); c.setFont(FONT, 13)
    c.drawString(L, top_y - 0.8*cm, "What’s included")
    yL = top_y - 1.6*cm
    c.setFont(FONT, size)
    for line in whats:
        c.drawString(L, yL, line); yL -= lh

    # Right column — smaller grey box sized to content, title above the box
    c.setFillColor(colors.black); c.setFont(FONT, 13)
    title_y = top_y - 0.8*cm
    c.drawString(R, title_y, "Details")

    # measure details height
    lines_h = len(details) * lh
    pad_y = 0.6*cm   # slimmer box
    pad_x = 0.5*cm
    # width: fit longest line (approx) but clamp to a max
    max_chars = max(len(s) for s in details) if details else 0
    approx_char_w = 0.21 * cm   # rough width of one glyph at 11pt
    box_w = min(col_w, max(7.0*cm, max_chars * approx_char_w) + 2*pad_x)

    box_top = title_y - 0.35*cm
    total_h = lines_h + 2*pad_y
    box_bottom = box_top - total_h

    c.setFillColor(colors.Color(0.95,0.96,0.98))
    c.setStrokeColor(colors.Color(0,0,0,0.10)); c.setLineWidth(1.2)
    c.roundRect(R - pad_x, box_bottom, box_w, total_h, 10, stroke=True, fill=True)

    # vertically center the detail lines inside the box
    text_start = box_bottom + (total_h - lines_h)/2 + (lh * (len(details)-1))
    c.setFillColor(colors.black); c.setFont(FONT, size)
    for i, line in enumerate(details):
        y = text_start - i * lh
        c.drawString(R, y, line)

def build_preview(kind, out_path, heading):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    c = canvas.Canvas(out_path, pagesize=landscape(A4))
    W, H = landscape(A4)

    # background
    c.setFillColor(colors.white); c.rect(0, 0, W, H, fill=True, stroke=False)

    # title + zodiac
    top = H - 1.8*cm
    draw_title_block(c, W, top, heading)

    # three palette tiles
    row_y = H - 8.2*cm
    x1, x2, x3 = W/2 - 8.0*cm, W/2, W/2 + 8.0*cm
    palette_tile(c, x1, row_y, "Core seasonal", CORE)
    palette_tile(c, x2, row_y, "Deluxe", DELUXE)
    palette_tile(c, x3, row_y, "Color Pop", NEON)

    # content rows
    left_x, right_x = 2.2*cm, W - 2.2*cm
    whats, details = bullets(kind)
    draw_text_block(c, left_x, right_x, row_y - 1.2*cm, whats, details)

    # footer
    c.setFillColor(colors.Color(0,0,0,0.60)); c.setFont(FONT, 9.6)
    c.drawCentredString(W/2, 1.35*cm, f"Preview page only {HEART} full content delivered after purchase.")
    c.setFillColor(colors.Color(0,0,0,0.75))
    c.drawCentredString(W/2, 0.95*cm, "© 2026 Serene. All rights reserved.")

    c.showPage(); c.save()
    print(f"Saved: {os.path.abspath(out_path)}")

def main():
    build_preview("13", os.path.join(OUT_DIR, "13-bundle-preview.pdf"),
                  "Thirteen Month Calendar Preview")
    build_preview("12", os.path.join(OUT_DIR, "12-bundle-preview.pdf"),
                  "Twelve Month Calendar Preview")

if __name__ == "__main__":
    main()
