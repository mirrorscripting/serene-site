# build_2026_12mo_full.py
# 12-month 2026 calendar with astro features (Moon-in, phases, eclipses,
# Sun & planet ingresses, solstices/equinoxes, meteor peaks).
# Output: serene-site/downloads/12/core-2026-v1.pdf

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import ephem, math, calendar
from datetime import datetime, timedelta, date
from pathlib import Path

# ---------- paths ----------
SCRIPT_DIR = Path(__file__).resolve().parent
SITE_DIR   = SCRIPT_DIR.parent
OUT_DIR    = SITE_DIR / "downloads" / "12"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = OUT_DIR / "core-2026-v1.pdf"

# ---------- page/layout ----------
W, H = landscape(A4)
MARGIN = 1.0*cm
GAP    = 0.22*cm

FONT = "Helvetica"
BOLD = "Helvetica-Bold"

YEAR = 2026

# seasonal background tints behind each month card (soft)
TINTS = {
    1: colors.HexColor("#e6f0ff"), 2: colors.HexColor("#e6f0ff"), 3: colors.HexColor("#e6f0ff"),  # winter
    4: colors.HexColor("#ffe6f3"), 5: colors.HexColor("#ffe6f3"), 6: colors.HexColor("#ffe6f3"),  # spring
    7: colors.HexColor("#ffefb8"), 8: colors.HexColor("#ffefb8"), 9: colors.HexColor("#ffefb8"),  # summer
    10: colors.HexColor("#ead6f0"),11: colors.HexColor("#ead6f0"),12: colors.HexColor("#ead6f0")  # autumn
}

# ---------- zodiacs ----------
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def sign_from_lon(lon_deg):
    i = int(math.floor((lon_deg % 360.0)/30.0))
    return SIGNS[i]

# ---------- daily Moon-in (noon UTC proxy) ----------
def moon_sign_on(d: date):
    # compute at 12:00 UTC as a stable proxy for "feel of the day"
    t = ephem.Date(datetime(d.year, d.month, d.day, 12, 0, 0))
    m = ephem.Moon(t)
    ecl = ephem.Ecliptic(m)
    lon_deg = float(ecl.lon) * 180.0/math.pi
    return sign_from_lon(lon_deg)

# ---------- planet sign change scan (Sun..Pluto) ----------
PLANET_FUN = {
    "Sun": ephem.Sun,
    "Mercury": ephem.Mercury,
    "Venus": ephem.Venus,
    "Mars": ephem.Mars,
    "Jupiter": ephem.Jupiter,
    "Saturn": ephem.Saturn,
    "Uranus": ephem.Uranus,
    "Neptune": ephem.Neptune,
    "Pluto": ephem.Pluto,
}

def ecliptic_lon_deg(body):
    return float(ephem.Ecliptic(body).lon)*180.0/math.pi

def planet_sign_at(dt_utc, name):
    b = PLANET_FUN[name](ephem.Date(dt_utc))
    return sign_from_lon(ecliptic_lon_deg(b))

def scan_ingresses(year=YEAR):
    # coarse-to-fine: step 6h, detect sign changes; then refine by binary search to hour.
    start = datetime(year,1,1); end = datetime(year,12,31,23,59)
    step = timedelta(hours=6)
    ing = {k: [] for k in PLANET_FUN.keys()}
    for pname in PLANET_FUN.keys():
        t = start
        prev = planet_sign_at(t, pname)
        while t <= end:
            t2 = t + step
            cur = planet_sign_at(t2, pname)
            if cur != prev:
                # refine inside [t, t2]
                lo, hi = t, t2
                for _ in range(24):  # ~hour precision
                    mid = lo + (hi-lo)/2
                    if planet_sign_at(mid, pname) == prev:
                        lo = mid
                    else:
                        hi = mid
                dt = hi  # first moment in new sign
                ing[pname].append( (dt.date(), cur) )
                prev = cur
            t = t2
    return ing

