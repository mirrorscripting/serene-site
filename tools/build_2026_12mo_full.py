# build_2026_12mo_full.py
# 12-month 2026 calendar with full astro features, one month per page,
# plus Information and Full Moons · Zodiac · Sun Enters Signs page.
# Output: serene-site/downloads/12/core-2026-v1.pdf

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
import ephem, math, calendar
from datetime import datetime, timedelta, date
from pathlib import Path

# ----- Paths anchored to this script -----
SCRIPT_DIR = Path(__file__).resolve().parent
SITE_DIR   = SCRIPT_DIR.parent
OUT_DIR    = SITE_DIR / "downloads" / "12"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = OUT_DIR / "core-2026-v1.pdf"

# ----- Page/Layout -----
W, H = landscape(A4)
MARGIN = 1.2 * cm
FONT = "Helvetica"
BOLD = "Helvetica-Bold"

YEAR = 2026

# Seasonal tints (soft)
TINTS = {
    1:"#e6f0ff", 2:"#e6f0ff", 3:"#e6f0ff",  # winter
    4:"#ffe6f3", 5:"#ffe6f3", 6:"#ffe6f3",  # spring
    7:"#ffefb8", 8:"#ffefb8", 9:"#ffefb8",  # summer
    10:"#ead6f0", 11:"#ead6f0", 12:"#ead6f0" # autumn
}

# ----- Zodiacs -----
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def sign_from_lon(lon_deg):
    i = int(math.floor((lon_deg % 360.0)/30.0))
    return SIGNS[i]

def moon_sign_on(d: date):
    t = ephem.Date(datetime(d.year, d.month, d.day, 12, 0, 0))  # noon UTC proxy
    m = ephem.Moon(t)
    lon_deg = float(ephem.Ecliptic(m).lon) * 180.0/math.pi
    return sign_from_lon(lon_deg)

