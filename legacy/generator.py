# -*- coding: utf-8 -*-
# 2026 · 13-Month Calendar · Production build (+ Ingresses page)
# Variants: core (seasonal), deluxe (white·gold·black·silver), neon (yellow·pink·green·blue)
# Calendar changes:
# - Front page: white with rounded frame; bold zodiac ribbon
# - Info page: white; sources astro-seek + wheeloftheyear
# - Year Day: white; mantras in black; © 2026 Serene. All rights reserved.
# - Meteor windows updated; labels use "peak window"
# - Borders:
#     core: white borders
#     deluxe: Winter/Spring/Autumn borders black; Summer borders white
#     neon: all borders black
# - Text colors (weekday headers + cell text + big 1–28):
#     core: Autumn months white text; others black
#     deluxe: Summer white text; others black
#     neon: all black text
# - Month cells: mini Gregorian date fixed top-left; event stack lifted; tighter spacing
#
# Plus: a single-page "Planet Ingresses · 2026 (dates only)" with a 3-column layout.

import os, math, random, argparse, datetime as dt
from zoneinfo import ZoneInfo
from dateutil.rrule import rrule, DAILY
import ephem

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------------- Timezones ----------------
OSLO = ZoneInfo("Europe/Oslo")
UTC  = ZoneInfo("UTC")

# ---------------- Fonts ----------------
FONT_REG  = "DejaVuSans"
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

# ---------------- 13-month layout ----------------
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

# Map Gregorian → Day1..28
mapping = {}
for name, start, end in months_13:
    n = 1
    for d in rrule(DAILY, dtstart=start, until=end):
        mapping[d.date()] = {"MonthName": name, "Day28": n}
        n += 1

# ---------------- Palettes ----------------
PALETTES = {
    "core": {  # Winter blue, Spring pink, Summer gold, Autumn plum
        "January": colors.Color(0.75,0.85,1.00),
        "February": colors.Color(0.75,0.85,1.00),
        "March": colors.Color(1.00,0.85,0.95),
        "April": colors.Color(1.00,0.85,0.95),
        "May": colors.Color(1.00,0.85,0.95),
        "June": colors.Color(1.00,0.93,0.70),
        "July": colors.Color(1.00,0.93,0.70),
        "Sunny": colors.Color(1.00,0.93,0.70),
        "August": colors.Color(1.00,0.93,0.70),
        "September": colors.Color(0.45,0.30,0.45),
        "October": colors.Color(0.45,0.30,0.45),
        "November": colors.Color(0.45,0.30,0.45),
        "December": colors.Color(0.75,0.85,1.00),
    },
    "deluxe": {  # White • Gold • Black • Silver
        "January":   colors.Color(1,1,1),
        "February":  colors.Color(1,1,1),
        "March":     colors.Color(0.96,0.80,0.20),
        "April":     colors.Color(0.96,0.80,0.20),
        "May":       colors.Color(0.96,0.80,0.20),
        "June":      colors.black,
        "July":      colors.black,
        "Sunny":     colors.black,
        "August":    colors.black,
        "September": colors.Color(0.82,0.84,0.86),
        "October":   colors.Color(0.82,0.84,0.86),
        "November":  colors.Color(0.82,0.84,0.86),
        "December":  colors.Color(1,1,1),
    },
    "neon": {  # Yellow • Pink • Green • Blue
        "January":   colors.Color(1.00,0.82,0.12),
        "February":  colors.Color(1.00,0.82,0.12),
        "March":     colors.Color(1.00,0.60,0.85),
        "April":     colors.Color(1.00,0.60,0.85),
        "May":       colors.Color(1.00,0.60,0.85),
        "June":      colors.Color(0.10,0.95,0.35),
        "July":      colors.Color(0.10,0.95,0.35),
        "Sunny":     colors.Color(0.10,0.95,0.35),
        "August":    colors.Color(0.10,0.95,0.35),
        "September": colors.Color(0.20,0.55,1.00),
        "October":   colors.Color(0.20,0.55,1.00),
        "November":  colors.Color(0.20,0.55,1.00),
        "December":  colors.Color(1.00,0.82,0.12),
    },
}

