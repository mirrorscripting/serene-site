# 2026 — 12-Month Calendar (v5)
# Updates in v5:
# • Planet Ingresses appendix now auto-paginates (no cut-off for Mars etc.).
# • Full Moons appendix = single vertical list (Jan→Dec), generous spacing.
# • New Moons appendix added (single vertical list).
# • Keeps earlier fixes: raised event stack in month cells, no empty boxes, Autumn text white.

import os, math, calendar, datetime as dt
from zoneinfo import ZoneInfo
import ephem

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------- Output ----------
SITE_DIR = os.path.expanduser("~/serene-site")
OUT_DIR  = os.path.join(SITE_DIR, "downloads", "12")
os.makedirs(OUT_DIR, exist_ok=True)
PDF_PATH = os.path.join(OUT_DIR, "core-2026-v1.pdf")

# ---------- Fonts ----------
FONT_REG  = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
def _reg(name, paths):
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p)); return True
    return False
if not _reg(FONT_REG, ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/TTF/DejaVuSans.ttf","/usr/local/share/fonts/DejaVuSans.ttf","DejaVuSans.ttf"]):
    FONT_REG = "Helvetica"
if not _reg(FONT_BOLD, ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/TTF/DejaVuSans-Bold.ttf","/usr/local/share/fonts/DejaVuSans-Bold.ttf","DejaVuSans-Bold.ttf"]):
    FONT_BOLD = "Helvetica-Bold"

# ---------- Colors ----------
season_colors = {
    "Winter": colors.Color(0.75,0.85,1.00),
    "Spring": colors.Color(1.00,0.85,0.95),
    "Summer": colors.Color(1.00,0.93,0.70),
    "Fall":   colors.Color(0.45,0.30,0.45),
}
month_color_map = {
    1:season_colors["Winter"], 2:season_colors["Winter"], 3:season_colors["Spring"],
    4:season_colors["Spring"], 5:season_colors["Spring"], 6:season_colors["Summer"],
    7:season_colors["Summer"], 8:season_colors["Summer"], 9:season_colors["Fall"],
    10:season_colors["Fall"],  11:season_colors["Fall"], 12:season_colors["Winter"],
}

# ---------- Symbols ----------
month_symbols = {1:"✶",2:"♥",3:"❀",4:"✿",5:"❧",6:"✢",7:"✺",8:"✸",9:"❦",10:"❁",11:"✦",12:"✳"}
zodiac_glyph  = {"Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓"}
zodiac_order  = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# ---------- Phases (your curated dates) ----------
full_moons = {
    dt.date(2026,1,3):"Cancer",
    dt.date(2026,4,2):"Libra",
    dt.date(2026,8,28):"Pisces",
    dt.date(2026,9,26):"Aries",
    dt.date(2026,10,26):"Taurus",
    dt.date(2026,11,24):"Gemini",
    dt.date(2026,12,24):"Cancer",
}
new_moons = {
    dt.date(2026,1,18):"Capricorn",
    dt.date(2026,3,19):"Pisces",
    dt.date(2026,6,15):"Gemini",
    dt.date(2026,8,12):"Leo",
    dt.date(2026,9,11):"Virgo",
    dt.date(2026,10,10):"Libra",
    dt.date(2026,11,9):"Scorpio",
    dt.date(2026,12,9):"Sagittarius",
}

# ---------- Eclipses (grid labels date-only) ----------
eclipses=[(dt.date(2026,8,12),"Solar"),(dt.date(2026,8,28),"Lunar")]

# ---------- Equinoxes / Solstices ----------
season_markers = {
    dt.date(2026,3,20):"Spring Equinox",
    dt.date(2026,6,21):"Summer Solstice",
    dt.date(2026,9,23):"Autumn Equinox",
    dt.date(2026,12,21):"Winter Solstice",
}

# ---------- Holidays ----------
GLOBAL_HOLIDAYS = {
    dt.date(2026,4,5):"Easter Sunday ★",
    dt.date(2026,10,31):"Halloween ★",
    dt.date(2026,12,25):"Christmas Day ★",
}

# ---------- Meteor showers ----------
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

# ---------- TZ ----------
OSLO = ZoneInfo("Europe/Oslo"); UTC = ZoneInfo("UTC")

# ---------- Moon sign (noon local) ----------
def moon_sign_for_day(d: dt.date)->str:
    if d == dt.date(2026,8,27): return "Pisces"
    local = dt.datetime(d.year,d.month,d.day,12,0,tzinfo=OSLO).astimezone(UTC)
    e = ephem.Ecliptic(ephem.Moon(local))
    lon = (float(e.lon)*180.0/math.pi)%360.0
    return zodiac_order[int(lon//30)]

# ---------- Ingresses (dates+times for appendices; grid uses date-only) ----------
def D(y,m,d,hh,mm): return dt.datetime(y,m,d,hh,mm,tzinfo=OSLO)

ingresses_with_times = {
    "Sun":[
        (D(2026,1,20, 1,45),"Aquarius"),
        (D(2026,2,18,15,52),"Pisces"),
        (D(2026,3,20,14,46),"Aries"),
        (D(2026,4,20, 1,39),"Taurus"),
        (D(2026,5,21, 0,37),"Gemini"),
        (D(2026,6,21, 8,25),"Cancer"),
        (D(2026,7,22,19,13),"Leo"),
        (D(2026,8,23, 2,19),"Virgo"),
        (D(2026,9,23, 0, 5),"Libra"),
        (D(2026,10,23, 9,38),"Scorpio"),
        (D(2026,11,22, 7,24),"Sagittarius"),
        (D(2026,12,21,20,50),"Capricorn"),
    ],
    "Mercury":[
        (D(2026,1, 1,21,11),"Capricorn"),
        (D(2026,1,20,16,41),"Aquarius"),
        (D(2026,2, 6,22,48),"Pisces"),
        (D(2026,4,15, 3,22),"Aries"),
        (D(2026,5, 3, 2,57),"Taurus"),
        (D(2026,5,17,10,27),"Gemini"),
        (D(2026,6, 1,11,56),"Cancer"),
        (D(2026,8, 9,16,29),"Leo"),
        (D(2026,8,25,11, 4),"Virgo"),
        (D(2026,9,10,16,21),"Libra"),
        (D(2026,9,30,11,45),"Scorpio"),
        (D(2026,12, 6, 8,34),"Sagittarius"),
        (D(2026,12,25,18,23),"Capricorn"),
    ],
    "Venus":[
        (D(2026,1,17,12,44),"Aquarius"),
        (D(2026,2,10,10,19),"Pisces"),
        (D(2026,3, 6,10,46),"Aries"),
        (D(2026,3,30,16, 1),"Taurus"),
        (D(2026,4,24, 4, 4),"Gemini"),
        (D(2026,5,19, 1, 5),"Cancer"),
        (D(2026,6,13,10,47),"Leo"),
        (D(2026,7, 9,17,22),"Virgo"),
        (D(2026,8, 6,19,13),"Libra"),
        (D(2026,12, 4, 8,13),"Scorpio"),
    ],
    "Mars":[
        (D(2026,1,23, 9,17),"Aquarius"),
        (D(2026,3, 2,14,16),"Pisces"),
        (D(2026,4, 9,19,36),"Aries"),
        (D(2026,5,18,22,26),"Taurus"),
        (D(2026,6,28,19,29),"Gemini"),
        (D(2026,8,11, 8,31),"Cancer"),
        (D(2026,9,28, 2,49),"Leo"),
        (D(2026,11,25,23,37),"Virgo"),
    ],
    "Jupiter":[ (D(2026,6,30, 5,52),"Leo") ],
    "Saturn":[  (D(2026,2,14, 0,12),"Aries") ],
    "Uranus":[  (D(2026,4,26, 0,50),"Gemini") ],
    "Neptune":[ (D(2026,1,26,17,38),"Aries") ],
    "Pluto":[   ],
}

ingress_by_date = {}
for planet, items in ingresses_with_times.items():
    for t, sign in items:
        d = t.date()
        ingress_by_date.setdefault(d, []).append(f"{planet} → {sign} {zodiac_glyph.get(sign,'')}")

# ---------- Retrogrades (dates only) ----------
retro_periods = {
    "Mercury":[
        (dt.date(2026,2,26), dt.date(2026,3,20)),
        (dt.date(2026,6,29), dt.date(2026,7,23)),
        (dt.date(2026,10,24),dt.date(2026,11,13)),
    ],
    "Venus":[ (dt.date(2026,10,3), dt.date(2026,11,14)) ],
    "Mars":[  ],
    "Jupiter":[
        (dt.date(2025,11,11), dt.date(2026,3,11)),
        (dt.date(2026,12,13), dt.date(2027,4,13)),
    ],
    "Saturn":[ (dt.date(2026,7,26), dt.date(2026,12,10)) ],
    "Uranus":[
        (dt.date(2025,9,6),  dt.date(2026,2,4)),
        (dt.date(2026,9,10), dt.date(2027,2,8)),
    ],
    "Neptune":[ (dt.date(2026,7,7), dt.date(2026,12,12)) ],
    "Pluto":[   (dt.date(2026,5,6), dt.date(2026,10,16)) ],
}
retro_markers_by_date = {}
for planet, spans in retro_periods.items():
    for a,b in spans:
        retro_markers_by_date.setdefault(a, []).append(f"{planet} R starts")
        retro_markers_by_date.setdefault(b, []).append(f"{planet} R ends")

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

def safe_join(items): return " · ".join(items)
def first_wrapped_line(text, font_name, font_size, max_w):
    wrapped = wrap_to_width(text, font_name, font_size, max_w)
    if not wrapped: return ""
    return wrapped[0].rstrip(" ,.;:·")

# ---------- PDF ----------
c = canvas.Canvas(PDF_PATH, pagesize=landscape(A4))
W,H = landscape(A4)

# ---------- Front ----------
def draw_front():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)
    m=2.0*cm; c.setLineWidth(2); c.setStrokeColor(colors.Color(0,0,0,0.12))
    c.roundRect(m,m,W-2*m,H-2*m,14,stroke=True,fill=False)
    glyphs=["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
    c.setFont(FONT_BOLD,18); c.setFillColor(colors.black)
    cols=6; gap=(W-2*m)/(cols+1); y_top=H-m-0.9*cm; y_bot=m+0.9*cm
    for i in range(cols): c.drawCentredString(m+(i+1)*gap,y_top,glyphs[i])
    for i in range(cols): c.drawCentredString(m+(i+1)*gap,y_bot,glyphs[i+6])
    c.setFont(FONT_BOLD,36); c.drawCentredString(W/2,H-6.5*cm,"The 12 Month Calendar of 2026")
    c.setFont(FONT_REG,18);  c.drawCentredString(W/2,H-8.3*cm,"Moons · Eclipses · Ingresses · Retrogrades")
    c.setFont(FONT_REG,13);  c.drawCentredString(W/2,H-9.8*cm,"Seasonal palette · Winter blue · Spring pink · Summer gold · Autumn plum")
    c.showPage()

# ---------- Month pages (no empty cells; raised stack) ----------
def draw_month_gregorian(year, month):
    name  = calendar.month_name[month]
    tint  = month_color_map[month]
    is_autumn = month in (9,10,11)
    fg = colors.white if is_autumn else colors.black

    c.setFillColor(tint); c.rect(0,0,W,H,fill=True,stroke=False)

    sym=month_symbols.get(month,"")
    c.setFillColor(fg); c.setFont(FONT_BOLD,26)
    c.drawCentredString(W/2,H-1.6*cm,f"{sym+' ' if sym else ''}{name} 2026")

    lm,rm,tm,bm = 1.8*cm, 1.8*cm, 3.0*cm, 2.3*cm
    left,top = lm, H - tm
    cols = 7
    cw = (W - lm - rm) / cols
    pad = 0.23*cm

    c.setFont(FONT_BOLD,12); c.setFillColor(fg)
    for i,wd in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        c.drawCentredString(left+cw*(i+0.5), top+0.45*cm, wd)

    first_wd, days_in_month = calendar.monthrange(year, month)  # Mon=0..Sun=6
    rows = math.ceil((first_wd + days_in_month) / 7)
    total_h = H - (tm + bm) - 0.9*cm
    ch = total_h / rows

    day_events = {}
    def push(d, text):
        if text: day_events.setdefault(d, []).append(text)

    for n in range(1, days_in_month+1):
        d = dt.date(year, month, n)
        ms = moon_sign_for_day(d)
        push(d, f"Moon in {ms} {zodiac_glyph[ms]}")
        if d in new_moons:  push(d, "○ New Moon")
        if d in full_moons: push(d, "● Full Moon")

        for dE, kind in eclipses:
            if d == dE:
                if kind=="Lunar":
                    msE = moon_sign_for_day(dE)
                    push(d, f"Lunar Eclipse {zodiac_glyph[msE]}")
                else:
                    sdt=dt.datetime(dE.year,dE.month,dE.day,12,0,tzinfo=OSLO)
                    slon=(float(ephem.Ecliptic(ephem.Sun(sdt)).lon)*180.0/math.pi)%360.0
                    ssign=zodiac_order[int(slon//30)]
                    push(d, f"Solar Eclipse {zodiac_glyph[ssign]}")

        if d in season_markers:  push(d, season_markers[d])
        if d in GLOBAL_HOLIDAYS: push(d, GLOBAL_HOLIDAYS[d])
        for a,b,label in METEOR_WINDOWS:
            if a<=d<=b: push(d, label)

        if d in ingress_by_date:
            compact = safe_join(ingress_by_date[d])
            push(d, first_wrapped_line(compact, FONT_BOLD, 7.2, cw-2*pad))

        if d in retro_markers_by_date:
            compact = safe_join(retro_markers_by_date[d])
            push(d, first_wrapped_line(compact, FONT_BOLD, 7.2, cw-2*pad))

    # Aug 27 only “Moon in Pisces”
    if month == 8:
        d27 = dt.date(2026,8,27)
        if d27 in day_events:
            day_events[d27] = [s for s in day_events[d27] if ("Full Moon" not in s and "Eclipse" not in s)]

    for r in range(rows):
        for col in range(cols):
            idx = r*7 + col - first_wd + 1
            if idx < 1 or idx > days_in_month:
                continue
            d = dt.date(year, month, idx)
            x = left + col*cw
            y = (H - tm - 0.9*cm) - (r+1)*ch

            c.setStrokeColor(colors.white); c.rect(x,y,cw,ch)

            stack_start = y + ch*0.76
            line_gap    = 0.29*cm
            safe_floor  = y + 1.18*cm
            usable_w    = cw - 2*pad

            lines = list(day_events.get(d, []))

            priority = {"Moon in":0, "○ New Moon":1, "● Full Moon":1, "Eclipse":2,
                        "Equinox":3, "Solstice":3, "peak window":4,
                        "Sun →":5, "Mercury →":6, "Venus →":7, "Mars →":8,
                        "Jupiter →":9, "Saturn →":10, "Uranus →":11, "Neptune →":12, "Pluto →":13,
                        " R starts":14, " R ends":14, "★":15}
            def keyfn(s):
                for k,v in priority.items():
                    if k in s: return v
                return 99
            lines.sort(key=keyfn)

            c.setFillColor(fg)
            y_line = stack_start; base = 7.1
            max_lines = max(0, int((stack_start - safe_floor)//line_gap))
            drawn=0
            for txt in lines:
                if drawn >= max_lines:
                    if y_line - line_gap >= safe_floor:
                        c.setFont(FONT_BOLD, base); c.drawString(x+pad, y_line - line_gap, "…")
                    break
                size = base
                while stringWidth(txt, FONT_BOLD, size) > usable_w and size > 6.6:
                    size -= 0.2
                if stringWidth(txt, FONT_BOLD, size) > usable_w:
                    w0 = wrap_to_width(txt, FONT_BOLD, size, usable_w)
                    if w0: txt = w0[0].rstrip(" ,.;:·")
                c.setFont(FONT_BOLD, size); c.drawString(x+pad, y_line, txt)
                y_line -= line_gap; drawn += 1

            c.setFont(FONT_BOLD,18); c.setFillColor(fg)
            c.drawCentredString(x+cw/2, y+0.28*cm, str(idx))

    c.showPage()

# ---------- Info page ----------
def info_page():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False)
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,"Information")
    y=H-4.5*cm; left=3*cm
    c.setFont(FONT_BOLD,12); c.drawString(left,y,"Symbols"); y-=0.6*cm
    c.setFont(FONT_REG,11)
    for line in ["♈ Aries    ♉ Taurus    ♊ Gemini    ♋ Cancer",
                 "♌ Leo      ♍ Virgo     ♎ Libra     ♏ Scorpio",
                 "♐ Sagittarius    ♑ Capricorn    ♒ Aquarius    ♓ Pisces"]:
        c.drawString(left,y,line); y-=0.55*cm
    c.drawString(left,y,"Month symbols · ✶ ♥ ❀ ✿ ❧ ✢ ✺ ✸ ❦ ❁ ✦ ✳"); y-=0.8*cm
    c.setFont(FONT_BOLD,12); c.drawString(left,y,"Colors"); y-=0.6*cm
    c.setFont(FONT_REG,11); c.drawString(left,y,"Winter pastel blue · Spring pastel pink · Summer warm gold · Autumn dark plum"); y-=1.0*cm
    c.setFont(FONT_BOLD,12); c.drawString(left,y,"Event Types"); y-=0.6*cm
    c.setFont(FONT_REG,11)
    for line in ["○ New Moon · ● Full Moon · Sun → Sign",
                 "Planet → Sign (Mercury to Pluto)",
                 "Mercury R starts · Mercury R ends",
                 "Eclipse (Solar or Lunar) · Equinox · Solstice"]:
        c.drawString(left,y,line); y-=0.5*cm
    y-=0.6*cm; c.setFont(FONT_BOLD,12); c.drawString(left,y,"Source"); y-=0.55*cm
    c.setFont(FONT_REG,11); c.drawString(left,y,"mooncalendar.astro-seek.com")
    c.showPage()

# ---------- Appendix A: Full Moons (single list) ----------
FM_KEYWORDS = {
    "Cancer":"home • tenderness • roots",
    "Libra":"harmony • poise • partnership",
    "Pisces":"dream • dissolve • devotion",
    "Aries":"spark • courage • initiation",
    "Taurus":"steadiness • body • comfort",
    "Gemini":"curiosity • exchange • quickness",
}
TRAD_NAMES={1:"Wolf",2:"Snow",3:"Worm",4:"Pink",5:"Flower",6:"Strawberry",7:"Buck",8:"Sturgeon",9:"Harvest",10:"Hunter’s",11:"Beaver",12:"Cold"}

def appendix_full_moons_single():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False); c.setFillColor(colors.black)
    c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,"Full Moons · 2026")
    x = 2.2*cm
    y = H - 4.0*cm
    line_h = 0.78*cm
    c.setFont(FONT_REG,12)
    items=[]
    for d,sign in sorted(full_moons.items()):
        name = TRAD_NAMES[d.month]
        if sum(1 for dd in full_moons if dd.month==d.month)>1 and d==max([dd for dd in full_moons if dd.month==d.month]): name="Blue"
        kw = FM_KEYWORDS.get(sign,"awareness • culmination")
        items.append((d,sign,name,kw))
    for d,sign,name,kw in items:
        if y < 2.0*cm:
            c.showPage()
            c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False); c.setFillColor(colors.black)
            c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,"Full Moons · 2026 (cont.)")
            c.setFont(FONT_REG,12); x=2.2*cm; y=H-4.0*cm
        c.drawString(x,y,f"{d.strftime('%b %d')}: Full Moon in {sign} {zodiac_glyph[sign]} · {name} Moon · {kw}")
        y -= line_h
    c.showPage()

# ---------- Appendix A2: New Moons (single list) ----------
NM_KEYWORDS = {
    "Capricorn":"commit • structure • integrity",
    "Pisces":"imagine • surrender • soften",
    "Gemini":"connect • learn • adapt",
    "Leo":"shine • create • lead",
    "Virgo":"refine • serve • organize",
    "Libra":"balance • beautify • relate",
    "Scorpio":"transform • merge • renew",
    "Sagittarius":"aim • explore • trust",
}
def appendix_new_moons_single():
    c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False); c.setFillColor(colors.black)
    c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,"New Moons · 2026")
    x = 2.2*cm; y = H-4.0*cm; line_h=0.78*cm
    c.setFont(FONT_REG,12)
    for d,sign in sorted(new_moons.items()):
        if y < 2.0*cm:
            c.showPage()
            c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False); c.setFillColor(colors.black)
            c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,"New Moons · 2026 (cont.)")
            c.setFont(FONT_REG,12); x=2.2*cm; y=H-4.0*cm
        kw = NM_KEYWORDS.get(sign,"seed • intention • begin")
        c.drawString(x,y,f"{d.strftime('%b %d')}: New Moon in {sign} {zodiac_glyph[sign]} · {kw}")
        y -= line_h
    c.showPage()

