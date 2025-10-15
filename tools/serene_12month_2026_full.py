~/calenv/bin/python3 ~/serene-site/tools/serene_12month_2026_full.py
xdg-open ~/serene-site/downloads/12/core-2026-v1.pdf

cd ~/serene-site
git add downloads/12/core-2026-v1.pdf tools/serene_12month_2026_full.py
git commit -m "12-month calendar: remove all out-of-month boxes"
git push

# 2026 — 12-Month Calendar (FULL · matches 13-month style)
# Update: draws ONLY real days; no boxes for out-of-month cells.

import os, math, random, calendar, datetime as dt
from zoneinfo import ZoneInfo
import ephem

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------------- Output path ----------------
SITE_DIR  = os.path.expanduser("~/serene-site")
OUT_DIR   = os.path.join(SITE_DIR, "downloads", "12")
os.makedirs(OUT_DIR, exist_ok=True)
pdf_path  = os.path.join(OUT_DIR, "core-2026-v1.pdf")

# ---------------- Fonts ----------------
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

# ---------------- Colors ----------------
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
    10:season_colors["Fall"],  11:season_colors["Fall"],  12:season_colors["Winter"],
}

# ---------------- Symbols ----------------
month_symbols = {1:"✶",2:"♥",3:"❀",4:"✿",5:"❧",6:"✢",7:"✺",8:"✸",9:"❦",10:"❁",11:"✦",12:"✳"}
zodiac_glyph  = {"Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓"}
zodiac_order  = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# ---------------- Phases (locked) ----------------
full_moons = {
    dt.date(2026,1,3):"Cancer",  dt.date(2026,4,2):"Libra",
    dt.date(2026,8,28):"Pisces", dt.date(2026,9,26):"Aries",
    dt.date(2026,10,26):"Taurus", dt.date(2026,11,24):"Gemini",
    dt.date(2026,12,24):"Cancer",
}
new_moons = {
    dt.date(2026,1,18):"Capricorn", dt.date(2026,3,19):"Pisces",
    dt.date(2026,6,15):"Gemini",    dt.date(2026,8,12):"Leo",
    dt.date(2026,9,11):"Virgo",     dt.date(2026,10,10):"Libra",
    dt.date(2026,11,9):"Scorpio",   dt.date(2026,12,9):"Sagittarius",
}

# ---------------- Sun ingresses ----------------
sun_ingress = {
    dt.date(2026,1,20):"Aquarius", dt.date(2026,2,18):"Pisces", dt.date(2026,3,20):"Aries",
    dt.date(2026,4,20):"Taurus",   dt.date(2026,5,21):"Gemini", dt.date(2026,6,21):"Cancer",
    dt.date(2026,7,22):"Leo",      dt.date(2026,8,23):"Virgo",  dt.date(2026,9,23):"Libra",
    dt.date(2026,10,23):"Scorpio", dt.date(2026,11,22):"Sagittarius", dt.date(2026,12,21):"Capricorn",
}

# ---------------- Holidays ----------------
GLOBAL_HOLIDAYS = {
    dt.date(2026,4,5):"Easter Sunday ★",
    dt.date(2026,10,31):"Halloween ★",
    dt.date(2026,12,25):"Christmas Day ★",
}

# ---------------- Meteors ----------------
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

# ---------------- Seasons ----------------
season_markers = {
    dt.date(2026,3,20):"Spring Equinox",
    dt.date(2026,6,21):"Summer Solstice",
    dt.date(2026,9,23):"Autumn Equinox",
    dt.date(2026,12,21):"Winter Solstice",
}

# ---------------- Astro helpers ----------------
OSLO = ZoneInfo("Europe/Oslo"); UTC = ZoneInfo("UTC")
def moon_sign_for_day(d: dt.date)->str:
    if d == dt.date(2026,8,27): return "Pisces"  # special rule
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
    d=start+dt.timedelta(days=1); inR=False; res=[]; Rs=None
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

eclipses=[(dt.date(2026,8,12),"Solar"),(dt.date(2026,8,28),"Lunar")]

# ---------------- PDF ----------------
c=canvas.Canvas(pdf_path,pagesize=landscape(A4))
W,H=landscape(A4)

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

def safe_join(items):
    return " · ".join(items)

def first_wrapped_line(text, font_name, font_size, max_w):
    wrapped = wrap_to_width(text, font_name, font_size, max_w)
    if not wrapped: return ""
    return wrapped[0].rstrip(" ,.;:·")

