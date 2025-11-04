# calendar12.py
# 2026 · 12-Month Calendar · A4 landscape · variants: core|deluxe|neon
# Matches visual language of your 13-month build. True Gregorian dates.

import os, math, datetime as dt
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
import calendar as pycal

OSLO = ZoneInfo("Europe/Oslo"); UTC = ZoneInfo("UTC")

# ----- fonts -----
FONT_REG  = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
def _try_font(name, paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p)); return True
    return False
if not _try_font(FONT_REG, ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/TTF/DejaVuSans.ttf","DejaVuSans.ttf"]):
    FONT_REG = "Helvetica"
if not _try_font(FONT_BOLD, ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/TTF/DejaVuSans-Bold.ttf","DejaVuSans-Bold.ttf"]):
    FONT_BOLD = "Helvetica-Bold"

# ----- palettes (same semantics as your 13-month) -----
PALETTES = {
    "core": {
        "Jan": colors.Color(0.75,0.85,1.00), "Feb": colors.Color(0.75,0.85,1.00),
        "Mar": colors.Color(1.00,0.85,0.95), "Apr": colors.Color(1.00,0.85,0.95), "May": colors.Color(1.00,0.85,0.95),
        "Jun": colors.Color(1.00,0.93,0.70), "Jul": colors.Color(1.00,0.93,0.70), "Aug": colors.Color(1.00,0.93,0.70),
        "Sep": colors.Color(0.45,0.30,0.45), "Oct": colors.Color(0.45,0.30,0.45), "Nov": colors.Color(0.45,0.30,0.45),
        "Dec": colors.Color(0.75,0.85,1.00),
    },
    "deluxe": {
        "Jan": colors.white, "Feb": colors.white,
        "Mar": colors.Color(0.96,0.80,0.20), "Apr": colors.Color(0.96,0.80,0.20), "May": colors.Color(0.96,0.80,0.20),
        "Jun": colors.black, "Jul": colors.black, "Aug": colors.black,
        "Sep": colors.Color(0.82,0.84,0.86), "Oct": colors.Color(0.82,0.84,0.86), "Nov": colors.Color(0.82,0.84,0.86),
        "Dec": colors.white,
    },
    "neon": {
        "Jan": colors.Color(1.00,0.82,0.12), "Feb": colors.Color(1.00,0.82,0.12),
        "Mar": colors.Color(1.00,0.60,0.85), "Apr": colors.Color(1.00,0.60,0.85), "May": colors.Color(1.00,0.60,0.85),
        "Jun": colors.Color(0.10,0.95,0.35), "Jul": colors.Color(0.10,0.95,0.35), "Aug": colors.Color(0.10,0.95,0.35),
        "Sep": colors.Color(0.20,0.55,1.00), "Oct": colors.Color(0.20,0.55,1.00), "Nov": colors.Color(0.20,0.55,1.00),
        "Dec": colors.Color(1.00,0.82,0.12),
    },
}

def _season(m):  # month index 1..12
    if m in (12,1,2): return "Winter"
    if m in (3,4,5):  return "Spring"
    if m in (6,7,8):  return "Summer"
    return "Autumn"

def text_color(variant, m):
    if variant=="core"   and _season(m)=="Autumn": return colors.white
    if variant=="deluxe" and _season(m)=="Summer": return colors.white
    return colors.black

def border_color(variant, m):
    if variant=="deluxe": return colors.black if _season(m) in ("Winter","Spring","Autumn") else colors.white
    if variant=="neon":   return colors.black
    return colors.white

# ----- symbols / data (reuse your sets) -----
zodiac_glyph  = {"Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓"}
zodiac_order  = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
month_symbols = {"Jan":"✶","Feb":"♥","Mar":"❀","Apr":"✿","May":"❧","Jun":"✢","Jul":"✺","Aug":"✸","Sep":"❦","Oct":"❁","Nov":"✦","Dec":"✳"}

# Your original event tables can be imported; for brevity we copy minimal hooks and expect you to import from the 13-month file if you prefer.
full_moons = {
    dt.date(2026,1,3):"Cancer", dt.date(2026,2,1):"Leo", dt.date(2026,3,3):"Virgo", dt.date(2026,4,2):"Libra",
    dt.date(2026,5,1):"Scorpio", dt.date(2026,5,31):"Sagittarius", dt.date(2026,6,29):"Capricorn",
    dt.date(2026,7,29):"Aquarius", dt.date(2026,8,28):"Pisces", dt.date(2026,9,26):"Aries",
    dt.date(2026,10,26):"Taurus", dt.date(2026,11,24):"Gemini", dt.date(2026,12,24):"Cancer",
}
new_moons = {
    dt.date(2026,1,18):"Capricorn", dt.date(2026,2,17):"Aquarius", dt.date(2026,3,19):"Pisces", dt.date(2026,4,17):"Aries",
    dt.date(2026,5,16):"Taurus", dt.date(2026,6,15):"Gemini", dt.date(2026,7,14):"Cancer", dt.date(2026,8,12):"Leo",
    dt.date(2026,9,11):"Virgo", dt.date(2026,10,10):"Libra", dt.date(2026,11,9):"Scorpio", dt.date(2026,12,8):"Sagittarius",
}
sun_ingress = {
    dt.date(2026,1,20):"Aquarius", dt.date(2026,2,18):"Pisces", dt.date(2026,3,20):"Aries", dt.date(2026,4,20):"Taurus",
    dt.date(2026,5,21):"Gemini", dt.date(2026,6,21):"Cancer", dt.date(2026,7,22):"Leo", dt.date(2026,8,23):"Virgo",
    dt.date(2026,9,23):"Libra",   dt.date(2026,10,23):"Scorpio", dt.date(2026,11,22):"Sagittarius", dt.date(2026,12,21):"Capricorn",
}
eclipses = [(dt.date(2026,2,17),"Solar"),(dt.date(2026,3,3),"Lunar"),(dt.date(2026,8,12),"Solar"),(dt.date(2026,8,28),"Lunar")]
GLOBAL_HOLIDAYS = {dt.date(2026,4,5):"Easter Sunday ★", dt.date(2026,10,31):"Halloween ★", dt.date(2026,12,25):"Christmas Day ★"}

def meteor_labels_for_date(d):
    windows=[(dt.date(2026,1,2),dt.date(2026,1,3),"Quadrantids peak window"),
             (dt.date(2026,4,21),dt.date(2026,4,22),"Lyrids peak window"),
             (dt.date(2026,7,28),dt.date(2026,7,29),"Delta Aquarids peak window"),
             (dt.date(2026,8,12),dt.date(2026,8,13),"Perseids peak window"),
             (dt.date(2026,10,21),dt.date(2026,10,22),"Orionids peak window"),
             (dt.date(2026,11,4),dt.date(2026,11,5),"Taurids peak window"),
             (dt.date(2026,11,17),dt.date(2026,11,18),"Leonids peak window"),
             (dt.date(2026,12,13),dt.date(2026,12,14),"Geminids peak window"),
             (dt.date(2026,12,21),dt.date(2026,12,22),"Ursids peak window")]
    return [lbl for a,b,lbl in windows if a<=d<=b]

def moon_sign_for_day(d):
    local = dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC)
    e = ephem.Ecliptic(ephem.Moon(local))
    lon = (float(e.lon)*180.0/math.pi)%360.0
    return zodiac_order[int(lon//30)]

# Simple planet ingress detector reused from your 13-month, daily step:
PLANETS = {"Mercury":ephem.Mercury,"Venus":ephem.Venus,"Mars":ephem.Mars,"Jupiter":ephem.Jupiter,"Saturn":ephem.Saturn,"Uranus":ephem.Uranus,"Neptune":ephem.Neptune,"Pluto":ephem.Pluto}
def _sidx(body_ctor,t)->int:
    e=ephem.Ecliptic(body_ctor(t)); lon=(float(e.lon)*180.0/math.pi)%360.0; return int(lon//30)
def _ing(body_ctor,year):
    out=[]; d=dt.date(year,1,1); end=dt.date(year,12,31)
    prev=_sidx(body_ctor, dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC))
    while d<=end:
        idx=_sidx(body_ctor, dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC))
        if idx!=prev: out.append((d,zodiac_order[idx])); prev=idx
        d+=dt.timedelta(days=1)
    return out
ingresses={p:_ing(ctor,2026) for p,ctor in PLANETS.items()}
planet_ingress_by_date={}
for p,items in ingresses.items():
    for d,sign in items:
        planet_ingress_by_date.setdefault(d,[]).append(f"{p} → {sign} {zodiac_glyph[sign]}")

# Mercury retrograde coarse detector (daily noon)
def _elon(body_ctor,t):
    e=ephem.Ecliptic(body_ctor(t)); return (float(e.lon)*180.0/math.pi)%360.0
def mercury_retrograde_periods(year):
    start=dt.date(year,1,1); end=dt.date(year,12,31)
    prev=_elon(ephem.Mercury, dt.datetime(start.year,start.month,start.day,12,0,tzinfo=OSLO).astimezone(UTC))
    inR=False; res=[]; Rs=None; d=start+dt.timedelta(days=1)
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

# ----- text helpers -----
def wrap_to_width(text,font,size,max_w):
    words=text.split(" "); lines=[]; cur=""
    for w in words:
        t=w if not cur else f"{cur} {w}"
        if cur and stringWidth(t,font,size)>max_w:
            lines.append(cur); cur=w
        else:
            cur=t
    if cur: lines.append(cur)
    return lines
def first_wrapped_line(text, font_name, font_size, max_w):
    w = wrap_to_width(text, font_name, font_size, max_w)
    return w[0].rstrip(" ,.;:·") if w else ""

# ----- month page -----
def draw_month(c, W, H, variant, year, month):
    mon_tag = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][month-1]
    bg = PALETTES[variant][mon_tag]
    c.setFillColor(bg); c.rect(0,0,W,H,fill=True,stroke=False)

    fg = text_color(variant, month)
    c.setFillColor(fg); c.setFont(FONT_BOLD,26)
    c.drawCentredString(W/2, H-1.6*cm, f"{month_symbols[mon_tag]} {dt.date(year,month,1).strftime('%B %Y')}")

    # layout
    lm,rm,tm,bm = 1.8*cm,1.8*cm,3.0*cm,2.3*cm
    left,top=lm,H-tm; cols,rows=7,6  # up to 6 rows for Gregorian months
    cw=(W-lm-rm)/cols; ch=(H-tm-bm)/rows; pad=0.22*cm

    # weekday headers
    c.setFont(FONT_BOLD,11)
    for i,wdn in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        c.drawCentredString(left+cw*(i+0.5), top+0.42*cm, wdn)

    # compute day matrix starting Monday
    first_weekday, ndays = pycal.monthrange(year, month)  # 0=Mon in Python? Actually 0=Mon? In Python: 0=Mon yes.
    # monthrange: 0=Mon..6=Sun, good.
    d1_col = first_weekday
    day = 1
    for r in range(rows):
        for col in range(cols):
            idx = r*7 + col
            in_month = (idx >= d1_col) and (day <= ndays)
            x=left+col*cw; y=top-(r+1)*ch
            c.setStrokeColor(border_color(variant, month)); c.rect(x,y,cw,ch)
            if not in_month: continue

            d = dt.date(year, month, day)
            c.setFillColor(fg)
            # mini Gregorian date
            c.setFont(FONT_BOLD, 7.2); c.drawString(x+pad, y+ch-0.36*cm, d.strftime("%b %d"))

            # build stacked lines
            stack_start = y + ch*0.72
            line_gap    = 0.24*cm
            safe_floor  = y + 0.92*cm
            usable_w    = cw - 2*pad

            lines=[]
            ms = moon_sign_for_day(d); mg = zodiac_glyph[ms]
            lines.append(f"Moon in {ms} {mg}")
            if d in new_moons:  lines.append("○ New Moon")
            if d in full_moons: lines.append("● Full Moon")
            if d in sun_ingress:
                s = sun_ingress[d]; lines.append(f"Sun → {s} {zodiac_glyph[s]}")
            for ed,kind in eclipses:
                if d==ed:
                    if kind == "Lunar":
                        lines.append(f"Lunar Eclipse {mg}")
                    else:
                        sdt  = dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC)
                        slon = (float(ephem.Ecliptic(ephem.Sun(sdt)).lon)*180.0/math.pi)%360.0
                        ssign = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"][int(slon//30)]
                        lines.append(f"Solar Eclipse {zodiac_glyph[ssign]}")
                    break
            if d in GLOBAL_HOLIDAYS: lines.append(GLOBAL_HOLIDAYS[d])
            if d in planet_ingress_by_date:
                compact = " · ".join(planet_ingress_by_date[d])
                first = first_wrapped_line(compact, FONT_BOLD, 7.0, usable_w)
                if first: lines.append(first)
            if d in retro_markers:
                txt = " · ".join(retro_markers[d])
                first = first_wrapped_line(txt, FONT_BOLD, 7.0, usable_w)
                if first: lines.append(first)
            for lbl in meteor_labels_for_date(d): lines.append(lbl)

            # draw stack
            y_line = stack_start
            for txt in lines:
                if y_line < safe_floor:
                    c.setFont(FONT_BOLD, 7.0); c.drawString(x + pad, y_line, "…")
                    break
                size = 7.0
                if stringWidth(txt, FONT_BOLD, size) > usable_w:
                    w0 = wrap_to_width(txt, FONT_BOLD, size, usable_w)
                    if w0: txt = w0[0].rstrip(" ,.;:·")
                c.setFont(FONT_BOLD, size); c.drawString(x + pad, y_line, txt)
                y_line -= line_gap

            # big day number bottom-right-ish for 12-month
            c.setFont(FONT_BOLD, 14); c.drawRightString(x+cw-0.18*cm, y+0.28*cm, str(day))
            day += 1