# ---------- Appendix C1: Sun Ingresses (auto paginate) ----------
def appendix_sun_ingresses():
    def header(title,cont=False):
        c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False); c.setFillColor(colors.black)
        t = title if not cont else title+" (cont.)"
        c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,t)

    header("Sun Ingresses · 2026 (dates + times)")
    xL = 2.2*cm; xR = W/2 + 0.8*cm
    yL = yR = H-4.0*cm; line_h=0.68*cm
    c.setFont(FONT_REG,12)

    items = ingresses_with_times.get("Sun",[])
    half = math.ceil(len(items)/2)
    left, right = items[:half], items[half:]
    for t,sign in left:
        if yL < 2.0*cm:
            c.showPage(); header("Sun Ingresses · 2026 (dates + times)",cont=True)
            c.setFont(FONT_REG,12); yL=yR=H-4.0*cm
        c.drawString(xL,yL,f"{t.strftime('%b %d %H:%M')}: Sun → {sign} {zodiac_glyph.get(sign,'')}")
        yL -= line_h
    for t,sign in right:
        if yR < 2.0*cm:
            c.showPage(); header("Sun Ingresses · 2026 (dates + times)",cont=True)
            c.setFont(FONT_REG,12); yL=yR=H-4.0*cm
        c.drawString(xR,yR,f"{t.strftime('%b %d %H:%M')}: Sun → {sign} {zodiac_glyph.get(sign,'')}")
        yR -= line_h
    c.showPage()