# ---------------- Front page ----------------
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
    c.setFont(FONT_REG,18);  c.drawCentredString(W/2,H-8.3*cm,"Gregorian months · 1 month per page")
    c.setFont(FONT_REG,13);  c.drawCentredString(W/2,H-9.8*cm,"Seasonal palette · Winter blue · Spring pink · Summer gold · Autumn plum")
draw_front(); c.showPage()

# ---------------- Month page (only real-day boxes) ----------------
def draw_month_gregorian(year, month):
    name  = calendar.month_name[month]
    tint  = month_color_map[month]
    is_autumn = month in (9,10,11)
    fg = colors.white if is_autumn else colors.black

    c.setFillColor(tint); c.rect(0,0,W,H,fill=True,stroke=False)

    sym=month_symbols.get(month,"")
    c.setFillColor(fg); c.setFont(FONT_BOLD,26)
    c.drawCentredString(W/2,H-1.6*cm,f"{sym+' ' if sym else ''}{name} 2026")

    # layout
    lm,rm,tm,bm=1.8*cm,1.8*cm,3.0*cm,2.3*cm
    left,top=lm,H-tm; cols=7
    cw=(W-lm-rm)/cols; pad=0.23*cm

    # weekday header
    c.setFont(FONT_BOLD,12); c.setFillColor(fg)
    for i,wd in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        c.drawCentredString(left+cw*(i+0.5),top+0.45*cm,wd)

    # month shape (no ghost boxes)
    first_wd, days_in_month = calendar.monthrange(year, month)  # Mon=0..Sun=6
    # rows needed:
    rows = (first_wd + days_in_month + 6)//7  # ceil

    # build event dict only for real days
    day_events = {}
    def push(d, text): day_events.setdefault(d, []).append(text)

    for day in range(1, days_in_month+1):
        d = dt.date(year, month, day)
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
                    sdt=dt.datetime(dE.year,dE.month,dE.day,12,0,tzinfo=OSLO).astimezone(UTC)
                    slon=(float(ephem.Ecliptic(ephem.Sun(sdt)).lon)*180.0/math.pi)%360.0
                    ssign=zodiac_order[int(slon//30)]
                    push(d, f"Solar Eclipse {zodiac_glyph[ssign]}")
        if d in season_markers:  push(d, season_markers[d])
        if d in GLOBAL_HOLIDAYS: push(d, GLOBAL_HOLIDAYS[d])
        for a,b,label in METEOR_WINDOWS:
            if a<=d<=b: push(d, label)
        if d in sun_ingress:
            s = sun_ingress[d]; push(d, f"Sun → {s} {zodiac_glyph[s]}")
        if d in planet_ingress_by_date:
            compact = safe_join(planet_ingress_by_date[d])
            push(d, first_wrapped_line(compact, FONT_BOLD, 7.2, cw-2*pad))
        if d in retro_markers:
            txt = safe_join(retro_markers[d])
            push(d, first_wrapped_line(txt, FONT_BOLD, 7.2, cw-2*pad))

    # Aug 27 rule
    if month == 8:
        d27 = dt.date(2026,8,27)
        if d27 in day_events:
            day_events[d27] = [s for s in day_events[d27] if ("Full Moon" not in s and "Eclipse" not in s)]

    # vertical metrics depend on rows used
    # total height for rows
    total_h = H - (tm + bm) - 0.9*cm  # header height ~0.9cm
    ch = total_h / rows

    # draw only real-day cells
    for r in range(rows):
        for col in range(cols):
            # map to day number
            n = r*7 + col - first_wd + 1
            if n < 1 or n > days_in_month:
                continue  # NO BOX for out-of-month cells
            d = dt.date(year, month, n)

            x = left + col*cw
            y = (H - tm - 0.9*cm) - (r+1)*ch  # below weekday header

            # cell border
            c.setStrokeColor(colors.white); c.rect(x,y,cw,ch)

            # stack geometry
            stack_start = y + ch*0.63
            line_gap    = 0.28*cm
            safe_floor  = y + 0.92*cm
            usable_w    = cw - 2*pad

            lines = day_events.get(d, [])
            # stable order
            priority = {"Moon in":0, "○ New Moon":1, "● Full Moon":1, "Eclipse":2,
                        "Equinox":3, "Solstice":3, "peak window":4,
                        "Sun →":5, "Mercury →":6, "Venus →":7, "Mars →":8,
                        "Jupiter →":9, "Saturn →":10, "Uranus →":11, "Neptune →":12, "Pluto →":13,
                        "Mercury R":14, "★":15}
            def keyfn(s):
                for k,v in priority.items():
                    if s.startswith(k) or k in s: return v
                return 99
            lines.sort(key=keyfn)

            # draw lines
            c.setFillColor(fg)
            y_line = stack_start; base = 7.2
            max_lines = max(0, int((stack_start - safe_floor)//line_gap))
            drawn=0
            for txt in lines:
                if not txt: continue
                if drawn>=max_lines:
                    if y_line - line_gap >= safe_floor:
                        c.setFont(FONT_BOLD, base)
                        c.drawString(x+pad, y_line - line_gap, "…")
                    break
                size=base
                while stringWidth(txt, FONT_BOLD, size) > usable_w and size > 6.7:
                    size -= 0.2
                if stringWidth(txt, FONT_BOLD, size) > usable_w:
                    w0=wrap_to_width(txt, FONT_BOLD, size, usable_w)
                    if w0: txt=w0[0].rstrip(" ,.;:·")
                c.setFont(FONT_BOLD, size)
                c.drawString(x+pad, y_line, txt)
                y_line -= line_gap; drawn += 1

            # BIG day number bottom-center
            c.setFont(FONT_BOLD,18); c.setFillColor(fg)
            c.drawCentredString(x+cw/2, y+0.28*cm, str(n))

# ---------------- Information page ----------------
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
    c.setFont(FONT_BOLD,12); c.drawString(left,y,"Meteor Showers · Peak windows"); y-=0.6*cm
    c.setFont(FONT_REG,11)
    for line in ["Quadrantids · Jan 2–3 · best after midnight to pre dawn",
                 "Lyrids · Apr 21–22 · best after midnight to pre dawn",
                 "Delta Aquarids · Jul 28–29 · best after midnight to pre dawn",
                 "Perseids · Aug 12–13 · best late evening to pre dawn",
                 "Orionids · Oct 21–22 · best after midnight to pre dawn",
                 "Taurids · Nov 4–5 · best after midnight to pre dawn",
                 "Leonids · Nov 17–18 · best after midnight to pre dawn",
                 "Geminids · Dec 13–14 · best late evening to pre dawn",
                 "Ursids · Dec 21–22 · best after midnight to pre dawn"]:
        c.drawString(left,y,line); y-=0.5*cm
    y-=0.6*cm; c.setFont(FONT_BOLD,12); c.drawString(left,y,"Source"); y-=0.55*cm
    c.setFont(FONT_REG,11); c.drawString(left,y,"mooncalendar.astro-seek.com")
    c.showPage()

# ---------------- Reference page ----------------
def reference_page():
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

    traditional_names={1:"Wolf Moon",2:"Snow Moon",3:"Worm Moon",4:"Pink Moon",5:"Flower Moon",6:"Strawberry Moon",7:"Buck Moon",8:"Sturgeon Moon",9:"Harvest Moon",10:"Hunter’s Moon",11:"Beaver Moon",12:"Cold Moon"}
    fm=[]
    for d,sign in sorted(full_moons.items()):
        name=traditional_names[d.month]
        if sum(1 for dd in full_moons if dd.month==d.month)>1 and d==max([dd for dd in full_moons if dd.month==d.month]): name="Blue Moon"
        fm.append((d,sign,name))
    def fmt_fm(it): d,sign,name=it; return f"{d.strftime('%b %d')}: Full Moon in {sign} {zodiac_glyph[sign]} · {name}"
    y_after_fm = draw_two_column_panel(left_x,right_x,top_y,"Full Moons 2026",fm,fmt_fm,rows_left_max=7)

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
    def fmt_sun(it): d,sign=it; return f"{d.strftime('%b %d')}: Sun → {sign} {zodiac_glyph[sign]}"
    rows_per_col=8; col_w=6.6*cm
    x1=right_x; x2=right_x+col_w
    for it in sun_items[:rows_per_col]:
        if y_s < bottom_margin + line_h: break
        c.drawString(x1,y_s,fmt_sun(it)); y_s-=line_h
    y_s2 = y_next - 0.8*cm
    for it in sun_items[rows_per_col:]:
        if y_s2 < bottom_margin + line_h: break
        c.drawString(x2,y_s2,fmt_sun(it)); y_s2-=line_h

    c.showPage()

# ---------------- Build ----------------
def build():
    for m in range(1,13):
        draw_month_gregorian(2026, m); c.showPage()
    info_page()
    reference_page()
    c.save()
    print(f"Saved: {pdf_path}")

if __name__ == "__main__":
    build()
