import json, yaml
# -*- coding: utf-8 -*-
# Serene · 13-Month Calendar 2026 · Production (core / deluxe / neon)
# Spec: bold cell text, top-left big Gregorian date, mid-upper event block,
# front page with zodiac rows + palette line, info + phases + ingresses + year day,
# no em-dashes, tight spacing that never collides.

import argparse, os, math, random, datetime as dt
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------- fonts (bold everywhere in cells) ----------
FONT = "DejaVuSans"
FONTB = "DejaVuSans-Bold"
def _reg(name, path):
    if os.path.exists(path):
        try: pdfmetrics.registerFont(TTFont(name, path))
        except: pass
for p in (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/local/share/fonts/DejaVuSans.ttf",
): _reg(FONT, p)
for p in (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
): _reg(FONTB, p)
if FONT not in pdfmetrics.getRegisteredFontNames():  FONT  = "Helvetica"
if FONTB not in pdfmetrics.getRegisteredFontNames(): FONTB = "Helvetica-Bold"

# ---------- args ----------
ap = argparse.ArgumentParser()
ap.add_argument("--cfg", default="tools/palettes_2026.json")
ap.add_argument("--text", default="tools/text_2026.yml")
ap.add_argument("--variant", choices=["core","deluxe","neon"], required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

# ---------- 13-month model (Thu start, 28 days) ----------
months_13 = [
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

mapping = {}
for name, start, end in months_13:
    n = 1
    for i in range((end-start).days+1):
        d = start + dt.timedelta(days=i)
        mapping[d] = {"MonthName": name, "Day28": n}
        n += 1

# ---------- data ----------
z = {"Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓"}

FULLS = [
    (dt.date(2026,1,3),"Cancer"),(dt.date(2026,2,1),"Leo"),(dt.date(2026,3,3),"Virgo"),
    (dt.date(2026,4,1),"Libra"), (dt.date(2026,5,1),"Scorpio"),(dt.date(2026,5,31),"Sagittarius"),
    (dt.date(2026,6,29),"Capricorn"),(dt.date(2026,7,29),"Aquarius"),(dt.date(2026,8,28),"Pisces"),
    (dt.date(2026,9,26),"Aries"),(dt.date(2026,10,25),"Taurus"),(dt.date(2026,11,24),"Gemini"),
    (dt.date(2026,12,24),"Cancer"),
]
NEWS = [
    (dt.date(2026,1,18),"Capricorn"),(dt.date(2026,2,17),"Aquarius"),(dt.date(2026,3,19),"Pisces"),
    (dt.date(2026,4,17),"Aries"),(dt.date(2026,5,16),"Taurus"),(dt.date(2026,6,15),"Gemini"),
    (dt.date(2026,7,14),"Cancer"),(dt.date(2026,8,12),"Leo"),(dt.date(2026,9,11),"Virgo"),
    (dt.date(2026,10,10),"Libra"),(dt.date(2026,11,9),"Scorpio"),(dt.date(2026,12,9),"Sagittarius"),
]
SUN_IN = [
    (dt.date(2026,1,20),"Aquarius"),(dt.date(2026,2,18),"Pisces"),(dt.date(2026,3,20),"Aries"),
    (dt.date(2026,4,20),"Taurus"),(dt.date(2026,5,21),"Gemini"),(dt.date(2026,6,21),"Cancer"),
    (dt.date(2026,7,22),"Leo"),(dt.date(2026,8,23),"Virgo"),(dt.date(2026,9,23),"Libra"),
    (dt.date(2026,10,23),"Scorpio"),(dt.date(2026,11,22),"Sagittarius"),(dt.date(2026,12,21),"Capricorn"),
]
INGRESSES = {
    "Mercury":[(dt.date(2026,1,1),"Capricorn"),(dt.date(2026,1,20),"Aquarius"),(dt.date(2026,2,6),"Pisces"),
               (dt.date(2026,4,15),"Aries"),(dt.date(2026,5,3),"Taurus"),(dt.date(2026,6,1),"Cancer"),
               (dt.date(2026,7,9),"Leo"),(dt.date(2026,9,10),"Libra"),(dt.date(2026,9,30),"Scorpio"),
               (dt.date(2026,12,6),"Sagittarius"),(dt.date(2026,12,25),"Capricorn")],
    "Venus":[(dt.date(2026,1,17),"Aquarius"),(dt.date(2026,2,10),"Pisces"),(dt.date(2026,3,6),"Aries"),
             (dt.date(2026,3,30),"Taurus"),(dt.date(2026,4,24),"Gemini"),(dt.date(2026,5,19),"Cancer"),
             (dt.date(2026,6,13),"Leo"),(dt.date(2026,8,7),"Libra"),(dt.date(2026,9,11),"Scorpio"),
             (dt.date(2026,10,25),"Libra"),(dt.date(2026,12,4),"Scorpio")],
    "Mars":[(dt.date(2026,3,2),"Pisces"),(dt.date(2026,4,9),"Aries"),(dt.date(2026,5,18),"Taurus"),
            (dt.date(2026,6,28),"Gemini"),(dt.date(2026,8,11),"Cancer"),(dt.date(2026,9,28),"Leo"),
            (dt.date(2026,11,25),"Virgo")],
    "Jupiter":[(dt.date(2026,6,30),"Leo")],
    "Saturn":[(dt.date(2026,2,14),"Aries")],
    "Uranus":[(dt.date(2026,4,26),"Gemini")],
    "Neptune":[(dt.date(2026,1,26),"Aries")],
    "Pluto":[]
}
METEORS = [
    ("Quadrantids","Jan 02–03 · after midnight → pre-dawn"),
    ("Lyrids","Apr 21–22 · after midnight → pre-dawn"),
    ("Delta Aquarids","Jul 28–29 · best late evening to pre-dawn"),
    ("Perseids","Aug 12–13 · best late evening to pre-dawn"),
    ("Orionids","Oct 21–22 · after midnight → pre-dawn"),
    ("Taurids","Nov 04–05 · after midnight to pre-dawn"),
    ("Leonids","Nov 17–18 · after midnight to pre-dawn"),
    ("Geminids","Dec 13–14 · best late evening to pre-dawn"),
    ("Ursids","Dec 21–22 · after midnight to pre-dawn"),
]
SOURCES = ["https://www.astro-seek.com/","https://www.wheeloftheyear.com/2026/meteorshowers.htm"]

# ---------- palettes ----------
def C(r,g,b): return colors.Color(r,g,b)
SEASONAL = {"Winter":C(0.76,0.86,1.00),"Spring":C(1.00,0.86,0.95),"Summer":C(1.00,0.93,0.70),"Autumn":C(0.45,0.30,0.45)}
DELUXE   = {"Winter":C(0.97,0.98,0.99),"Spring":C(0.98,0.90,0.50),"Summer":C(0.05,0.05,0.05),"Autumn":C(0.86,0.88,0.92)}
NEON     = {"Winter":C(1.00,0.92,0.12),"Spring":C(1.00,0.78,0.93),"Summer":C(0.55,1.00,0.70),"Autumn":C(0.36,0.72,1.00)}

def season_of(month):
    if month in ("December","January","February"): return "Winter"
    if month in ("March","April","May"): return "Spring"
    if month in ("June","July","Sunny","August"): return "Summer"
    return "Autumn"

if args.variant=="core":
    PALETTE = SEASONAL
    palette_line = "Seasonal palette · Winter blue · Spring pink · Summer gold · Autumn plum"
elif args.variant=="deluxe":
    PALETTE = DELUXE
    palette_line = "Deluxe palette · Winter white · Spring gold · Summer black · Autumn silver"
else:
    PALETTE = NEON
    palette_line = "Color Pop palette · Yellow (winter) · Pink (spring) · Green (summer) · Blue (autumn)"

# ---------- utils ----------
def wrap(text, font, size, max_w):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        t = (cur+" "+w).strip()
        if cur and stringWidth(t, font, size) > max_w:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur: lines.append(cur)
    return lines

# ---------- build ----------
W,H = landscape(A4)
c = canvas.Canvas(args.out, pagesize=landscape(A4))

def front():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setStrokeColor(colors.black); c.setLineWidth(2)
    c.roundRect(0.8*cm,0.8*cm, W-1.6*cm, H-1.6*cm, 0.6*cm, stroke=1, fill=0)
    c.setFont(FONT,18); c.drawCentredString(W/2, H-2.3*cm, "♈  ♉  ♊  ♋  ♌  ♍")
    c.setFont(FONTB,28); c.drawCentredString(W/2, H-5.0*cm, "The 13 Month Calendar of 2026")
    c.setFont(FONT,13); c.drawCentredString(W/2, H-6.4*cm, "28 Days · 13 Months · 1 Year Day")
    c.setFont(FONT,10.5); c.drawCentredString(W/2, H-7.8*cm, "Every month begins on Thursday")
    c.setFont(FONT,10.5); c.drawCentredString(W/2, H-9.2*cm, palette_line)
    c.setFont(FONT,18); c.drawCentredString(W/2, 1.8*cm, "♎  ♏  ♐  ♑  ♒  ♓")
    c.showPage()

def info_page():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONTB,22); c.drawCentredString(W/2, H-2.2*cm, "Information")
    x = 2.4*cm; y = H-4.0*cm
    c.setFont(FONTB,12); c.drawString(x,y,"Symbols"); y-=0.55*cm
    c.setFont(FONT,10.5)
    c.drawString(x,y,"♈ Aries  ♉ Taurus  ♊ Gemini  ♋ Cancer  ♌ Leo  ♍ Virgo  ♎ Libra  ♏ Scorpio  ♐ Sagittarius  ♑ Capricorn  ♒ Aquarius  ♓ Pisces"); y-=0.7*cm
    c.drawString(x,y,"Calendar: ○ New Moon · ● Full Moon · Sun→Sign · Planet→Sign · Mercury R starts/ends · Eclipse · Equinox · Solstice"); y-=0.9*cm
    c.setFont(FONTB,12); c.drawString(x,y,"Meteor Showers · Peak windows"); y-=0.55*cm
    c.setFont(FONT,10.5)
    for name,note in METEORS:
        c.drawString(x,y,f"{name}: {note}"); y-=0.48*cm
    y-=0.4*cm
    c.setFont(FONTB,12); c.drawString(x,y,"Sources"); y-=0.55*cm
    c.setFont(FONT,10.5)
    for s in SOURCES:
        c.drawString(x,y,s); y-=0.48*cm
    c.showPage()

def phase_pages():
    # Fulls
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONTB,20); c.drawCentredString(W/2, H-2.2*cm, "Full Moons · 2026")
    xL, xR = 2.2*cm, W/2 + 0.6*cm; y0 = H-4.0*cm
    c.setFont(FONT,11)
    half = (len(FULLS)+1)//2
    for i,(d,sg) in enumerate(FULLS[:half]):  c.drawString(xL, y0 - i*0.62*cm, f"{d:%b %d}: Full Moon in {sg} {z[sg]}")
    for i,(d,sg) in enumerate(FULLS[half:]): c.drawString(xR, y0 - i*0.62*cm, f"{d:%b %d}: Full Moon in {sg} {z[sg]}")
    c.showPage()
    # News
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONTB,20); c.drawCentredString(W/2, H-2.2*cm, "New Moons · 2026")
    c.setFont(FONT,11)
    half = (len(NEWS)+1)//2
    for i,(d,sg) in enumerate(NEWS[:half]):  c.drawString(xL, y0 - i*0.62*cm, f"{d:%b %d}: New Moon in {sg} {z[sg]}")
    for i,(d,sg) in enumerate(NEWS[half:]): c.drawString(xR, y0 - i*0.62*cm, f"{d:%b %d}: New Moon in {sg} {z[sg]}")
    c.showPage()

