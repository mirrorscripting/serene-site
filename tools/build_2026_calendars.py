# build_2026_calendars.py
# Generates 12-month 2026 calendar PDFs (Core, Deluxe, Color-Pop) into:
#   serene-site/downloads/12/core-2026-v1.pdf
#   serene-site/downloads/12/deluxe-2026-v1.pdf
#   serene-site/downloads/12/color-2026-v1.pdf
#
# This version anchors output paths to THIS FILE’s folder, so you can run it
# from anywhere and it will still write into your site’s downloads/12/.

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
import calendar
from datetime import date
from pathlib import Path

# ----- Paths anchored to script location -----
SCRIPT_DIR = Path(__file__).resolve().parent
SITE_DIR = SCRIPT_DIR.parent
OUT_DIR = SITE_DIR / "downloads" / "12"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = landscape(A4)
MARGIN = 1.2 * cm
GAP = 0.25 * cm
FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

YEAR = 2026

MONTH_NAMES = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

# Seasonal palettes
CORE_TINTS = {
    "winter": colors.HexColor("#e6f0ff"),
    "spring": colors.HexColor("#ffe6f3"),
    "summer": colors.HexColor("#ffefb8"),
    "autumn": colors.HexColor("#ead6f0"),
}
DELUXE_ACCENT = colors.HexColor("#c9a227")  # gold
COLORPOP = {
    1:"#ff2bd1", 2:"#21e6ff", 3:"#f9ff21",
    4:"#7cff5b", 5:"#ff7a00", 6:"#9b59ff",
    7:"#00d1a0", 8:"#ff006e", 9:"#00c2ff",
    10:"#ffd166", 11:"#ef476f", 12:"#06d6a0"
}

def season(m):
    if m in (1,2,3): return "winter"
    if m in (4,5,6): return "spring"
    if m in (7,8,9): return "summer"
    return "autumn"

def month_grid(c, x, y, w, h, year, month, style="core"):
    """Draw one month at x,y with size w×h."""
    title_h = 1.1 * cm
    header_h = 0.8 * cm
    rows, cols = 6, 7
    grid_h = h - title_h
    cell_h = (grid_h - header_h) / rows
    cell_w = w / cols

    # Card backgrounds
    if style == "core":
        tint = CORE_TINTS[season(month)]
        c.setFillColor(tint); c.setStrokeColor(tint)
        c.roundRect(x, y, w, h, 10, fill=1, stroke=0)
        c.setFillColor(colors.black)
    elif style == "deluxe":
        c.setFillColor(colors.white)
        c.roundRect(x, y, w, h, 10, fill=1, stroke=0)
    else:  # color
        c.setFillColor(colors.white)
        c.roundRect(x, y, w, h, 10, fill=1, stroke=0)
        c.setFillColor(colors.HexColor(COLORPOP[month]))
        c.roundRect(x, y+h-title_h, w, title_h, 10, fill=1, stroke=0)
        c.setFillColor(colors.black)

    # Month title
    c.setFont(FONT_BOLD, 16)
    title_y = y + h - 0.75*cm
    c.setFillColor(colors.black)
    c.drawString(x + 0.5*cm, title_y, f"{MONTH_NAMES[month-1]} {year}")
    if style == "deluxe":
        c.setStrokeColor(DELUXE_ACCENT); c.setLineWidth(2)
        c.line(x + 0.5*cm, title_y - 0.25*cm, x + w - 0.5*cm, title_y - 0.25*cm)
        c.setStrokeColor(colors.black); c.setLineWidth(1)

    # Weekday header (Mon–Sun)
    c.setFont(FONT_BOLD, 10)
    headers = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    header_y = y + h - title_h - 0.2*cm
    for i,wd in enumerate(headers):
        tx = x + i*cell_w + 0.08*cm
        c.drawString(tx, header_y, wd)

    # Grid lines (light)
    c.setStrokeColor(colors.Color(0,0,0, alpha=0.12))
    gy = header_y - 0.15*cm
    for r in range(rows+1):
        c.line(x, gy - r*cell_h, x+w, gy - r*cell_h)
    for col in range(cols+1):
        c.line(x + col*cell_w, gy, x + col*cell_w, gy - rows*cell_h)
    c.setStrokeColor(colors.black)

    # Compute month days
    cal = calendar.Calendar(firstweekday=0)  # Monday start
    month_days = cal.monthdatescalendar(year, month)

    # Day numbers (top-right)
    c.setFont(FONT_BOLD, 10)
    for r in range(rows):
        for col in range(cols):
            d = month_days[r][col] if r < len(month_days) and col < len(month_days[r]) else None
            if not d: continue
            cell_x = x + col*cell_w
            cell_top = gy - r*cell_h
            if d.month == month:
                c.setFillColor(colors.black)
            else:
                c.setFillColor(colors.Color(0,0,0, alpha=0.28))
            c.drawRightString(cell_x + cell_w - 0.08*cm, cell_top - 0.22*cm, str(d.day))
    c.setFillColor(colors.black)

def draw_footer(c, text):
    c.setFont(FONT, 9)
    c.setFillColor(colors.black)
    c.drawCentredString(W/2, 0.7*cm, text)

def page_layout(c, year, style="core"):
    cols, rows = 3, 2          # 6 months per page
    grid_w = W - 2*MARGIN
    grid_h = H - 2*MARGIN
    cell_w = (grid_w - (cols-1)*GAP) / cols
    cell_h = (grid_h - (rows-1)*GAP) / rows

    months = list(range(1,13))
    for page in range(2):
        c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFont(FONT_BOLD, 18)
        title = f"Serene · 12-Month Calendar — {year}"
        if style == "deluxe":
            c.setFillColor(DELUXE_ACCENT)
            c.drawCentredString(W/2, H - 0.9*cm, title)
            c.setFillColor(colors.black)
        else:
            c.drawCentredString(W/2, H - 0.9*cm, title)

        block = months[page*6:(page+1)*6]
        for idx, m in enumerate(block):
            r = idx // cols
            col = idx % cols
            x = MARGIN + col * (cell_w + GAP)
            y = H - MARGIN - (r+1)*cell_h - r*GAP - 0.4*cm
            month_grid(c, x, y, cell_w, cell_h, year, m, style=style)

        draw_footer(c, "A4 landscape · print-friendly · © 2026 Serene")
        c.showPage()

def build_all():
    files = {
        "core":   OUT_DIR / "core-2026-v1.pdf",
        "deluxe": OUT_DIR / "deluxe-2026-v1.pdf",
        "color":  OUT_DIR / "color-2026-v1.pdf",
    }
    for style, path in files.items():
        c = canvas.Canvas(str(path), pagesize=landscape(A4))
        page_layout(c, YEAR, style=style)
        c.save()
        print("Saved:", path)

if __name__ == "__main__":
    build_all()