# ---------- fixed 2026 astro dates (from your corrections) ----------
NEW_MOONS = [
    date(2026,1,18), date(2026,3,19), date(2026,6,15), date(2026,8,12),
    date(2026,9,11), date(2026,10,10), date(2026,11,9), date(2026,12,9)
]
FULL_MOONS = [
    date(2026,1,3), date(2026,4,2), date(2026,8,28), date(2026,9,26),
    date(2026,10,26), date(2026,11,24), date(2026,12,24)
]
ECLIPSES = [
    ("Solar eclipse", date(2026,8,12)),
    ("Lunar eclipse", date(2026,8,28)),
]
# Solstices / Equinoxes (calendar markers only; dates approximate & commonly used)
SEASON_TURNS = [
    ("March equinox", date(2026,3,20)),
    ("June solstice", date(2026,6,21)),
    ("September equinox", date(2026,9,22)),
    ("December solstice", date(2026,12,21)),
]
# Meteor peaks (window written on both dates)
METEORS = [
    ("Quadrantids peak window", (date(2026,1,2),  date(2026,1,3))),
    ("Lyrids peak window",      (date(2026,4,21), date(2026,4,22))),
    ("Delta Aquarids peak window",(date(2026,7,28),date(2026,7,29))),
    ("Perseids peak window",    (date(2026,8,12), date(2026,8,13))),
    ("Orionids peak window",    (date(2026,10,21),date(2026,10,22))),
    ("Taurids peak window",     (date(2026,11,4), date(2026,11,5))),
    ("Leonids peak window",     (date(2026,11,17),date(2026,11,18))),
    ("Geminids peak window",    (date(2026,12,13),date(2026,12,14))),
    ("Ursids peak window",      (date(2026,12,21),date(2026,12,22))),
]

# ---------- text helpers ----------
def add_line(c, x, y, w, text, font=FONT, size=8.7, color=colors.black):
    c.setFont(font, size); c.setFillColor(color)
    c.drawString(x, y, text)

def draw_month(c, year, month, ingresses):
    # card size grid (3 columns × 2 rows per page)
    cols, rows = 3, 2
    # (we’ll be called with absolute x,y,w,h)
    pass