def _season(month_name):
    if month_name in ("December","January","February"): return "Winter"
    if month_name in ("March","April","May"):           return "Spring"
    if month_name in ("June","July","Sunny","August"):  return "Summer"
    return "Autumn"

def border_color_for_cell(variant, month_name):
    season = _season(month_name)
    if variant == "deluxe":
        return colors.black if season in ("Winter","Spring","Autumn") else colors.white
    if variant == "neon":
        return colors.black
    return colors.white  # core

def text_color_for_cell(variant, month_name):
    season = _season(month_name)
    if variant == "core":   return colors.white if season == "Autumn" else colors.black
    if variant == "deluxe": return colors.white if season == "Summer" else colors.black
    return colors.black  # neon

weekday_color = text_color_for_cell

# ---------------- Symbols ----------------
month_symbols = {"January":"✶","February":"♥","March":"❀","April":"✿","May":"❧","June":"✢","July":"✺","Sunny":"✾","August":"✸","September":"❦","October":"❁","November":"✦","December":"✳"}
zodiac_glyph  = {"Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓"}
zodiac_order  = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# ---------------- Phases ----------------
full_moons = {
    dt.date(2026,1,3):"Cancer",
    dt.date(2026,2,1):"Leo",
    dt.date(2026,3,3):"Virgo",
    dt.date(2026,4,2):"Libra",
    dt.date(2026,5,1):"Scorpio",
    dt.date(2026,5,31):"Sagittarius",
    dt.date(2026,6,29):"Capricorn",
    dt.date(2026,7,29):"Aquarius",
    dt.date(2026,8,28):"Pisces",
    dt.date(2026,9,26):"Aries",
    dt.date(2026,10,26):"Taurus",
    dt.date(2026,11,24):"Gemini",
    dt.date(2026,12,24):"Cancer",
}
new_moons = {
    dt.date(2026,1,18):"Capricorn",
    dt.date(2026,2,17):"Aquarius",
    dt.date(2026,3,19):"Pisces",
    dt.date(2026,4,17):"Aries",
    dt.date(2026,5,16):"Taurus",
    dt.date(2026,6,15):"Gemini",
    dt.date(2026,7,14):"Cancer",
    dt.date(2026,8,12):"Leo",
    dt.date(2026,9,11):"Virgo",
    dt.date(2026,10,10):"Libra",
    dt.date(2026,11,9):"Scorpio",
    dt.date(2026,12,8):"Sagittarius",
}

# Sun ingresses (dates)
sun_ingress = {
    dt.date(2026,1,20):"Aquarius",   dt.date(2026,2,18):"Pisces",
    dt.date(2026,3,20):"Aries",      dt.date(2026,4,20):"Taurus",
    dt.date(2026,5,21):"Gemini",     dt.date(2026,6,21):"Cancer",
    dt.date(2026,7,22):"Leo",        dt.date(2026,8,23):"Virgo",
    dt.date(2026,9,23):"Libra",      dt.date(2026,10,23):"Scorpio",
    dt.date(2026,11,22):"Sagittarius", dt.date(2026,12,21):"Capricorn",
}

# Optional holidays
GLOBAL_HOLIDAYS = {
    dt.date(2026,4,5):  "Easter Sunday ★",
    dt.date(2026,10,31):"Halloween ★",
    dt.date(2026,12,25):"Christmas Day ★",
}

# Eclipses
eclipses = [
    (dt.date(2026,2,17),"Solar"),
    (dt.date(2026,3,3), "Lunar"),
    (dt.date(2026,8,12),"Solar"),
    (dt.date(2026,8,28),"Lunar"),
]

