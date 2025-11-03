# make_ingresses_page_2026.py
# Planet Ingresses · 2026 (dates only)
# Single-page PDF laid out in THREE COLUMNS so everything fits on one page.

import os
import datetime as dt
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------- fonts ----------
FONT_REG = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
def _try_font(name, paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
            return True
    return False

if not _try_font(FONT_REG, [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/local/share/fonts/DejaVuSans.ttf",
    "DejaVuSans.ttf",
]):
    FONT_REG = "Helvetica"

if not _try_font(FONT_BOLD, [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
]):
    FONT_BOLD = "Helvetica-Bold"

# ---------- glyphs ----------
Z = {
    "Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋",
    "Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏",
    "Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓",
}

# ---------- ingress data (DATES ONLY, 2026) ----------
INGRESSES = {
    # Inner / Action
    "Mercury":[
        ("Jan 01","Capricorn"), ("Jan 20","Aquarius"), ("Feb 06","Pisces"),
        ("Apr 15","Aries"), ("May 03","Taurus"), ("May 17","Gemini"),
        ("Jun 01","Cancer"), ("Aug 09","Leo"), ("Aug 25","Virgo"),
        ("Sep 10","Libra"), ("Sep 30","Scorpio"), ("Dec 06","Sagittarius"),
        ("Dec 25","Capricorn"),
    ],
    "Venus":[
        ("Jan 17","Aquarius"), ("Feb 10","Pisces"), ("Mar 06","Aries"),
        ("Mar 30","Taurus"), ("Apr 24","Gemini"), ("May 19","Cancer"),
        ("Jul 09","Leo"), ("Aug 06","Libra"), ("Sep 10","Scorpio"),
        # leaves on retro Oct 25 (R), then re-enters:
        ("Dec 04","Scorpio"),
    ],
    "Mars":[
        ("Jan 23","Aquarius"), ("Mar 02","Pisces"), ("Apr 09","Aries"),
        ("May 18","Taurus"), ("Jun 28","Gemini"), ("Aug 11","Cancer"),
        ("Sep 28","Leo"), ("Nov 25","Virgo"),
    ],
    "Jupiter":[ ("Jun 30","Leo") ],

    # Outer
    "Saturn":[ ("Feb 14","Aries") ],
    "Uranus":[ ("Apr 26","Gemini") ],
    "Neptune":[ ("Jan 26","Aries") ],
    "Pluto":[ ],  # no sign change in 2026
}

# Which planets go in which column (3 columns)
COLS = [
    ["Mercury", "Venus"],
    ["Mars", "Jupiter"],
    ["Saturn", "Uranus", "Neptune", "Pluto"],
]

def draw_planet_block(c, x, y_top, planet, line_gap, item_size, head_size):
    """Draw one planet header + its lines. Return new y after block."""
    c.setFont(FONT_BOLD, head_size)
    c.setFillColor(colors.black)
    c.drawString(x, y_top, planet)
    y = y_top - (line_gap + 2)  # small gap after header

    rows = INGRESSES.get(planet, [])
    c.setFont(FONT_REG, item_size)
    if not rows:
        c.drawString(x, y, "—")
        return y - (line_gap + 4)

    for (d, sign) in rows:
        c.drawString(x, y, f"{d} → {sign} {Z[sign]}")
        y -= line_gap
    return y - (line_gap // 2)

def build_pdf(out_path="out/ingresses_2026.pdf"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    c = canvas.Canvas(out_path, pagesize=landscape(A4))
    W, H = landscape(A4)

    # page background
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=True, stroke=False)

    # title
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD, 28)
    c.drawCentredString(W/2, H - 40, "Planet Ingresses · 2026 (dates only)")

    # three-column layout
    margin_l = 36
    margin_r = 36
    margin_t = 72
    margin_b = 36

    usable_w = W - margin_l - margin_r
    col_w = usable_w / 3.0
    x_positions = [margin_l + i * col_w for i in range(3)]

    # column headings
    heads = ["Inner / Action", "Inner / Action", "Outer Planets"]
    c.setFont(FONT_BOLD, 12)
    for i, head in enumerate(heads):
        c.drawString(x_positions[i], H - margin_t, head)

    # start y for blocks
    y_start = H - margin_t - 18

    # typography
    head_size = 12
    item_size = 10.5
    line_gap  = 14

    # draw columns
    for col_idx, planets in enumerate(COLS):
        x = x_positions[col_idx]
        y = y_start
        for p in planets:
            y = draw_planet_block(c, x, y, p, line_gap, item_size, head_size)

    c.showPage()
    c.save()
    return out_path

if __name__ == "__main__":
    path = build_pdf()
    print(f"Saved: {os.path.abspath(path)}")
