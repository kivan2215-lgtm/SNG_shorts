"""Illustrated cutaways and original broadcast-style motion graphics, 720×1280."""
from functools import lru_cache
from math import sin, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
keys = (
    "tv runway class merch points ledger loophole math check order desk fleet "
    "reject lawyers judge verdict receipt finale"
).split()
animated = {"tv", "points", "math", "order", "check", "reject", "verdict", "receipt", "finale"}
BLUE = "#102349"
CREAM = "#fff3cb"
RED = "#e75649"
GOLD = "#ffd66d"
MINT = "#90d2ce"


@lru_cache(None)
def plate(key):
    i = keys.index(key)
    with Image.open(ROOT / ("ABC"[i // 6] + ".png")) as sheet:
        w, h = sheet.size
        col, row = i % 3, (i % 6) // 3
        cut = sheet.crop((w*col//3+4, h*row//2+4, w*(col+1)//3-4, h*(row+1)//2-4)).convert("RGB")
    return ImageOps.fit(cut, (720, 1280), method=Image.Resampling.LANCZOS)


@lru_cache(None)
def font(size, mono=False):
    name = "liberation/LiberationMono-Bold.ttf" if mono else "dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype("/usr/share/fonts/truetype/" + name, size)


def draw(key, t, ru):
    # Use the verified fictional-commercial Harrier cutaway at both endpoints.
    if key == "finale":
        img = plate("runway").copy()
    else:
        img = plate("merch" if key=="receipt" else key).copy()
    if key not in animated:
        return img
    d = ImageDraw.Draw(img)
    u = min(1., t * 1.8)
    u = u * u * (3. - 2. * u)

    def text(x, y, words, size=28, color=CREAM, mono=False):
        d.text((x,y), words, font=font(size, mono), fill=color, anchor="mm")

    def panel(top, bottom):
        d.rounded_rectangle((51,top+5,669,bottom+5), radius=20, fill="#3d2c2c")
        d.rounded_rectangle((49,top,667,bottom), radius=20, fill=BLUE, outline=CREAM,width=2)

    def num(value):
        return f"{value:,}".replace(",", " " if ru else ",")

    if key == "tv":
        d.rounded_rectangle((71,760,325,822),12,fill=BLUE)
        d.ellipse((90,780,106,796),fill=RED if sin(3*pi*t)>-.5 else "#bf8a79")
        text(213,790,"В ЭФИРЕ" if ru else "ON AIR",24)
    elif key == "points":
        panel(684,855)
        text(360,722,"ЦЕНА В РОЛИКЕ" if ru else "ON-SCREEN PRICE",24,MINT)
        text(360,790,num(round(7000000*u)),56,GOLD,True)
        text(360,831,"БАЛЛОВ" if ru else "POINTS",18)
    elif key == "math":
        panel(648,852)
        text(360,685,"7 000 000 × 10¢" if ru else "7,000,000 × 10¢",39,CREAM,True)
        d.line((106,727,106+509*u,727),fill=RED,width=4)
        if t>.20:
            text(360,785,"$700 000" if ru else "$700,000",57,GOLD,True)
    elif key == "order":
        x=int(70-280*(1-u)**2)
        d.rounded_rectangle((x,700,x+580,844),12,fill="#fff1cc",outline=BLUE,width=3)
        d.line((x+27,753,x+554,753),fill="#afa893",width=2)
        text(x+291,729,"ЗАКАЗ" if ru else "ORDER FORM",22,BLUE)
        text(x+290,797,"1 × HARRIER JET",39,BLUE,True)
    elif key == "check":
        panel(605,852)
        text(360,641,"СУММА ЧЕКА" if ru else "CHECK AMOUNT",24,MINT)
        text(360,690,"6 999 985 × 10¢" if ru else "6,999,985 × 10¢",35,CREAM,True)
        text(360,737,"+ $10 за доставку" if ru else "+ $10 shipping",26,CREAM)
        d.line((112,772,112+494*u,772),fill=RED,width=3)
        text(360,813,"$700 008,50" if ru else "$700,008.50",48,GOLD,True)
    elif key == "reject":
        x=round(93-300*(1-u)**2)
        d.rounded_rectangle((x,724,x+532,830),12,fill="#f9ebc6",outline="#b43c40",width=5)
        text(x+266,777,"ЧЕК ВОЗВРАЩЁН" if ru else "CHECK RETURNED",36,"#a82c3b")
    elif key == "receipt":
        # Oversized coupon, intentionally not a facsimile of an official document.
        x=int(71-252*(1-u)**2)
        d.rounded_rectangle((x,660,x+572,848),16,fill=CREAM,outline=RED,width=5)
        for i in range(11):
            yy=679+i*15
            d.line((x+115,yy,x+115,yy+7),fill=BLUE,width=2)
        text(x+64,756,"1×",31,BLUE,True)
        text(x+347,724,"КУПОН" if ru else "COUPON",24,BLUE)
        text(x+345,787,"БЕСПЛАТНАЯ КОЛА" if ru else "FREE COLA",33,"#a82c3b")
    elif key == "verdict":
        panel(710,852)
        text(360,744,"РЕШЕНИЕ СУДА · 1999" if ru else "COURT RULING · 1999",23,MINT)
        if t>.15:
            text(360,807,"В ПОЛЬЗУ PEPSI" if ru else "PEPSI WINS",38,GOLD)
    else:
        panel(650,855)
        text(360,689,"В следующей рекламе" if ru else "In a later ad",25,MINT)
        text(192,758,num(7000000),27,CREAM,True)
        d.line((289,758,291+38*u,758),fill=RED,width=4)
        if u>.48:
            d.polygon(((329,750),(342,758),(329,766)),fill=RED)
            text(495,758,num(700000000),32,GOLD,True)
        text(360,815,"БАЛЛОВ" if ru else "POINTS",20)
    return img