# Equinoxes & Solstices
season_markers = {
    dt.date(2026,3,20): "Spring Equinox",
    dt.date(2026,6,21): "Summer Solstice",
    dt.date(2026,9,23): "Autumn Equinox",
    dt.date(2026,12,21):"Winter Solstice",
}

# Meteor windows (inclusive) — labels have no dashes
METEOR_WINDOWS = [
    (dt.date(2026,1,2),  dt.date(2026,1,3),  "Quadrantids peak window"),
    (dt.date(2026,4,21), dt.date(2026,4,22), "Lyrids peak window"),
    (dt.date(2026,7,28), dt.date(2026,7,29), "Delta Aquarids peak window"),
    (dt.date(2026,8,12), dt.date(2026,8,13), "Perseids peak window"),
    (dt.date(2026,10,21),dt.date(2026,10,22),"Orionids peak window"),
    (dt.date(2026,11,4), dt.date(2026,11,5), "Taurids peak window"),
    (dt.date(2026,11,17),dt.date(2026,11,18),"Leonids peak window"),
    (dt.date(2026,12,13),dt.date(2026,12,14),"Geminids peak window"),
    (dt.date(2026,12,21),dt.date(2026,12,22),"Ursids peak window"),
]
def meteor_labels_for_date(d):
    return [label for a,b,label in METEOR_WINDOWS if a<=d<=b]

# ---------------- Astro helpers ----------------
def moon_sign_for_day(d: dt.date)->str:
    local = dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC)
    e = ephem.Ecliptic(ephem.Moon(local))
    lon = (float(e.lon)*180.0/math.pi)%360.0
    return zodiac_order[int(lon//30)]

PLANETS = {
    "Mercury":ephem.Mercury,"Venus":ephem.Venus,"Mars":ephem.Mars,
    "Jupiter":ephem.Jupiter,"Saturn":ephem.Saturn,"Uranus":ephem.Uranus,
    "Neptune":ephem.Neptune,"Pluto":ephem.Pluto
}
def _sidx(body_ctor,t)->int:
    e=ephem.Ecliptic(body_ctor(t))
    lon=(float(e.lon)*180.0/math.pi)%360.0
    return int(lon//30)
def _ing(body_ctor,year):
    out=[]; d=dt.date(year,1,1); end=dt.date(year,12,31)
    prev=_sidx(body_ctor, dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC))
    while d<=end:
        idx=_sidx(body_ctor, dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC))
        if idx!=prev:
            out.append((d,zodiac_order[idx])); prev=idx
        d+=dt.timedelta(days=1)
    return out

ingresses={p:_ing(ctor,2026) for p,ctor in PLANETS.items()}
planet_ingress_by_date={}
for p,items in ingresses.items():
    for d,sign in items:
        planet_ingress_by_date.setdefault(d,[]).append(f"{p} → {sign} {zodiac_glyph[sign]}")

# Mercury retro markers (start/end)
def _elon(body_ctor,t):
    e=ephem.Ecliptic(body_ctor(t))
    return (float(e.lon)*180.0/math.pi)%360.0
def mercury_retrograde_periods(year):
    start=dt.date(year,1,1); end=dt.date(year,12,31)
    prev=_elon(ephem.Mercury, dt.datetime(start.year,start.month,start.day,12,0,tzinfo=OSLO).astimezone(UTC))
    inR=False; res=[]; Rs=None
    d=start+dt.timedelta(days=1)
    while d<=end:
        lon=_elon(ephem.Mercury, dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC))
        delta=lon-prev
        if delta<-180: delta+=360
        if delta>180:  delta-=360
        if not inR and delta<0: inR=True; Rs=d
        elif inR and delta>=0: inR=False; res.append((Rs,d)); Rs=None
        prev=lon; d+=dt.timedelta(days=1)
    if inR and Rs: res.append((Rs,end))
    return res