PLANETS = {
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

def planet_sign_at(dt_utc, name):
    body = PLANETS[name](ephem.Date(dt_utc))
    lon_deg = float(ephem.Ecliptic(body).lon)*180.0/math.pi
    return sign_from_lon(lon_deg)

def scan_ingresses(year=YEAR):
    start = datetime(year,1,1); end = datetime(year,12,31,23,59)
    step = timedelta(hours=6)
    ing = {k: [] for k in PLANETS}
    for pname in PLANETS:
        t = start
        prev = planet_sign_at(t, pname)
        while t <= end:
            t2 = t + step
            cur = planet_sign_at(t2, pname)
            if cur != prev:
                lo, hi = t, t2
                for _ in range(28):  # refine to ~minutes
                    mid = lo + (hi-lo)/2
                    if planet_sign_at(mid, pname) == prev:
                        lo = mid
                    else:
                        hi = mid
                dt = hi
                ing[pname].append((dt.date(), cur))
                prev = cur
            t = t2
    return ing

# ----- Your corrected 2026 dates -----
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
SEASON_TURNS = [
    ("March equinox",    date(2026,3,20)),
    ("June solstice",    date(2026,6,21)),
    ("September equinox",date(2026,9,22)),
    ("December solstice",date(2026,12,21)),
]
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

# ----- Drawing helpers -----
def add_text(c, x, y, text, size=9, bold=False, color=colors.black):
    c.setFont(BOLD if bold else FONT, size)
    c.setFillColor(color)
    c.drawString(x, y, text)

def month_page(c, year, month, ingresses):
    # Card background
    tint = colors.HexColor(TINTS[month])
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    card_x = MARGIN; card_y = MARGIN; card_w = W-2*MARGIN; card_h = H-2*MARGIN
    c.setFillColor(tint); c.roundRect(card_x, card_y, card_w, card_h, 12, fill=1, stroke=0)

    # Title
    add_text(c, card_x+0.7*cm, card_y+card_h-0.9*cm, f"{calendar.month_name[month]} {year}", size=20, bold=True)

    # Grid metrics
    title_h = 1.2*cm
    header_h = 0.9*cm
    top = card_y + card_h - title_h
    rows, cols = 6, 7
    cell_w = card_w/cols
    cell_h = (card_h - title_h - header_h)/rows

    # Weekday header (Mon–Sun)
    headers = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    c.setFont(BOLD, 11); c.setFillColor(colors.black)
    for i,wd in enumerate(headers):
        c.drawString(card_x + i*cell_w + 0.10*cm, top - 0.28*cm, wd)

    # Grid lines
    y0 = top - header_h + 0.08*cm
    c.setStrokeColor(colors.Color(0,0,0, alpha=0.14))
    for r in range(rows+1):
        c.line(card_x, y0 - r*cell_h, card_x+card_w, y0 - r*cell_h)
    for col in range(cols+1):
        c.line(card_x + col*cell_w, y0, card_x + col*cell_w, y0 - rows*cell_h)
    c.setStrokeColor(colors.black)

    # Month matrix (Mon-first)
    cal = calendar.Calendar(firstweekday=0)
    matrix = cal.monthdatescalendar(year, month)

    # Build daily event lists
    day_events = {}
    def push(d, s):
        day_events.setdefault(d, []).append(s)

    # Daily Moon-in
    for week in matrix:
        for d in week:
            if d.month == month:
                push(d, f"Moon in {moon_sign_on(d)}")

    # Phases (labels only)
    for d in NEW_MOONS:
        if d.month == month: push(d, "New Moon")
    for d in FULL_MOONS:
        if d.month == month: push(d, "Full Moon")

    # Eclipses (only on exact day)
    for name, d in ECLIPSES:
        if d.month == month: push(d, name)

    # Solstices/Equinoxes
    for name, d in SEASON_TURNS:
        if d.month == month: push(d, name)

    # Meteors (both days)
    for name, (d1, d2) in METEORS:
        if d1.month == month: push(d1, name)
        if d2.month == month: push(d2, name)

    # Planet ingresses (Sun + others) — no commas, arrow formatting
    for planet, items in ingresses.items():
        arrow = "Sun →" if planet == "Sun" else f"{planet} →"
        for d_local, sign in items:
            if d_local.year == year and d_local.month == month:
                push(d_local, f"{arrow} {sign}")

    # Special: Aug 27 shows no Full/Eclipse (your rule)
    if month == 8:
        d27 = date(2026,8,27)
        if d27 in day_events:
            day_events[d27] = [s for s in day_events[d27] if ("Full Moon" not in s and "Lunar eclipse" not in s)]

    # Draw cells
    for r in range(rows):
        if r >= len(matrix): break
        week = matrix[r]
        for col in range(cols):
            d = week[col]
            cx = card_x + col*cell_w
            top_cell = y0 - r*cell_h

            # Day number (top-right)
            c.setFont(BOLD, 11)
            if d.month == month: c.setFillColor(colors.black)
            else: c.setFillColor(colors.Color(0,0,0, alpha=0.28))
            c.drawRightString(cx + cell_w - 0.10*cm, top_cell - 0.24*cm, str(d.day))
            c.setFillColor(colors.black)

            # Stack events (start safely below date)
            line_y = top_cell - 0.48*cm
            line_h = 0.38*cm
            max_lines = int((cell_h - 0.30*cm)/line_h)  # safe capacity
            lines = day_events.get(d, [])

            # Sort events for nice reading order (Moon-in first, then phases, eclipses, seasons, meteors, ingresses)
            priority = {"Moon in":0, "New Moon":1, "Full Moon":1, "Solar eclipse":2, "Lunar eclipse":2,
                        "equinox":3, "solstice":3, "peak window":4, "Sun →":5, "Mercury →":6, "Venus →":7,
                        "Mars →":8, "Jupiter →":9, "Saturn →":10, "Uranus →":11, "Neptune →":12, "Pluto →":13}
            def keyfn(s):
                for k,v in priority.items():
                    if s.startswith(k) or k in s: return v
                return 99
            lines.sort(key=keyfn)

            shown = 0
            for s in lines:
                if shown >= max_lines:
                    add_text(c, cx+0.10*cm, line_y, "…", size=9)
                    break
                add_text(c, cx+0.10*cm, line_y, s, size=9)
                shown += 1; line_y -= line_h

    # Footer
    c.setFont(FONT,9)
    c.drawCentredString(W/2, 0.7*cm, "A4 landscape · print-friendly · © 2026 Serene")

def info_page(c):
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFont(BOLD,22); c.setFillColor(colors.black)
    c.drawCentredString(W/2, H-2.0*cm, "Information")
    c.setFont(FONT,12)
    y = H-3.1*cm
    items = [
        'In each day box: “Moon in <Sign>” (computed at a noon proxy for a clean daily feel).',
        'Phases appear as words only: “New Moon”, “Full Moon”.',
        'Eclipses, solstices/equinoxes, and major meteor shower peak windows are included.',
        'Sun & planet ingresses (Mercury → Pluto) are shown on the calendar date.',
        'Source cross-check: mooncalendar.astro-seek.com · All rights reserved.',
    ]
    for t in items:
        c.drawString(2.0*cm, y, "• " + t); y -= 0.95*cm
    c.showPage()

def reference_page(c, ingresses):
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    left_x = 2.0*cm; mid_x = W/2 + 0.7*cm; top = H - 1.8*cm

    # Full Moons 2026 (left)
    c.setFont(BOLD,18); c.setFillColor(colors.black)
    c.drawString(left_x, top, "Full Moons · 2026")
    c.setFont(FONT,12)
    y = top - 0.9*cm
    fml = [
        ("Jan 03","Full Moon"),
        ("Apr 02","Full Moon"),
        ("Aug 28","Full Moon · Lunar eclipse"),
        ("Sep 26","Full Moon"),
        ("Oct 26","Full Moon"),
        ("Nov 24","Full Moon"),
        ("Dec 24","Full Moon"),
    ]
    for d,label in fml:
        c.drawString(left_x, y, f"{d}: {label}")
        y -= 0.75*cm

    # Sun Enters Signs (right)
    c.setFont(BOLD,18)
    c.drawString(mid_x, top, "Sun Enters Signs · 2026")
    c.setFont(FONT,12)
    y2 = top - 0.9*cm
    suns = sorted(ingresses["Sun"], key=lambda t: t[0])
    for d, s in suns:
        c.drawString(mid_x, y2, f"{d.strftime('%b %d')}: Sun → {s}")
        y2 -= 0.75*cm

    # Zodiac keywords (bottom across)
    c.setFont(BOLD,18)
    c.drawString(left_x, H/2 - 0.3*cm, "Zodiac")
    c.setFont(FONT,12)
    y3 = H/2 - 1.1*cm
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
    colgap = 7.3*cm
    col2 = left_x + colgap
    col3 = left_x + 2*colgap
    i = 0
    for s in SIGNS:
        text = f"{s}: {kw[s]}"
        xcol = [left_x, col2, col3][i%3]
        c.drawString(xcol, y3 - 0.9*cm*(i//3), text)
        i += 1

    c.showPage()

def build():
    print("Computing Sun & planet ingresses…")
    ing = scan_ingresses(YEAR)

    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(A4))

    # 12 pages: one per month, full astro stack
    for m in range(1,13):
        month_page(c, YEAR, m, ing)
        c.showPage()

    # Info + Reference pages
    info_page(c)
    reference_page(c, ing)

    c.save()
    print("Saved:", PDF_PATH)

if __name__ == "__main__":
    build()
