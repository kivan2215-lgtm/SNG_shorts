"""Copper, ultramarine and rubric-red motion art for the Roman synod of 897."""
from functools import lru_cache
from math import cos, sin, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
SIZE=(720,1280)
SHEETS={
    'A':'accused clerks rome tomb vestments deacon',
    'B':'stephen speaks scribe council ledger avalanche',
    'C':'seal records monk corridor restored chair',
    'D':'summons double mute quills sandal lamp',
}
LAYOUT={k:(sheet,j) for sheet,names in SHEETS.items() for j,k in enumerate(names.split())}
keys=list(LAYOUT)+['painting','painting_detail','sees']
animated={'tomb','sees','double','seal','restored','scribe'}
GOLD='#e1b56c'
GILT='#af8451'
PARCH='#efdbaf'
INK='#29212d'
LAPIS='#253843'
TEAL='#9fd2c2'
RED='#8b2936'
MILK='#fff2cf'
LINE='#9e825f'


@lru_cache(None)
def face(size,kind='sans'):
    family={'sans':'DejaVuSansCondensed-Bold','serif':'DejaVuSerif','italic':'DejaVuSerif-Italic','roman':'DejaVuSerif-Bold','mono':'DejaVuSansMono'}[kind]
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+family+'.ttf',size)


def label(d,xy,string,size,fill=MILK,kind='sans',anchor='lm'):
    d.text(xy,string,font=face(size,kind),fill=fill,anchor=anchor)


def ramp(t,start=0,end=1):
    t=max(0,min(1,(t-start)/(end-start)))
    return t*t*(3-2*t)


def diamond(d,x,y,r,color):
    d.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill=color)


def stroke(d,x1,y1,x2,y2,t,fill=GOLD,width=3):
    d.line((x1,y1,x1+(x2-x1)*t,y1+(y2-y1)*t),fill=fill,width=width)


def plaque(d,top,bottom):
    d.rounded_rectangle((47,top+4,671,bottom+5),12,fill='#292021')
    d.rounded_rectangle((44,top,668,bottom),12,fill='#252534',outline=GILT,width=3)
    d.line((60,top+12,651,top+12),fill='#655344',width=1)
    for x in (62,650):
        for y in (top+22,bottom-19):
            diamond(d,x,y,3,GOLD)