retro_markers={}
for a,b in mercury_retrograde_periods(2026):
    retro_markers.setdefault(a,[]).append("Mercury R starts")
    retro_markers.setdefault(b,[]).append("Mercury R ends")

# ---------------- PDF helpers ----------------
def wrap_to_width(text,font,size,max_w):
    words=text.split(" "); lines=[]; cur=""
    for w in words:
        trial=w if not cur else f"{cur} {w}"
        if cur and stringWidth(trial,font,size)>max_w:
            lines.append(cur); cur=w
        else:
            cur=trial
    if cur: lines.append(cur)
    return lines
def safe_join(items): return " · ".join(items)
def first_wrapped_line(text, font_name, font_size, max_w):
    wrapped = wrap_to_width(text, font_name, font_size, max_w)
    if not wrapped: return ""
    return wrapped[0].rstrip(" ,.;:·")

# ---------------- Calendar Pages ----------------
def front_palette_line(variant):
    if variant=="core":
        return "Seasonal palette · Winter → Blue · Spring → Pink · Summer → Gold · Autumn → Plum"
    if variant=="deluxe":
        return "Deluxe palette · Winter → White · Spring → Gold · Summer → Black · Autumn → Silver"
    if variant=="neon":
        return "Color Pop palette · Winter → Yellow · Spring → Pink · Summer → Green · Autumn → Blue"
    return ""

def draw_front(c, W, H, variant):
    # white background
    c.setFillColor(colors.white); c.rect(0, 0, W, H, fill=True, stroke=False)

    # title + meta
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD, 40); c.drawCentredString(W/2, H - 6*cm, "The 13-Month Calendar of 2026")
    c.setFont(FONT_REG, 19);  c.drawCentredString(W/2, H - 8*cm, "28 Days · 13 Months · 1 Year Day")
    c.setFont(FONT_REG, 13);  c.drawCentredString(W/2, H - 9.5*cm, "Every month begins on Thursday")
    c.setFont(FONT_REG, 12);  c.drawCentredString(W/2, H - 11.0*cm, front_palette_line(variant))

    # bold zodiac ribbon
    zodiac_row = " ".join(["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"])
    c.setFont(FONT_BOLD, 24)
    c.drawCentredString(W/2, H - 12.6*cm, zodiac_row)

    # subtle rounded frame
    m = 2.0*cm
    c.setLineWidth(2)
    c.setStrokeColor(colors.Color(0, 0, 0, 0.12))
    c.roundRect(m, m, W - 2*m, H - 2*m, 14, stroke=True, fill=False)