# ---------- Appendix C2: Planet Ingresses (auto paginate) ----------
def appendix_planet_ingresses():
    def header(cont=False):
        c.setFillColor(colors.white); c.rect(0,0,W,H,fill=True,stroke=False); c.setFillColor(colors.black)
        t = "Planet Ingresses · 2026 (dates + times)" + (" (cont.)" if cont else "")
        c.setFont(FONT_BOLD,24); c.drawCentredString(W/2,H-2.5*cm,t)
        c.setFont(FONT_BOLD,16)
        c.drawString(1.8*cm, H-4.0*cm, "Inner / Action")
        c.drawString(W/2,   H-4.0*cm, "Outer Planets")

    header()
    xL = 1.8*cm; xM = W/2
    yL = yM = H-4.9*cm     # a bit lower to fit the subheaders above
    line_h=0.65*cm
    c.setFont(FONT_REG,11)

    def write_block(x, y, planet, items):
        c.setFont(FONT_BOLD,12); c.drawString(x,y,f"{planet}")
        y -= 0.46*cm; c.setFont(FONT_REG,11)
        if not items:
            c.drawString(x,y,"—"); y -= line_h
        else:
            for t,sign in items:
                if y < 2.0*cm:
                    c.showPage(); header(cont=True)
                    c.setFont(FONT_REG,11)
                    y = H-4.9*cm
                    c.setFont(FONT_BOLD,12); c.drawString(x,y,f"{planet} (cont.)")
                    y -= 0.46*cm; c.setFont(FONT_REG,11)
                c.drawString(x,y,f"{t.strftime('%b %d %H:%M')} → {sign} {zodiac_glyph.get(sign,'')}")
                y -= line_h
        y -= 0.22*cm
        return y

    # Left column
    for planet in ["Mercury","Venus","Mars","Jupiter"]:
        items = ingresses_with_times.get(planet,[])
        yL = write_block(xL, yL, planet, items)

    # Right column
    for planet in ["Saturn","Uranus","Neptune","Pluto"]:
        items = ingresses_with_times.get(planet,[])
        yM = write_block(xM, yM, planet, items)

    c.showPage()

# ---------- Build ----------
def build():
    # Front + months
    c.setTitle("Serene — 12-month Calendar 2026")
    draw_front()
    for m in range(1,13):
        draw_month_gregorian(2026, m)
    # Info + Appendices
    info_page()
    appendix_full_moons_single()
    appendix_new_moons_single()
    appendix_sun_ingresses()
    appendix_planet_ingresses()
    c.save()
    print(f"Saved: {PDF_PATH}")

if __name__ == "__main__":
    build()
