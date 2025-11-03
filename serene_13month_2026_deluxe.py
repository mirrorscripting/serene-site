#!/usr/bin/env python3
"""
SERENE 13-MONTH CALENDAR 2026 — DELUXE EDITION
Thursday-Start • Autumn White • Auto Moons • Cosmic Events
Made with love by YOU + Grok
"""

import os
import math
import random
import datetime as dt
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

print("Building Serene 13-Month Calendar 2026 — Deluxe Edition...", flush=True)

# ========================================
# 1. FONT SETUP
# ========================================
FONT_NAME = "DejaVuSans"
font_paths = [
 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
 "/usr/share/fonts/TTF/DejaVuSans.ttf",
 "DejaVuSans.ttf",
]
for path in font_paths:
 if os.path.exists(path):
 pdfmetrics.registerFont(TTFont(FONT_NAME, path))
 print(f"Font loaded: {path}")
 break
else:
 FONT_NAME = "Helvetica"
 print("Using fallback font: Helvetica")

# ========================================
# 2. 13-MONTH LAYOUT (2026)
# ========================================
months_13 = [
 ("January", dt.date(2026,1,1), dt.date(2026,1,28)),
 ("February", dt.date(2026,1,29), dt.date(2026,2,25)),
 ("March", dt.date(2026,2,26), dt.date(2026,3,25)),
 ("April", dt.date(2026,3,26), dt.date(2026,4,22)),
 ("May", dt.date(2026,4,23), dt.date(2026,5,20)),
 ("June", dt.date(2026,5,21), dt.date(2026,6,17)),
 ("July", dt.date(2026,6,18), dt.date(2026,7,15)),
 ("Sunny", dt.date(2026,7,16), dt.date(2026,8,12)),
 ("August", dt.date(2026,8,13), dt.date(2026,9,9)),
 ("September", dt.date(2026,9,10), dt.date(2026,10,7)),
 ("October", dt.date(2026,10,8), dt.date(2026,11,4)),
 ("November", dt.date(2026,11,5), dt.date(2026,12,2)),
 ("December", dt.date(2026,12,3), dt.date(2026,12,30)),
]
YEAR_DAY = dt.date(2026, 12, 31)

mapping = {}
for name, start, end in months_13:
 n = 1
 for d in rrule(DAILY, dtstart=start, until=end):
 mapping[d.date()] = {"MonthName": name, "Day28": n}
 n += 1

# ========================================
# 3. COLORS & SYMBOLS
# ========================================
season_colors = {
 "Winter": colors.Color(0.75, 0.85, 1.00),
 "Spring": colors.Color(1.00, 0.85, 0.95),
 "Summer": colors.Color(1.00, 0.93, 0.70),
 "Fall": colors.Color(0.45, 0.30, 0.45),
}
month_color_map = {
 "January": season_colors["Winter"], "February": season_colors["Winter"],
 "March": season_colors["Spring"], "April": season_colors["Spring"], "May": season_colors["Spring"],
 "June": season_colors["Summer"], "July": season_colors["Summer"],
 "Sunny": season_colors["Summer"], "August": season_colors["Summer"],
 "September": season_colors["Fall"], "October": season_colors["Fall"], "November": season_colors["Fall"],
 "December": season_colors["Winter"],
}

month_symbols = {
 "January": "✶", "February": "♥", "March": "❀", "April": "✿",
 "May": "June": "✢", "July": "✺", "Sunny": "✾",
 "August": "✸", "September": "❦", "October": "❁", "November": "✦", "December": "✳",
}

zodiac_glyph = {
 "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
 "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
 "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}
zodiac_order = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# ========================================
# 4. ASTRONOMY (Auto Moons, Ingress, Retro)
# ========================================
OSLO = ZoneInfo("Europe/Oslo")
UTC = ZoneInfo("UTC")

def moon_sign_for_day(date_greg: dt.date) -> str:
 local_dt = dt.datetime(date_greg.year, date_greg.month, date_greg.day, 12, 0, tzinfo=OSLO)
 utc_dt = local_dt.astimezone(UTC)
 m = ephem.Moon(utc_dt)
 e = ephem.Ecliptic(m)
 lon_deg = (float(e.lon) * 180.0 / math.pi) % 360.0
 return zodiac_order[int(lon_deg // 30)]

def compute_moon_phases(year):
 observer = ephem.Observer()
 observer.lat = '59.9139'
 observer.lon = '10.7522'
 observer.elevation = 0
 observer.pressure = 0

 new_moons = {}
 full_moons = {}
 date = dt.datetime(year, 1, 1, 12, 0, tzinfo=UTC)

 for _ in range(15):
 observer.date = date
 try:
 nm = ephem.next_new_moon(observer.date)
 fm = ephem.next_full_moon(observer.date)
 except:
 break
 nm_local = ephem.localtime(observer, nm).date()
 fm_local = ephem.localtime(observer, fm).date()
 if nm_local.year == year:
 new_moons[nm _local] = moon_sign_for_day(nm_local)
 if fm_local.year == year:
 full_moons[fm_local] = moon_sign_for_day(fm_local)
 date = nm + dt.timedelta(days=1)
 return new_moons, full_moons

new_moons, full_moons = compute_moon_phases(2026)

sun_ingress = {
 dt.date(2026,1,20):"Aquarius", dt.date(2026,2,18):"Pisces", dt.date(2026,3,20):"Aries",
 dt.date(2026,4,20):"Taurus", dt.date(2026,5,21):"Gemini", dt.date(2026,6,21):"Cancer",
 dt.date(2026,7,22):"Leo", dt.date(2026,8,23):"Virgo", dt.date(2026,9,23):"Libra",
 dt.date(2026,10,23):"Scorpio", dt.date(2026,11,22):"Sagittarius", dt.date(2026,12,21):"Capricorn",
}

PLANETS = {
 "Mercury": ephem.Mercury, "Venus": ephem.Venus, "Mars": ephem.Mars,
 "Jupiter": ephem.Jupiter, "Saturn": ephem.Saturn,
 "Uranus": ephem.Uranus, "Neptune": ephem.Neptune, "Pluto": ephem.Pluto,
}

def find_ingresses(body_ctor, year):
 out = []
 start = dt.date(year,1,1)
 end = dt.date(year,12,31)
 prev_idx = None
 d = start
 while d <= end:
 local_dt = dt.datetime(d.year, d.month, d.day, 12, 0, tzinfo=OSLO)
 utc_dt = local_dt.astimezone(UTC)
 b = body_ctor(utc_dt)
 e = ephem.Ecliptic(b)
 lon = (float(e.lon) * 180.0 / math.pi) % 360.0
 idx = int(lon // 30)
 if prev_idx is not None and idx != prev_idx:
 out.append((d, zodiac_order[idx]))
 prev_idx = idx
 d += dt.timedelta(days=1)
 return out

planet_ingress_by_date = {}
for pname, ctor in PLANETS.items():
 for d, sign in find_ingresses(ctor, 2026):
 planet_ingress_by_date.setdefault(d, []).append(f"{pname} → {sign} {zodiac_glyph[sign]}")

def mercury_retro_periods(year):
 periods = []
 start = dt.date(year,1,1)
 end = dt.date(year,12,31)
 prev_lon = None
 in_retro = False
 retro_start = None
 d = start
 while d <= end:
 local_dt = dt.datetime(d