# We’ll build each page manually to manage coordinates & spacing robustly
def month_card(c, x, y, w, h, year, month, ingresses):
    # background tint
    c.setFillColor(TINTS[month]); c.roundRect(x, y, w, h, 10, fill=1, stroke=0)
    # heading
    c.setFillColor(colors.black)
    c.setFont(BOLD, 16)
    c.drawString(x+0.5*cm, y+h-0.75*cm, f"{calendar.month_name[month]} {year}")

    # header row (Mon–Sun)
    headers = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    title_h = 1.1*cm
    header_h = 0.8*cm
    grid_top = y + h - title_h
    c.setFont(BOLD, 10)
    cell_w = w/7.0
    for i, wd in enumerate(headers):
        add_line(c, x + i*cell_w + 0.08*cm, grid_top - 0.2*cm, wd, BOLD, 10)

    # grid lines
    rows = 6
    cell_h = (h - title_h - header_h)/rows
    y0 = grid_top - header_h + 0.05*cm
    c.setStrokeColor(colors.Color(0,0,0, alpha=0.12))
    for r in range(rows+1):
        c.line(x, y0 - r*cell_h, x+w, y0 - r*cell_h)
    for col in range(8):
        c.line(x + col*cell_w, y0, x + col*cell_w, y0 - rows*cell_h)
    c.setStrokeColor(colors.black)

    # days matrix
    cal = calendar.Calendar(firstweekday=0)  # Monday-first
    matrix = cal.monthdatescalendar(year, month)

    # pre-build event dict for this month (only what we show in-grid)
    daily_events = {}
    def push(d, s):
        daily_events.setdefault(d, []).append(s)

    # Moon-in daily
    for week in matrix:
        for d in week:
            if d.month == month:
                push(d, f"Moon in {moon_sign_on(d)}")

    # Phases (grid shows only words "New Moon" / "Full Moon")
    for d in NEW_MOONS:
        if d.month == month: push(d, "New Moon")
    for d in FULL_MOONS:
        if d.month == month: push(d, "Full Moon")

    # Eclipses (on the correct day only)
    for name, d in ECLIPSES:
        if d.month == month: push(d, name)

    # Solstices/Equinoxes
    for name, d in SEASON_TURNS:
        if d.month == month: push(d, name)

    # Meteor windows (write on both dates)
    for name, (d1, d2) in METEORS:
        if d1.month == month: push(d1, name)
        if d2.month == month: push(d2, name)

    # Sun & planet ingresses (computed)
    for planet, items in ingresses.items():
        for d_local, sign in items:
            if d_local.year==year and d_local.month==month:
                arrow = "Sun →" if planet=="Sun" else f"{planet} →"
                push(d_local, f"{arrow} {sign}")

    # draw each cell
    for r in range(rows):
        if r >= len(matrix): break
        week = matrix[r]
        for col in range(7):
            try: d = week[col]
            except IndexError: continue
            cx = x + col*cell_w
            top = y0 - r*cell_h
            # day number top-right
            c.setFont(BOLD, 10)
            if d.month == month:
                c.setFillColor(colors.black)
            else:
                c.setFillColor(colors.Color(0,0,0, alpha=0.28))
            c.drawRightString(cx + cell_w - 0.08*cm, top - 0.22*cm, str(d.day))
            c.setFillColor(colors.black)

            # stacked text: start at a mid-anchor to avoid colliding with the number
            line_y = top - 0.45*cm
            line_h = 0.36*cm  # spacing
            max_lines = int((cell_h - 0.28*cm)/line_h) - 1
            lines = [s for s in daily_events.get(d, [])]
            # special case: Aug 27 should NOT say Full/Lunar eclipse per your note
            if d == date(2026,8,27):
                lines = [s for s in lines if ("Full Moon" not in s and "Lunar eclipse" not in s)]
            # render with overflow ellipsis
            shown = 0
            for s in lines:
                if shown >= max_lines:
                    add_line(c, cx+0.08*cm, line_y, cell_w-0.16*cm, "…", FONT, 9)
                    break
                add_line(c, cx+0.08*cm, line_y, cell_w-0.16*cm, s, FONT, 9)
                shown += 1
                line_y -= line_h

def render_months(c, ingresses):
    # 3×2 months per page → 2 pages total
    cols, rows = 3, 2
    grid_w = W - 2*MARGIN
    grid_h = H - 2*MARGIN
    cell_w = (grid_w - (cols-1)*GAP)/cols
    cell_h = (grid_h - (rows-1)*GAP)/rows

    months = list(range(1,13))
    for page in range(2):
        c.setFillColor(colors.white); c.rect(0,0,W,H, fill=1, stroke=0)
        c.setFont(BOLD, 18); c.setFillColor(colors.black)
        c.drawCentredString(W/2, H-0.9*cm, f"Serene · 12-Month Calendar — {YEAR}")
        block = months[page*6:(page+1)*6]
        for i, m in enumerate(block):
            r = i//cols; col=i%cols
            x = MARGIN + col*(cell_w+GAP)
            y = H - MARGIN - (r+1)*cell_h - r*GAP
            month_card(c, x, y, cell_w, cell_h, YEAR, m, ingresses)
        c.setFont(FONT,9)
        c.drawCentredString(W/2, 0.7*cm, "A4 landscape · print-friendly · © 2026 Serene")
        c.showPage()