def ingress_page():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONTB,22); c.drawCentredString(W/2, H-2.2*cm, "Planet Ingresses · 2026 (dates only)")
    cols = [2.0*cm, W/3+0.3*cm, 2*W/3+0.6*cm]; y0 = H-4.1*cm
    groups = [("Mercury","Venus","Mars"),("Jupiter","Saturn","Uranus"),("Neptune","Pluto",None)]
    for ci,(a,b,d3) in enumerate(groups):
        x = cols[ci]; y = y0
        for p in (a,b,d3):
            if not p: continue
            c.setFont(FONTB,12); c.drawString(x,y,p); y-=0.55*cm
            c.setFont(FONT,10.5)
            for (d,sg) in INGRESSES.get(p,[]):
                c.drawString(x,y,f"{d:%b %d} · {sg} {z.get(sg,'')}"); y-=0.48*cm
            y-=0.35*cm
    c.showPage()

def year_day():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(colors.Color(0,0,0,alpha=0.06))
    random.seed(2026)
    for _ in range(160):
        x = random.uniform(1*cm, W-1*cm); y = random.uniform(2*cm, H-2*cm); r = random.uniform(0.3,0.9)
        c.circle(x,y,r,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONTB,26); c.drawCentredString(W/2, H-3.0*cm, "Year Day · New Year’s")
    c.setFont(FONT,12); c.drawCentredString(W/2, H-4.3*cm, YEAR_DAY.strftime("Gregorian date · %A, %B %d, %Y"))
    c.setFont(FONT,11)
    y = H-6.0*cm
    for line in ("align · act · rest · renew","create · refine · release · receive","quiet the noise · crown the signal"):
        c.drawCentredString(W/2, y, line); y -= 0.85*cm
    c.setFont(FONT,9); c.drawCentredString(W/2, 1.5*cm, "© 2026 · Serene · All rights reserved")
    c.showPage()