def draw_month(c,W,H,variant,name,start,end):
    # background
    bg = PALETTES[variant][name]
    c.setFillColor(bg); c.rect(0,0,W,H,fill=True,stroke=False)

    # colors
    fg = text_color_for_cell(variant, name)
    wd = weekday_color(variant, name)

    # header
    sym=month_symbols.get(name,"")
    c.setFillColor(fg); c.setFont(FONT_BOLD,26)
    c.drawCentredString(W/2, H-1.6*cm, f"{sym+' ' if sym else ''}{name} 2026")

    # grid
    lm,rm,tm,bm = 1.8*cm,1.8*cm,3.0*cm,2.3*cm
    left,top=lm,H-tm; cols,rows=7,5
    cw=(W-lm-rm)/cols; ch=(H-tm-bm)/rows; pad=0.22*cm

    # weekday headers
    c.setFont(FONT_BOLD,11); c.setFillColor(wd)
    for i,wdn in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        c.drawCentredString(left+cw*(i+0.5), top+0.42*cm, wdn)

    # day cells
    dates=[d.date() for d in rrule(DAILY,dtstart=start,until=end)]
    THU_COL=3
    c.setLineWidth(1)
    for d in dates:
        day28=mapping[d]["Day28"]; col=(THU_COL+(day28-1))%7; r=(THU_COL+(day28-1))//7
        x=left+col*cw; y=top-(r+1)*ch

        # border
        c.setStrokeColor(border_color_for_cell(variant, name))
        c.rect(x,y,cw,ch)

        c.setFillColor(fg)

        # --- date (top-left) ---
        c.setFont(FONT_BOLD, 7.2)
        c.drawString(x + pad, y + ch - 0.36*cm, d.strftime("%b %d"))

        # layout numbers for the stacked info (lifted higher)
        stack_start = y + ch*0.72
        line_gap    = 0.24*cm
        safe_floor  = y + 0.92*cm
        usable_w    = cw - 2*pad

        # --- stacked lines (without the date now) ---
        lines = []
        ms = moon_sign_for_day(d); mg = zodiac_glyph[ms]
        lines.append(f"Moon in {ms} {mg}")

        if d in new_moons:
            lines.append("○ New Moon")
        if d in full_moons:
            lines.append("● Full Moon")

        if d in sun_ingress:
            s = sun_ingress[d]; lines.append(f"Sun → {s} {zodiac_glyph[s]}")

        for ed,kind in eclipses:
            if d == ed:
                if kind == "Lunar":
                    lines.append(f"Lunar Eclipse {mg}")
                else:
                    sdt  = dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC)
                    slon = (float(ephem.Ecliptic(ephem.Sun(sdt)).lon)*180.0/math.pi)%360.0
                    ssign = zodiac_order[int(slon//30)]
                    lines.append(f"Solar Eclipse {zodiac_glyph[ssign]}")
                break

        if d in GLOBAL_HOLIDAYS:
            lines.append(GLOBAL_HOLIDAYS[d])

        if d in planet_ingress_by_date:
            compact = safe_join(planet_ingress_by_date[d])
            first = first_wrapped_line(compact, FONT_BOLD, 7.0, usable_w)
            if first: lines.append(first)

        if d in retro_markers:
            txt = safe_join(retro_markers[d])
            first = first_wrapped_line(txt, FONT_BOLD, 7.0, usable_w)
            if first: lines.append(first)

        for lbl in meteor_labels_for_date(d):
            lines.append(lbl)

        # draw the stack
        y_line = stack_start
        for txt in lines:
            if y_line < safe_floor:
                c.setFont(FONT_BOLD, 7.0); c.drawString(x + pad, y_line, "…")
                break
        # draw each line
            size = 7.0
            if stringWidth(txt, FONT_BOLD, size) > usable_w:
                w0 = wrap_to_width(txt, FONT_BOLD, size, usable_w)
                if w0: txt = w0[0].rstrip(" ,.;:·")
            c.setFont(FONT_BOLD, size); c.drawString(x + pad, y_line, txt)
            y_line -= line_gap

        # big 1–28 bottom
        c.setFont(FONT_BOLD,18); c.setFillColor(fg)
        c.drawCentredString(x+cw/2, y+0.28*cm, str(day28))

def draw_information(c,W,H):
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD,24); c.drawCentredString(W/2, H-2.5*cm, "Information")

    y=H-4.5*cm; left=3*cm
    c.setFont(FONT_BOLD,12); c.drawString(left,y,"Symbols"); y-=0.6*cm
    c.setFont(FONT_REG,11)
    for line in [
        "♈ Aries    ♉ Taurus    ♊ Gemini    ♋ Cancer",
        "♌ Leo      ♍ Virgo     ♎ Libra     ♏ Scorpio",
        "♐ Sagittarius    ♑ Capricorn    ♒ Aquarius    ♓ Pisces",
    ]:
        c.drawString(left,y,line); y-=0.5*cm

    c.drawString(left,y,"Month symbols · ✶ ♥ ❀ ✿ ❧ ✢ ✺ ✾ ✸ ❦ ❁ ✦ ✳"); y-=0.8*cm

    c.setFont(FONT_BOLD,12); c.drawString(left,y,"Event Types"); y-=0.6*cm
    c.setFont(FONT_REG,11)
    for line in [
        "○ New Moon · ● Full Moon · Sun → Sign",
        "Planet → Sign (Mercury to Pluto)",
        "Mercury R starts · Mercury R ends",
        "Eclipse (Solar or Lunar) · Equinox · Solstice",
    ]:
        c.drawString(left,y,line); y-=0.5*cm

    c.setFont(FONT_BOLD,12); c.drawString(left,y,"Meteor Showers · Peak windows"); y-=0.6*cm
    c.setFont(FONT_REG,11)
    for line in [
        "Quadrantids · Jan 2 to Jan 3 · best after midnight to pre dawn",
        "Lyrids · Apr 21 to Apr 22 · best after midnight to pre dawn",
        "Delta Aquarids · Jul 28 to Jul 29 · best after midnight to pre dawn",
        "Perseids · Aug 12 to Aug 13 · best late evening to pre dawn",
        "Orionids · Oct 21 to Oct 22 · best after midnight to pre dawn",
        "Taurids · Nov 4 to Nov 5 · best after midnight to pre dawn",
        "Leonids · Nov 17 to Nov 18 · best after midnight to pre dawn",
        "Geminids · Dec 13 to Dec 14 · best late evening to pre dawn",
        "Ursids · Dec 21 to Dec 22 · best after midnight to pre dawn",
    ]:
        c.drawString(left,y,line); y-=0.5*cm

    y-=0.6*cm; c.setFont(FONT_BOLD,12); c.drawString(left,y,"Sources"); y-=0.55*cm
    c.setFont(FONT_REG,11)
    c.drawString(left,y,"astro-seek.com"); y-=0.45*cm
    c.drawString(left,y,"wheeloftheyear.com/2026/meteorshowers.htm")
    c.showPage()

def draw_reference(c,W,H):
    # White page
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False); c.setFillColor(colors.black)

    left_x   = 2.2*cm
    right_x  = W/2 + 0.8*cm
    top_y    = H - 2.9*cm
    line_h   = 0.60*cm
    bottom_margin = 2.0*cm

    def draw_two_column_panel(x_left,x_right,y_start,title,items,fmt,rows_left_max=7,title_size=18,text_size=11):
        c.setFont(FONT_BOLD,title_size); c.drawString(x_left,y_start,title)
        y_txt=y_start-0.9*cm; c.setFont(FONT_REG,text_size)
        rows=min(rows_left_max,len(items)); left_items=items[:rows]; right_items=items[rows:]
        yL=y_txt
        for it in left_items: c.drawString(x_left,yL,fmt(it)); yL-=line_h
        yR=y_txt
        for it in right_items: c.drawString(x_right,yR,fmt(it)); yR-=line_h
        return min(yL,yR)

    # Full Moons (two columns)
    traditional_names={1:"Wolf Moon",2:"Snow Moon",3:"Worm Moon",4:"Pink Moon",5:"Flower Moon",6:"Strawberry Moon",7:"Buck Moon",8:"Sturgeon Moon",9:"Harvest Moon",10:"Hunter’s Moon",11:"Beaver Moon",12:"Cold Moon"}
    fm=[]
    for d,sign in sorted(full_moons.items()):
        name=traditional_names[d.month]
        if sum(1 for dd in full_moons if dd.month==d.month)>1 and d==max([dd for dd in full_moons if dd.month==d.month]):
            name="Blue Moon"
        fm.append((d,sign,name))
    def fmt_fm(it): d,sign,name=it; return f"{d.strftime('%b %d')}: Full Moon in {sign} {zodiac_glyph[sign]} · {name}"
    y_after_fm = draw_two_column_panel(left_x,right_x,top_y,"Full Moons 2026",fm,fmt_fm,rows_left_max=7)

    # Bottom sections: Zodiac (left) and Sun entries (right)
    y_next = y_after_fm - 1.0*cm

    c.setFont(FONT_BOLD,16); c.drawString(left_x,y_next,"Zodiac")
    y_z = y_next - 0.8*cm
    keywords={"Aries":"initiative · courage · spark","Taurus":"stability · senses · patience","Gemini":"curiosity · dialogue · agility","Cancer":"nurture · home · intuition","Leo":"creativity · heart · play","Virgo":"craft · service · clarity","Libra":"balance · beauty · harmony","Scorpio":"depth · devotion · transformation","Sagittarius":"vision · freedom · truth","Capricorn":"structure · ambition · endurance","Aquarius":"innovation · community · future","Pisces":"empathy · dreams · flow"}
    label_width = 3.1*cm
    z_line_h = 0.66*cm
    for s in ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]:
        if y_z < bottom_margin + z_line_h: break
        c.setFont(FONT_BOLD,11); c.drawString(left_x, y_z, f"{zodiac_glyph[s]} {s}:")
        c.setFont(FONT_REG,11);  c.drawString(left_x + label_width, y_z, keywords[s])
        y_z -= z_line_h

    c.setFont(FONT_BOLD,16); c.drawString(right_x,y_next,"Sun entries")
    y_s = y_next - 0.8*cm; c.setFont(FONT_REG,11)
    sun_items = sorted(sun_ingress.items())
    def fmt_s(it): d,sign=it; return f"{d.strftime('%b %d')}: Sun → {sign} {zodiac_glyph[sign]}"
    rows_per_col=8; col_w=6.6*cm
    x1=right_x; x2=right_x+col_w
    for it in sun_items[:rows_per_col]:
        if y_s < bottom_margin + line_h: break
        c.drawString(x1,y_s,fmt_s(it)); y_s-=line_h
    y_s2 = y_next - 0.8*cm
    for it in sun_items[rows_per_col:]:
        if y_s2 < bottom_margin + line_h: break
        c.drawString(x2,y_s2,fmt_s(it)); y_s2-=line_h

    c.showPage()

