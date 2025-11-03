# serene_13month_palettes_2026.py
# Builds THREE 13-month calendars for 2026 with different color palettes:
#   - core  (Winter blue, Spring pink, Summer gold, Autumn plum; Autumn text=white)
#   - deluxe (WGBS = Winter white, Spring gold, Summer black, Autumn silver; auto-contrast)
#   - colorpop (Neon: pink/blue/yellow/green; auto-contrast)
#
# Outputs (in ~/serene-site/downloads/13):
#   core-2026-v1.pdf
#   deluxe-2026-wgbs-v1.pdf
#   colorpop-2026-v1.pdf

import os, math, random, datetime as dt
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

# ---------- Fonts ----------
FONT_REG = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
def _reg(name, paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
            return True
    return False

if not _reg(FONT_REG, [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/local/share/fonts/DejaVuSans.ttf",
    "DejaVuSans.ttf"
]):
    FONT_REG = "Helvetica"
if not _reg(FONT_BOLD, [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf"
]):
    FONT_BOLD = "Helvetica-Bold"

# ---------- 13-month model (Thursday-start, 28-day months + Year Day) ----------
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

# Day28 index mapping
mapping = {}
for name, start, end in months_13:
    n = 1
    for d in rrule(DAILY, dtstart=start, until=end):
        mapping[d.date()] = {"MonthName": name, "Day28": n}
        n += 1

# ---------- Glyphs & symbols ----------
month_symbols = {"January":"✶","February":"♥","March":"❀","April":"✿","May":"❧","June":"✢","July":"✺","Sunny":"✾","August":"✸","September":"❦","October":"❁","November":"✦","December":"✳"}
zodiac_glyph = {"Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓"}
zodiac_order = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# ---------- Event tables (from your locked fixes) ----------
full_moons = {
    dt.date(2026,1,3):"Cancer", dt.date(2026,2,1):"Leo", dt.date(2026,3,3):"Virgo",
    dt.date(2026,4,2):"Libra",  dt.date(2026,5,1):"Scorpio", dt.date(2026,5,31):"Sagittarius",
    dt.date(2026,6,29):"Capricorn", dt.date(2026,7,29):"Aquarius",
    dt.date(2026,8,28):"Pisces", dt.date(2026,9,26):"Aries",
    dt.date(2026,10,25):"Taurus", dt.date(2026,11,24):"Gemini", dt.date(2026,12,24):"Cancer",
}
new_moons = {
    dt.date(2026,1,18):"Capricorn", dt.date(2026,2,17):"Aquarius", dt.date(2026,3,19):"Pisces",
    dt.date(2026,4,17):"Aries",     dt.date(2026,5,16):"Taurus",   dt.date(2026,6,15):"Gemini",
    dt.date(2026,7,14):"Cancer",    dt.date(2026,8,12):"Leo",      dt.date(2026,9,11):"Virgo",
    dt.date(2026,10,10):"Libra",    dt.date(2026,11,9):"Scorpio",  dt.date(2026,12,8):"Sagittarius",
}
sun_ingress = {
    dt.date(2026,1,20):"Aquarius", dt.date(2026,2,18):"Pisces", dt.date(2026,3,20):"Aries",
    dt.date(2026,4,20):"Taurus",   dt.date(2026,5,21):"Gemini", dt.date(2026,6,21):"Cancer",
    dt.date(2026,7,22):"Leo",      dt.date(2026,8,23):"Virgo",  dt.date(2026,9,23):"Libra",
    dt.date(2026,10,23):"Scorpio", dt.date(2026,11,22):"Sagittarius", dt.date(2026,12,21):"Capricorn",
}
GLOBAL_HOLIDAYS = {dt.date(2026,4,5):"Easter Sunday ★", dt.date(2026,10,31):"Halloween ★", dt.date(2026,12,25):"Christmas Day ★"}
METEOR_WINDOWS = [
    (dt.date(2026,1,2), dt.date(2026,1,3), "Quadrantids peak window"),
    (dt.date(2026,4,21),dt.date(2026,4,22),"Lyrids peak window"),
    (dt.date(2026,7,28),dt.date(2026,7,29),"Delta Aquarids peak window"),
    (dt.date(2026,8,12),dt.date(2026,8,13),"Perseids peak window"),
    (dt.date(2026,10,21),dt.date(2026,10,22),"Orionids peak window"),
    (dt.date(2026,11,4),dt.date(2026,11,5),"Taurids peak window"),
    (dt.date(2026,11,17),dt.date(2026,11,18),"Leonids peak window"),
    (dt.date(2026,12,13),dt.date(2026,12,14),"Geminids peak window"),
    (dt.date(2026,12,21),dt.date(2026,12,22),"Ursids peak window"),
]
def meteor_labels_for_date(d):
    return [label for a,b,label in METEOR_WINDOWS if a<=d<=b]
season_markers = {dt.date(2026,3,20):"Spring Equinox", dt.date(2026,6,21):"Summer Solstice", dt.date(2026,9,23):"Autumn Equinox", dt.date(2026,12,21):"Winter Solstice"}

OSLO = ZoneInfo("Europe/Oslo"); UTC = ZoneInfo("UTC")

def moon_sign_for_day(d: dt.date)->str:
    if d == dt.date(2026,8,27): return "Pisces"
    local = dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC)
    e = ephem.Ecliptic(ephem.Moon(local))
    lon = (float(e.lon)*180.0/math.pi)%360.0
    return zodiac_order[int(lon//30)]

PLANETS={"Mercury":ephem.Mercury,"Venus":ephem.Venus,"Mars":ephem.Mars,"Jupiter":ephem.Jupiter,"Saturn":ephem.Saturn,"Uranus":ephem.Uranus,"Neptune":ephem.Neptune,"Pluto":ephem.Pluto}
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

def _elon(body_ctor,t):
    e=ephem.Ecliptic(body_ctor(t)); return (float(e.lon)*180.0/math.pi)%360.0
def mercury_retrograde_periods(year):
    start=dt.date(year,1,1); end=dt.date(year,12,31)
    prev=_elon(ephem.Mercury, dt.datetime(start.year,start.month,start.day,12,0,tzinfo=OSLO).astimezone(UTC))
    d=start+dt.timedelta(days=1); inR=False; Rs=None; res=[]
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
eclipses=[(dt.date(2026,2,17),"Solar"),(dt.date(2026,3,3),"Lunar"),(dt.date(2026,8,12),"Solar"),(dt.date(2026,8,28),"Lunar")]

# ---------- Helpers ----------
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

def first_wrapped_line(text, font_name, font_size, max_w):
    wrapped = wrap_to_width(text, font_name, font_size, max_w)
    if not wrapped: return ""
    return wrapped[0].rstrip(" ,.;:·")

# Luminance for auto contrast (simple)
def _lum(c: colors.Color):
    # approximate relative luminance from RGB 0..1
    return 0.2126*c.red + 0.7152*c.green + 0.0722*c.blue

# ---------- Palettes ----------
PALETTES = {
    "core": {  # your seasonal pastels
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
        "force_white_months": {"September","October","November"},  # white text
    },
    "deluxe": {  # White / Gold / Black / Silver
        "January": colors.white,       # Winter = white
        "February": colors.white,
        "March": colors.Color(0.90,0.78,0.30),  # Spring = gold
        "April": colors.Color(0.90,0.78,0.30),
        "May": colors.Color(0.90,0.78,0.30),
        "June": colors.black,          # Summer = black
        "July": colors.black,
        "Sunny": colors.black,
        "August": colors.black,
        "September": colors.Color(0.78,0.78,0.80),  # Autumn = silver
        "October":  colors.Color(0.78,0.78,0.80),
        "November": colors.Color(0.78,0.78,0.80),
        "December": colors.white,
        "force_white_months": set(),   # auto-contrast handles text
    },
    "colorpop": {  # Neon-ish: pink / blue / yellow / green
        "January": colors.Color(1.00,0.40,0.75),  # pink
        "February": colors.Color(1.00,0.40,0.75),
        "March": colors.Color(0.20,0.55,1.00),    # blue
        "April": colors.Color(0.20,0.55,1.00),
        "May": colors.Color(0.20,0.55,1.00),
        "June": colors.Color(1.00,0.95,0.25),     # yellow
        "July": colors.Color(1.00,0.95,0.25),
        "Sunny": colors.Color(1.00,0.95,0.25),
        "August": colors.Color(1.00,0.95,0.25),
        "September": colors.Color(0.20,0.85,0.40), # green
        "October":  colors.Color(0.20,0.85,0.40),
        "November": colors.Color(0.20,0.85,0.40),
        "December": colors.Color(1.00,0.40,0.75),
        "force_white_months": set(),   # auto-contrast handles text
    }
}

# ---------- Drawing ----------
THU_COL=3
def draw_month(c, name, start, end, bg_color, force_white=False):
    W,H=landscape(A4)
    c.setFillColor(bg_color); c.rect(0,0,W,H,fill=True,stroke=False)

    # text color: force white if requested, else choose by luminance
    if force_white:
        fg = colors.white
    else:
        fg = colors.white if _lum(bg_color)<0.45 else colors.black

    sym=month_symbols.get(name,"")
    c.setFillColor(fg); c.setFont(FONT_BOLD,26)
    c.drawCentredString(W/2,H-1.6*cm,f"{sym+' ' if sym else ''}{name} 2026")

    lm,rm,tm,bm=1.8*cm,1.8*cm,3.0*cm,2.3*cm
    left,top=lm,H-tm; cols,rows=7,5
    cw=(W-lm-rm)/cols; ch=(H-tm-bm)/rows; pad=0.23*cm

    # weekday headers: **always black** per your rule
    c.setFont(FONT_BOLD,12); c.setFillColor(colors.black)
    for i,wd in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        c.drawCentredString(left+cw*(i+0.5),top+0.45*cm,wd)

    dates=[d.date() for d in rrule(DAILY,dtstart=start,until=end)]
    for d in dates:
        day28=mapping[d]["Day28"]; col=(THU_COL+(day28-1))%7; r=(THU_COL+(day28-1))//7
        x=left+col*cw; y=top-(r+1)*ch
        c.setStrokeColor(colors.white); c.rect(x,y,cw,ch)  # keep subtle border

        c.setFillColor(fg)
        date_y=y+ch-0.50*cm
        stack_start=y+ch*0.63
        line_gap=0.28*cm
        safe_floor=y+0.92*cm
        usable_w=cw-2*pad

        lines=[]

        if d==dt.date(2026,8,27):
            lines.append("Moon in Pisces ♓")
        else:
            ms=moon_sign_for_day(d); mg=zodiac_glyph[ms]
            lines.append(f"Moon in {ms} {mg}")
            if d in new_moons:  lines.append("○ New Moon")
            if d in full_moons: lines.append("● Full Moon")
            if d in sun_ingress:
                s=sun_ingress[d]; lines.append(f"Sun → {s} {zodiac_glyph[s]}")
            for ed,kind in eclipses:
                if d==ed:
                    if kind=="Lunar": lines.append(f"Lunar Eclipse {mg}")
                    else:
                        sdt=dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC)
                        slon=(float(ephem.Ecliptic(ephem.Sun(sdt)).lon)*180.0/math.pi)%360.0
                        ssign=zodiac_order[int(slon//30)]
                        lines.append(f"Solar Eclipse {zodiac_glyph[ssign]}")
                    break
        if d in season_markers:  lines.append(season_markers[d])
        if d in GLOBAL_HOLIDAYS: lines.append(GLOBAL_HOLIDAYS[d])
        if d in planet_ingress_by_date:
            compact = " · ".join(planet_ingress_by_date[d])
            first   = first_wrapped_line(compact, FONT_BOLD, 7.2, usable_w)
            if first: lines.append(first)
        if d in retro_markers:
            txt   = " · ".join(retro_markers[d])
            first = first_wrapped_line(txt, FONT_BOLD, 7.2, usable_w)
            if first: lines.append(first)
        for lbl in meteor_labels_for_date(d): lines.append(lbl)

        c.setFont(FONT_BOLD,8.6); c.drawString(x+pad,date_y,d.strftime("%b %d"))
        y_line=stack_start; base=7.2; max_lines=max(0,int((stack_start-safe_floor)//line_gap)); drawn=0
        for txt in lines:
            if drawn>=max_lines:
                if y_line-line_gap>=safe_floor:
                    c.setFont(FONT_BOLD,base); c.drawString(x+pad,y_line-line_gap,"…")
                break
            size=base
            while stringWidth(txt,FONT_BOLD,size)>usable_w and size>6.7: size-=0.2
            if stringWidth(txt,FONT_BOLD,size)>usable_w:
                w0=wrap_to_width(txt,FONT_BOLD,size,usable_w)
                if w0: txt=w0[0].rstrip(" ,.;:·")
            c.setFont(FONT_BOLD,size); c.drawString(x+pad,y_line,txt)
            y_line-=line_gap; drawn+=1

        c.setFont(FONT_BOLD,18); c.setFillColor(fg); c.drawCentredString(x+cw/2,y+0.28*cm,str(day28))

def build_pdf(palette_name, out_path):
    pal = PALETTES[palette_name]
    force_white = pal.get("force_white_months", set())

    c = canvas.Canvas(out_path, pagesize=landscape(A4))
    # Front
    W,H=landscape(A4)
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)
    c.setFont(FONT_BOLD,34); c.setFillColor(colors.black)
    c.drawCentredString(W/2,H-6.2*cm,f"The 13-Month Calendar of 2026 — {palette_name.capitalize()}")
    c.setFont(FONT_REG,16); c.drawCentredString(W/2,H-8.0*cm,"28 Days · 13 Months · Year Day")
    c.setFont(FONT_REG,12); c.drawCentredString(W/2,H-9.4*cm,"Seasonal palette variant")
    c.showPage()

    # Months
    for name,start,end in months_13:
        bg = pal[name]
        draw_month(c,name,start,end,bg,force_white=(name in force_white))

    # Info
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,"Information")
    y=H-4.5*cm; left=3*cm
    c.setFont(FONT_BOLD,12); c.drawString(left,y,"Source"); y-=0.55*cm
    c.setFont(FONT_REG,11); c.drawString(left,y,"mooncalendar.astro-seek.com")
    c.showPage()

    # Year Day
    random.seed(2026)
    c.setFillColor(colors.Color(1,1,1)); c.rect(0,0,W,H,fill=True,stroke=False)
    c.setFillColor(colors.Color(0,0,0,alpha=0.08))
    for _ in range(160):
        x=random.uniform(1.0*cm,W-1.0*cm); y2=random.uniform(2.0*cm,H-2.0*cm); r=random.uniform(0.25,0.8)
        c.circle(x,y2,r,fill=1,stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD,28); c.drawCentredString(W/2,H-3*cm,"Year Day · New Year’s")
    c.setFont(FONT_REG,10); c.drawCentredString(W/2,1.4*cm,"© 2026 Serene. All rights reserved.")
    c.showPage()

    c.save()
    print("Saved:", out_path)

if __name__=="__main__":
    base = os.path.expanduser("~/serene-site/downloads/13")
    os.makedirs(base, exist_ok=True)
    build_pdf("core",     os.path.join(base, "core-2026-v1.pdf"))
    build_pdf("deluxe",   os.path.join(base, "deluxe-2026-wgbs-v1.pdf"))
    build_pdf("colorpop", os.path.join(base, "colorpop-2026-v1.pdf"))
