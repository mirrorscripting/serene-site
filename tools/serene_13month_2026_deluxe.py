#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serene • 13-Month Calendar • 2026
Color preview generator with 3 variants:
  - core   : Winter Blue • Spring Pink • Summer Gold • Autumn Plum
  - deluxe : White • Gold • Black • Silver
  - neon   : Pink • Blue • Yellow • Green

Focus: COLORS ONLY (no astro overlays). Use this to approve palettes.
"""

import os
import argparse
import datetime as dt
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------- CLI ----------------
parser = argparse.ArgumentParser()
parser.add_argument("--variant", choices=["core","deluxe","neon"], default="deluxe",
                    help="Color palette variant")
parser.add_argument("--out", default="downloads/13/preview-2026.pdf",
                    help="Output PDF path")
args = parser.parse_args()

# ---------------- Fonts ----------------
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

# ---------------- Month layout (13 x 28 days) ----------------
MONTHS_13 = [
    ("January",   dt.date(2026,1,1),  dt.date(2026,1,28)),
    ("February",  dt.date(2026,1,29), dt.date(2026,2,25)),
    ("March",     dt.date(2026,2,26), dt.date(2026,3,25)),
    ("April",     dt.date(2026,3,26), dt.date(2026,4,22)),
    ("May",       dt.date(2026,4,23), dt.date(2026,5,20)),
    ("June",      dt.date(2026,5,21), dt.date(2026,6,17)),
    ("July",      dt.date(2026,6,18), dt.date(2026,7,15)),
    ("Sunny",     dt.date(2026,7,16), dt.date(2026,8,12)),
    ("August",    dt.date(2026,8,13), dt.date(2026,9,9)),
    ("September", dt.date(2026,9,10), dt.date(2026,10,7)),
    ("October",   dt.date(2026,10,8), dt.date(2026,11,4)),
    ("November",  dt.date(2026,11,5), dt.date(2026,12,2)),
    ("December",  dt.date(2026,12,3), dt.date(2026,12,30)),
]
YEAR_DAY = dt.date(2026,12,31)

# 28-day Thursday-start math
THU_COL = 3  # Mon=0..Sun=6
WEEKDAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

MONTH_SYMBOL = {
    "January":"✶","February":"♥","March":"❀","April":"✿","May":"❧","June":"✢","July":"✺",
    "Sunny":"✾","August":"✸","September":"❦","October":"❁","November":"✦","December":"✳",
}

# ---------------- Palettes ----------------
CORE = {  # seasonal
    "winter": colors.Color(0.75,0.85,1.00),   # blue
    "spring": colors.Color(1.00,0.85,0.95),   # pink
    "summer": colors.Color(1.00,0.93,0.70),   # gold
    "autumn": colors.Color(0.45,0.30,0.45),   # plum
}
DELUXE = {  # men-friendly, luxe
    "winter": colors.Color(1.00,1.00,1.00),   # white
    "spring": colors.Color(0.95,0.83,0.27),   # gold
    "summer": colors.Color(0.08,0.08,0.08),   # black
    "autumn": colors.Color(0.80,0.80,0.85),   # silver
}
NEON = {   # color-pop
    "winter": colors.Color(1.00,0.35,0.80),   # neon pink
    "spring": colors.Color(0.25,0.60,1.00),   # neon blue
    "summer": colors.Color(1.00,0.95,0.20),   # neon yellow
    "autumn": colors.Color(0.20,0.95,0.55),   # neon green
}

PAL = {"core": CORE, "deluxe": DELUXE, "neon": NEON}[args.variant]

def month_colors(p):
    return {
        "January": p["winter"], "February": p["winter"],
        "March": p["spring"], "April": p["spring"], "May": p["spring"],
        "June": p["summer"], "July": p["summer"], "Sunny": p["summer"], "August": p["summer"],
        "September": p["autumn"], "October": p["autumn"], "November": p["autumn"],
        "December": p["winter"],
    }

MONTH_BG = month_colors(PAL)

def is_dark(col: colors.Color) -> bool:
    # Relative luminance ~ simple
    r, g, b = col.red, col.green, col.blue
    lum = 0.2126*r + 0.7152*g + 0.0722*b
    return lum < 0.45

# ---------------- PDF ----------------
pdf_path = args.out
os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
W, H = landscape(A4)

def front_page():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONT, 30)
    title = "The 13-Month Calendar of 2026 — " + {"core":"Core","deluxe":"Deluxe (W•G•B•S)","neon":"Color-Pop"}[args.variant]
    c.drawCentredString(W/2, H-5.7*cm, title)
    c.setFont(FONT, 16)
    c.drawCentredString(W/2, H-7.2*cm, "28 Days · 13 Months · Year Day")
    c.setFont(FONT, 12)
    if args.variant == "core":
        c.drawCentredString(W/2, H-8.6*cm, "Seasonal palette: Winter (blue) · Spring (pink) · Summer (gold) · Autumn (plum)")
    elif args.variant == "deluxe":
        c.drawCentredString(W/2, H-8.6*cm, "Deluxe palette: White · Gold · Black · Silver")
    else:
        c.drawCentredString(W/2, H-8.6*cm, "Neon palette: Pink · Blue · Yellow · Green")
    c.showPage()

def draw_month(name):
    bg = MONTH_BG[name]
    c.setFillColor(bg); c.rect(0,0,W,H,fill=1,stroke=0)

    fg = colors.white if is_dark(bg) else colors.black
    c.setFillColor(fg)
    c.setFont(FONT, 22)
    hdr = f"{MONTH_SYMBOL.get(name,'')} {name} 2026".strip()
    c.drawCentredString(W/2, H-1.6*cm, hdr)

    # grid (7x4 exact fit; all months are 28 days)
    lm, rm, tm, bm = 1.6*cm, 1.6*cm, 3.0*cm, 2.0*cm
    left, top = lm, H - tm
    cols, rows = 7, 4
    cw = (W - lm - rm) / cols
    ch = (H - tm - bm) / rows

    # weekday header
    c.setFont(FONT, 10.5)
    c.setFillColor(colors.black if args.variant!="deluxe" or not is_dark(bg) else colors.white)
    for i, wd in enumerate(WEEKDAYS):
        c.drawCentredString(left + cw*(i+0.5), top + 0.4*cm, wd)

    # cells
    c.setFillColor(fg)
    c.setLineWidth(1)
    c.setFont(FONT, 15)

    for day in range(1, 29):  # 1..28
        col = (THU_COL + (day - 1)) % 7
        row = (THU_COL + (day - 1)) // 7
        x = left + col*cw
        y = top - (row+1)*ch

        # cell border (subtle)
        c.setStrokeColor(colors.Color(1,1,1,alpha=0.25) if is_dark(bg) else colors.Color(0,0,0,alpha=0.15))
        c.rect(x, y, cw, ch, stroke=1, fill=0)

        # big number bottom-center
        c.setFillColor(fg)
        c.setFont(FONT, 17 if args.variant!="neon" else 18)
        c.drawCentredString(x + cw/2, y + 0.28*cm, str(day))

def year_day_page():
    # simple neutral page
    c.setFillColor(colors.Color(0.98,0.98,0.98)); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONT, 24)
    c.drawCentredString(W/2, H-2.6*cm, "Year Day — New Year’s")
    c.setFont(FONT, 12)
    c.drawCentredString(W/2, H-4.1*cm, YEAR_DAY.strftime("Gregorian date: %A, %B %d, %Y"))
    c.showPage()

# -------- render --------
print(f"Building 2026 · 13-month {args.variant.upper()} …")
front_page()
for (name, _s, _e) in MONTHS_13:
    draw_month(name)
    c.showPage()
year_day_page()
c.save()
print(f"Saved: {os.path.abspath(pdf_path)}")