def draw_front(c,W,H,variant):
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD, 40); c.drawCentredString(W/2, H - 6*cm, "The 12-Month Calendar of 2026")
    c.setFont(FONT_REG, 19);  c.drawCentredString(W/2, H - 8*cm, "Gregorian months · astrological overlays")
    c.setFont(FONT_REG, 12);  c.drawCentredString(W/2, H - 11.0*cm, {"core":"Seasonal palette","deluxe":"Deluxe palette","neon":"Color Pop palette"}[variant])
    c.setFont(FONT_BOLD, 24)
    c.drawCentredString(W/2, H - 12.6*cm, "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓")
    m = 2.0*cm; c.setLineWidth(2); c.setStrokeColor(colors.Color(0,0,0,0.12)); c.roundRect(m,m,W-2*m,H-2*m,14,stroke=True,fill=False)

def build_calendar12(variant, out_path):
    c=canvas.Canvas(out_path,pagesize=landscape(A4))
    W,H=landscape(A4)
    draw_front(c,W,H,variant); c.showPage()
    for m in range(1,13):
        draw_month(c,W,H,variant,2026,m); c.showPage()
    # simple info sheet reuse
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)
    c.setFillColor(colors.black); c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,"Information")
    c.setFont(FONT_REG,11); c.drawCentredString(W/2,1.3*cm,"© 2026 Serene. All rights reserved.")
    c.showPage(); c.save()
    print(f"Saved: {out_path}")

if __name__=="__main__":
    import argparse, pathlib
    ap=argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["core","deluxe","neon"], required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    build_calendar12(args.variant, args.out)