THU_COL = 3
def draw_month(name, start, end):
    season = season_of(name)
    bg = {"core":SEASONAL,"deluxe":DELUXE,"neon":NEON}[args.variant][season]
    c.setFillColor(bg); c.rect(0,0,W,H,fill=1,stroke=0)

    # colors
    if args.variant=="deluxe" and season=="Summer":  fg, frame, head = colors.white, colors.white, colors.white
    elif season=="Autumn" and args.variant!="deluxe": fg, frame, head = colors.white, colors.black, colors.white
    else: fg, frame, head = colors.black, colors.black, colors.black

    # header
    c.setFillColor(fg); c.setFont(FONTB,28); c.drawCentredString(W/2, H-1.6*cm, f"✶ {name} 2026")

    # weekday row
    left = 1.4*cm; top = H-3.4*cm; cols,rows = 7,5
    cw = (W-2.8*cm)/cols; ch=(H-5.4*cm)/rows
    c.setFillColor(head); c.setFont(FONTB,13)
    for i,wd in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        c.drawCentredString(left+cw*(i+0.5), top+0.40*cm, wd)

    # cells
    pad = 0.22*cm
    for i in range(28):
        d = start + dt.timedelta(days=i)
        day28 = mapping[d]["Day28"]
        col = (THU_COL + (day28-1)) % 7
        r   = (THU_COL + (day28-1)) // 7
        x = left + col*cw; y = top - (r+1)*ch
        c.setStrokeColor(frame); c.setLineWidth(1.0); c.rect(x,y,cw,ch,stroke=1,fill=0)

        # Gregorian date (big, bold, top-left)
        c.setFillColor(fg); c.setFont(FONTB,10.2)
        c.drawString(x+pad, y+ch-0.38*cm, d.strftime("%b %d"))

        # Event block: bold, mid-upper with guard
        usable = cw - 2*pad
        y_line = y + ch - 1.02*cm
        gap = 0.26*cm
        c.setFont(FONTB,8.6)

        def add(txt):
            nonlocal y_line
            for line in wrap(txt, FONTB, 8.6, usable):
                if y_line < y+0.66*cm: return
                c.drawString(x+pad, y_line, line)
                y_line -= gap

        # phases
        for d0,sg in FULLS:
            if d==d0: add(f"● Full Moon in {sg} {z[sg]}")
        for d0,sg in NEWS:
            if d==d0: add(f"○ New Moon in {sg} {z[sg]}")
        # sun ingress
        for d0,sg in SUN_IN:
            if d==d0: add(f"Sun → {sg} {z[sg]}")
        # planet ingresses
        for p,items in INGRESSES.items():
            for d0,sg in items:
                if d==d0: add(f"{p} → {sg} {z.get(sg,'')}")

        # big 1–28 bottom
        c.setFont(FONTB,18); c.drawCentredString(x+cw/2, y+0.24*cm, str(day28))

    c.showPage()

# render
W,H = landscape(A4)
front()
for name,start,end in months_13:
    draw_month(name,start,end)
info_page()
phase_pages()
ingress_page()
year_day()
c.save()
print(f"Saved: {args.out}")