def draw_year_day(c,W,H):
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)
    random.seed(2026); c.setFillColor(colors.Color(0,0,0,alpha=0.08))
    for _ in range(160):
        x=random.uniform(1.0*cm,W-1.0*cm); y2=random.uniform(2.0*cm,H-2.0*cm); r=random.uniform(0.25,0.8)
        c.circle(x, y2, r, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD,28); c.drawCentredString(W/2,H-3*cm,"Year Day · New Year’s")
    c.setFont(FONT_REG,12); c.drawCentredString(W/2,H-4.4*cm, YEAR_DAY.strftime("Gregorian date · %A, %B %d, %Y"))
    c.setFont(FONT_REG,12); y0 = H-6.2*cm
    for m in ["align · act · rest · renew","create · refine · release · receive","quiet the noise · crown the signal"]:
        c.drawCentredString(W/2,y0,m); y0-=0.9*cm
    c.setFont(FONT_REG,10)
    c.drawCentredString(W/2,1.4*cm,"© 2026 Serene. All rights reserved.")
    c.showPage()

# ---------------- Build Calendar ----------------
def build_calendar(variant, out_path):
    c=canvas.Canvas(out_path,pagesize=landscape(A4))
    W,H=landscape(A4)
    draw_front(c,W,H,variant); c.showPage()
    for name,start,end in months_13:
        draw_month(c,W,H,variant,name,start,end); c.showPage()
    draw_information(c,W,H)
    draw_reference(c,W,H)
    draw_year_day(c,W,H)
    c.save()
    print(f"Saved: {out_path}")