@lru_cache(None)
def square(key):
    sheet,i=LAYOUT[key]
    with Image.open(ROOT/(sheet+'.png')) as im:
        w,h=im.size
        x,y=i%3,i//3
        return im.crop((x*w//3+3,y*h//2+3,(x+1)*w//3-3,(y+1)*h//2-3)).convert('RGB')


# Each framing can be moved independently to retain the significant action.
CENTERS={'accused':.40, 'deacon':.78, 'avalanche':.82, 'scribe':.70, 'speaks':.42}

@lru_cache(None)
def plate(key):
    return ImageOps.fit(square(key),SIZE,Image.Resampling.LANCZOS,centering=(CENTERS.get(key,.5),.5))


@lru_cache(None)
def original():
    with Image.open(ROOT/'painting.jpg') as im:return im.convert('RGB')


def texture(im):
    """Toned paper and tiny flecks, deterministically sampled once per canvas."""
    from random import Random
    r=Random(897)
    d=ImageDraw.Draw(im,'RGBA')
    for i in range(36000):
        x=r.randrange(im.width);y=r.randrange(im.height)
        d.point((x,y),fill=(30,14,10,r.randrange(12,37)))
    return im


def arch(d,x,y,w,h,c):
    """A basilica in profile in the visual language of drawn manuscript maps."""
    x,y,w,h=map(int,(x,y,w,h))
    d.rectangle((x-w//2,y-h//2,x+w//2,y),fill=c)
    d.polygon([(x-w//2-7,y-h//2),(x,y-h-7),(x+w//2+7,y-h//2)],fill=c)
    d.line((x,y-h-6,x,y-h-24),fill=c,width=4)
    d.line((x-6,y-h-17,x+6,y-h-17),fill=c,width=4)
    d.ellipse((x-7,y-25,x+7,y-9),fill=PARCH)
    d.rectangle((x-7,y-16,x+7,y),fill=PARCH)
    d.line((x-w//2-8,y+3,x+w//2+8,y+3),fill=c,width=3)


@lru_cache(None)
def sees_base(ru):
    # Porto here is the episcopal see at Portus by Rome, not the Portuguese city.
    im=texture(Image.new('RGB',SIZE,'#e6c795'))
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,720,1280),outline='#695941',width=13)
    d.rectangle((21,19,697,1262),outline='#9d7540',width=2)
    # Loose coastal engraving, to orient the viewer without asserting a precise road.
    d.polygon([(0,641),(49,670),(86,724),(101,779),(144,842),(199,905),(224,980),(290,1056),(310,1280),(0,1280)],fill='#628e95')
    for i in range(20):
        x=21+(i%4)*32;y=760+i*26
        if x<(y-618)*.45:
            d.arc((x-22,y,x+22,y+11),5,175,fill='#bed1c0',width=1)
    river=[(705,191),(626,237),(640,281),(577,322),(590,365),(531,405),(532,458),(466,489),(460,548),(382,584),(333,617),(275,645),(225,688),(163,703),(112,703),(57,681)]
    d.line(river,fill='#567c7c',width=10,joint='curve')
    d.line(river,fill='#9fc2b4',width=5,joint='curve')
    # Hand-engraved banks, settlement blocks and the ancient harbour basin at Porto.
    d.line([(x+6,y+9) for x,y in river],fill='#b79d77',width=2)
    for x,y in [(396,521),(421,501),(461,532),(510,546),(541,492),(588,464),
                (556,421),(598,411),(621,423),(448,432),(125,626),(129,657),
                (212,641),(233,625),(235,657)]:
        d.polygon([(x,y),(x+12,y-6),(x+23,y),(x+13,y+7)],fill='#c5aa80',outline='#a38b69')
        d.line((x+13,y+7,x+13,y+14,x+23,y+8,x+23,y),fill='#aa916d',width=2)
    basin=[(97,622),(115,613),(132,620),(132,638),(116,647),(99,640)]
    d.polygon(basin,fill='#91afa1',outline='#877e60')
    d.line((97,635,72,648,54,648),fill='#74999a',width=4)
    label(d,(566,341),'Тибр' if ru else 'Tiber',24,'#415959','italic')
    label(d,(39,993),'Море' if ru else 'Sea',27,'#d0dfd3','italic')
    for x,y,r in [(74,188,43),(93,222,49),(137,184,37),(642,881,43),(618,918,35),(671,905,38),(382,348,30),(360,369,25),(272,870,32)]:
        d.arc((x-r,y-r,x+r,y+r),198,340,fill='#ac936e',width=3)
        for j in range(8):
            xx=x-r*.68+j*r*.17
            yy=y-r*.7-abs(sin((j+1)*pi/9))*r*.24
            d.line((xx,yy,xx-5,yy+8),fill='#b19a73',width=2)
    # Topographic bands keep the manuscript map legible behind the transfer line.
    for layer in range(5):
        d.arc((264+layer*11,2+layer*13,665-layer*9,210-layer*3),12,163,fill='#c6ac84',width=2)
        d.arc((311+layer*9,925+layer*7,708-layer*9,1130-layer*4),191,338,fill='#c2a880',width=2)
    arch(d,180,643,59,54,RED);arch(d,515,452,84,73,LAPIS)
    label(d,(181,679),'ПОРТО' if ru else 'PORTO',32,INK,'roman','mm')
    label(d,(514,498),'РИМ' if ru else 'ROME',42,INK,'roman','mm')
    label(d,(348,810),'Переход между кафедрами' if ru else 'Transfer between episcopal sees',32,INK,'serif','mm')
    d.line((153,846,566,846),fill=GILT,width=2)
    label(d,(359,877),'Предмет обвинения' if ru else 'The charge against Formosus',25,RED,'sans','mm')
    return im


def draw_sees(t,ru):
    im=sees_base(ru).copy();d=ImageDraw.Draw(im)
    pts=[]
    for i in range(91):
        u=i/90
        pts.append((round(208+258*u),round(607-153*u-43*sin(pi*u))))
    n=max(1,round(ramp(t,.1,.87)*90));d.line(pts[:n+1],fill=RED,width=5)
    x,y=pts[n];d.ellipse((x-6,y-6,x+6,y+6),fill=MILK,outline=RED,width=3)
    return im


@lru_cache(None)
def painting_plate(ru):
    # Reproduce the entire canvas; the two details below identify the principals.
    im=texture(Image.new('RGB',SIZE,'#24222a'))
    d=ImageDraw.Draw(im)
    w,h=original().size
    picture=original().resize((720,round(720*h/w)),Image.Resampling.LANCZOS)
    y=127
    im.paste(picture,(0,y));edge=y+picture.height
    d.line((0,y-3,719,y-3),fill=GOLD,width=3)
    d.line((0,edge+3,719,edge+3),fill=GOLD,width=3)
    label(d,(38,edge+46),'Жан-Поль Лоранс' if ru else 'Jean-Paul Laurens',32,MILK,'serif')
    label(d,(678,edge+46),'1870',34,GOLD,'roman','rm')
    d.line((38,edge+78,679,edge+78),fill=GILT,width=1)
    details=[((.035,.14,.29,.48),'Стефан VI' if ru else 'Stephen VI'),((.54,.13,.82,.49),'Формоз' if ru else 'Formosus')]
    for j,(box,name) in enumerate(details):
        crop=original().crop(tuple(round((w if k%2==0 else h)*f) for k,f in enumerate(box)))
        crop=ImageOps.fit(crop,(292,135),Image.Resampling.LANCZOS,centering=(.5,.40))
        x=38+j*350
        im.paste(crop,(x,edge+94))
        label(d,(x,edge+257),name,24,GOLD,'sans')
    return im


@lru_cache(None)
def painting_crop():
    # The unabridged picture establishes context; this shot returns to Formosus.
    im=original()
    w,h=im.size
    center=int(w*.653)
    cw=round(h*720/1280)
    return im.crop((center-cw//2,0,center+cw//2,h)).resize(SIZE,Image.Resampling.LANCZOS)


def draw(key,t,ru):
    if key=='painting':return painting_plate(ru).copy()
    if key=='painting_detail':
        im=painting_crop().copy()
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((28,851,342,910),7,fill='#302934',outline=GILT,width=1)
        label(d,(43,880),'Формоз · Лоранс, 1870' if ru else 'Formosus · Laurens, 1870',22,MILK,'serif')
        return im
    t=max(0.,min(1.,t))
    if key=='sees':return draw_sees(t,ru)
    im=plate(key).copy()
    if key not in animated:return im
    d=ImageDraw.Draw(im);tr=lambda a,b:a if ru else b
    if key=='tomb':
        plaque(d,669,873)
        label(d,(83,713),tr('Смерть Формоза','Formosus dies'),24)
        label(d,(626,713),tr('Суд','Trial'),24,kind='sans',anchor='rm')
        label(d,(83,764),tr('АПРЕЛЬ 896','APRIL 896'),30,GOLD,'roman')
        label(d,(625,764),'897',36,GOLD,'roman','rm')
        y=812
        for i in range(10):
            x=92+i*58
            d.line((x,y-7,x,y+7),fill=GILT,width=2)
        n=ramp(t,.02,.62)
        d.line((92,y,614,y),fill=GILT,width=2)
        stroke(d,92,y,614,y,n,MILK,4);diamond(d,92+522*n,y,6,GOLD)
        label(d,(354,846),tr('около девяти месяцев','about nine months'),23,TEAL,'sans','mm')
    elif key=='double':
        plaque(d,698,876)
        label(d,(83,742),tr('Вопрос Стефана','Stephen asks'),25)
        label(d,(629,742),tr('Подсудимый','Defendant'),25,kind='sans',anchor='rm')
        d.line((96,790,591,790),fill='#786552',width=2)
        n=ramp(t,.04,.41)
        stroke(d,96,790,591,790,n,GOLD,3)
        if n>.85:d.polygon([(596,790),(580,784),(580,796)],fill=GOLD)
        if t>.31:
            label(d,(356,839),tr('Отвечает диакон','The deacon answers'),32,TEAL,'serif','mm')
    elif key in ('seal','restored'):
        green=key=='restored'
        x=61;y=710
        d.rounded_rectangle((x,y,655,y+160),5,fill=PARCH,outline='#6c4939',width=3)
        d.line((x+26,y+49,610,y+49),fill=LINE,width=2)
        label(d,(x+29,y+27),tr('Рукоположения','Ordinations') if green else tr('Дело Формоза','Case of Formosus'),25,INK,'serif')
        name=tr('ВОССТАНОВЛЕНЫ','RESTORED') if green else tr('ВИНОВЕН','GUILTY')
        # Impression arrives after the document, then settles.
        n=ramp(t,.02,.34)
        col='#275745' if green else '#8a3036'
        if t>=.16:
            label(d,(x+28,y+97+round((1-n)*10)),name,36,col,'roman')
        sx,sy=592,y+104
        r=round(30+5*(1-n))
        pts=[(sx+(r+(i%2)*1.8)*cos(i*pi/24),sy+(r+(i%2)*1.8)*sin(i*pi/24)) for i in range(48)]
        d.polygon(pts,fill=col,outline=INK)
        d.ellipse((sx-21,sy-21,sx+21,sy+21),outline=GILT,width=2)
        d.line((sx,sy-12,sx,sy+12),fill=GOLD,width=3)
        d.line((sx-7,sy-5,sx+7,sy-5),fill=GOLD,width=3)
        # The brass die comes down on the wax, then lifts to expose the impression.
        if t < .58:
            lift=47*(1-ramp(t,0,.16))+126*ramp(t,.21,.58)
            stamp=round(sy+4-lift)
            if stamp>y-12:
                d.rounded_rectangle((sx-18,stamp-67,sx+18,stamp-20),11,fill='#6e4b3b',outline=GILT,width=3)
                d.ellipse((sx-26,stamp-77,sx+26,stamp-49),fill='#836849',outline=GOLD,width=3)
                d.polygon([(sx-16,stamp-25),(sx+16,stamp-25),(sx+33,stamp-9),(sx+33,stamp-1),(sx-33,stamp-1),(sx-33,stamp-9)],fill=GILT,outline='#6a4a37')
                d.line((sx-27,stamp-5,sx+27,stamp-5),fill=GOLD,width=2)
    elif key=='scribe':
        # A tiny expanding ink spot supplies the cutaway's action.
        n=ramp(t,.1,.65)
        if n:
            x,y=342,808
            r=2+int(9*n)
            d.ellipse((x-r,y-r*.7,x+r,y+r*.7),fill='#38262e')
    return im