# ---------- Info / Reference pages ----------
def info_page(c):
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFont(BOLD, 22); c.setFillColor(colors.black)
    c.drawCentredString(W/2, H-2.0*cm, "Information")
    c.setFont(FONT, 12)
    y = H-3.0*cm
    lines = [
        "Moon phases shown as words in-grid: “New Moon”, “Full Moon”.",
        "Daily “Moon in <Sign>” computed at local-noon proxy for a clean daily feel; not a minute-exact ephemeris.",
        "Sun and planet ingresses (Mercury → Pluto) are included on the calendar date.",
        "Solstices, equinoxes, and major meteor shower peak windows are included.",
        "Source cross-check: mooncalendar.astro-seek.com · All rights reserved.",
    ]
    for t in lines:
        c.drawString(2.0*cm, y, "• " + t); y -= 0.9*cm
    c.showPage()

def zodiac_and_fullmoons_page(c):
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    # layout: Full Moons (left), Zodiac keywords (bottom left), Sun Enters (right column)
    left_x = 2.0*cm; mid_x = W/2 + 0.5*cm; top_y = H - 2.0*cm
    c.setFont(BOLD, 18); c.setFillColor(colors.black)
    c.drawString(left_x, top_y, "Full Moons · 2026")
    c.setFont(FONT, 12)
    y = top_y - 0.9*cm
    # Full Moons list (dates only; the grid itself has no sign words for phases)
    fml = [
        ("Jan 03", "Full Moon"),
        ("Apr 02", "Full Moon"),
        ("Aug 28", "Full Moon · Lunar eclipse"),
        ("Sep 26", "Full Moon"),
        ("Oct 26", "Full Moon"),
        ("Nov 24", "Full Moon"),
        ("Dec 24", "Full Moon"),
    ]
    for d, label in fml:
        c.drawString(left_x, y, f"{d}: {label}"); y -= 0.7*cm

    # Sun enters signs (right column)
    c.setFont(BOLD, 18)
    c.drawString(mid_x, top_y, "Sun Enters Signs · 2026")
    c.setFont(FONT, 12)
    y2 = top_y - 0.9*cm

    # Compute Sun ingresses from our scan (to avoid hardcoding)
    sun_list = []
    # we’ll re-scan quickly just for Sun for reliability
    ing = scan_ingresses(YEAR)
    for d, s in ing["Sun"]:
        sun_list.append( (d, s) )
    sun_list.sort(key=lambda x: x[0])

    for d, s in sun_list:
        c.drawString(mid_x, y2, f"{d.strftime('%b %d')}: Sun → {s}")
        y2 -= 0.7*cm

    # Zodiac keywords (bottom)
    c.setFont(BOLD, 18)
    c.drawString(left_x, H/2 - 0.4*cm, "Zodiac")
    c.setFont(FONT, 12)
    y3 = H/2 - 1.2*cm
    kw = {
        "Aries":"initiate, bold, spark",
        "Taurus":"grounded, sensual, steady",
        "Gemini":"curious, airy, quick",
        "Cancer":"nurturing, intuitive, protective",
        "Leo":"radiant, creative, proud",
        "Virgo":"precise, service, refine",
        "Libra":"harmonize, relate, balance",
        "Scorpio":"deep, transformative, magnetic",
        "Sagittarius":"expansive, adventurous, candid",
        "Capricorn":"ambitious, disciplined, builder",
        "Aquarius":"innovative, future-minded, unique",
        "Pisces":"dreamy, compassionate, mystical",
    }
    colgap = 7.0*cm
    col2_x = left_x + colgap
    col3_x = left_x + 2*colgap
    i = 0
    for s in SIGNS:
        text = f"{s}: {kw[s]}"
        xcol = [left_x, col2_x, col3_x][i%3]
        c.drawString(xcol, y3 - 0.9*cm*(i//3), text)
        i += 1

    c.showPage()

# ---------- build ----------
def build():
    print("Scanning ingresses (Sun + planets)…")
    ing = scan_ingresses(YEAR)

    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(A4))
    render_months(c, ing)
    info_page(c)
    zodiac_and_fullmoons_page(c)
    c.save()
    print("Saved:", PDF_PATH)

if __name__ == "__main__":
    build()