# ======================================================================
#                          INGRESS PAGE (3 columns)
# ======================================================================

# Glyphs for ingresses
Z = {
    "Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋",
    "Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏",
    "Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓",
}

# 2026 ingress data (dates only), as provided
INGRESSES_DATA = {
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
        ("Dec 04","Scorpio"),  # re-entry after retro
    ],
    "Mars":[
        ("Jan 23","Aquarius"), ("Mar 02","Pisces"), ("Apr 09","Aries"),
        ("May 18","Taurus"), ("Jun 28","Gemini"), ("Aug 11","Cancer"),
        ("Sep 28","Leo"), ("Nov 25","Virgo"),
    ],
    "Jupiter":[ ("Jun 30","Leo") ],
    "Saturn":[ ("Feb 14","Aries") ],
    "Uranus":[ ("Apr 26","Gemini") ],
    "Neptune":[ ("Jan 26","Aries") ],
    "Pluto":[ ],  # no sign change in 2026
}

INNER_PLANETS = ["Mercury","Venus","Mars","Jupiter"]
OUTER_PLANETS = ["Saturn","Uranus","Neptune","Pluto"]

def _format_ingress_line(date_str, sign):
    return f"{date_str} → {sign} {Z[sign]}"

def build_ingresses_pdf(out_path="ingresses_2026.pdf"):
    c = canvas.Canvas(out_path, pagesize=landscape(A4))
    W, H = landscape(A4)

    # background
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)

    # title
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD, 28)
    c.drawCentredString(W/2, H-2.2*cm, "Planet Ingresses · 2026 (dates only)")

    # three balanced columns
    margin_l, margin_r = 2.0*cm, 2.0*cm
    gutter = 1.2*cm
    content_w = W - margin_l - margin_r
    col_w = (content_w - 2*gutter) / 3.0
    x_cols = [margin_l + i*(col_w+gutter) for i in range(3)]
    top_y = H - 3.2*cm
    line_h = 0.55*cm

    # we’ll split groups across 3 columns:
    groups = [
        ("Inner / Action", INNER_PLANETS),
        ("Outer Planets", OUTER_PLANETS),
    ]

    col_idx = 0
    y = top_y

    def new_col(idx):
        return x_cols[idx], top_y

    def draw_group(title, planets, x, y_start):
        c.setFont(FONT_BOLD, 14); c.drawString(x, y_start, title)
        y = y_start - 0.7*cm
        for p in planets:
            c.setFont(FONT_BOLD, 12); c.drawString(x, y, p); y -= 0.5*cm
            rows = INGRESSES_DATA.get(p, [])
            c.setFont(FONT_REG, 11)
            if not rows:
                c.drawString(x, y, "—"); y -= line_h
            else:
                for (d, sign) in rows:
                    c.drawString(x, y, _format_ingress_line(d, sign))
                    y -= line_h
            y -= 0.2*cm  # small spacer between planets
        return y - 0.4*cm

    for title, planets in groups:
        # If the remaining vertical space in this column is too small, jump to next column
        x = x_cols[col_idx]
        y = draw_group(title, planets, x, y)
        # move to next column after each group to keep balance
        col_idx += 1
        if col_idx >= 3:
            col_idx = 0
            x, y = new_col(col_idx)
        else:
            x, y = new_col(col_idx)

    c.showPage()
    c.save()
    print(f"Saved: {out_path}")

# ---------------- CLI ----------------
if __name__=="__main__":
    ap = argparse.ArgumentParser()
    mx = ap.add_mutually_exclusive_group(required=True)
    mx.add_argument("--variant", choices=["core","deluxe","neon"], help="Build a 13-month calendar PDF in the chosen palette.")
    mx.add_argument("--ingresses", help="Build a single-page Planet Ingresses 2026 PDF at this path.")
    ap.add_argument("--out", help="Output PDF path for calendar variant.")
    args = ap.parse_args()

    if args.variant:
        if not args.out:
            raise SystemExit("--out is required when --variant is used.")
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        build_calendar(args.variant, args.out)
    else:
        # ingresses
        out_path = args.ingresses
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        build_ingresses_pdf(out_path)
