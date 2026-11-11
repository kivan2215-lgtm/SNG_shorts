"""Native portrait documentary layouts. No random crops, shake, or zoom loops."""
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json, math, numpy as np

ROOT=Path(__file__).parent; A=ROOT/'assets'; W,H=1080,1920
INK='#edf3f3'; MUTED='#a9bec4'; GOLD='#f0cc73'; AQUA='#76d4dc'; NAVY='#0a1c28'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
@lru_cache(100)
def font(n,bold=True):return ImageFont.truetype(BOLD if bold else FONT,n)
def text(d,xy,s,size=46,fill=INK,width=940,anchor='mm',bold=True):
    while max(font(size,bold).getlength(line) for line in s.split('\n'))>width:size-=1
    d.multiline_text(xy,s,font=font(size,bold),fill=fill,anchor=anchor,spacing=14,align='center' if anchor=='mm' else 'left')
def tr(lang,ru,en):return ru if lang=='ru' else en

@lru_cache(1)
def paper():
    y=np.arange(H)[:,None,None]/H
    top=np.array([15,39,51]);bottom=np.array([5,15,23])
    rgb=np.tile((top*(1-y)+bottom*y).astype('uint8'),(1,W,1))
    im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
    for x in range(0,W,90):d.line((x,0,x,H),fill='#17303b',width=1)
    for y in range(0,H,90):d.line((0,y,W,y),fill='#17303b',width=1)
    return im
def base():return paper().copy()
def header(im,kicker,title,color=GOLD):
    d=ImageDraw.Draw(im)
    d.line((70,155,145,155),fill=color,width=4)
    text(d,(171,155),kicker,27,color,825,'lm')
    text(d,(70,253),title,54,INK,935,'lm')
def footer(im,s):
    d=ImageDraw.Draw(im);text(d,(70,1760),s,22,MUTED,900,'lm',False)
def pill(d,xy,s,color=GOLD,size=27):
    x,y=xy;w=font(size).getlength(s)+38
    d.rounded_rectangle((x,y,x+w,y+53),radius=10,fill='#10222d',outline=color,width=1)
    text(d,(x+19,y+26),s,size,color,1000,'lm')
def rectphoto(im,pic,box):
    x,y,w,h=box;pic=ImageOps.contain(pic,(w,h),Image.Resampling.LANCZOS)
    im.paste(pic,(int(x+(w-pic.width)/2),int(y+(h-pic.height)/2)))
@lru_cache(80)
def source(name,crop=None):
    # A review/publishing bundle keeps only the used archival crops, not entire magazine issues.
    index=A/'prepared_index.json'
    if index.exists():
        prepared=json.loads(index.read_text()).get(json.dumps([name,crop]))
        if prepared and (A/prepared).exists():return Image.open(A/prepared).convert('RGB')
    im=Image.open(A/name).convert('RGB')
    if crop:
        w,h=im.size;im=im.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(crop)))
    return im

CROPS={
 'captain':('life35_hd.jpg',(.365,.002,.999,.536)),
 'family':('life34_hd.jpg',(.38,.64,.96,.999)),
 'yacht':('life34_hd.jpg',(.003,.595,.346,.947)),
 'raft':('life30_hd.jpg',(.005,.002,.995,.857)),
 'crew':('life32_hd.jpg',(.003,.002,.812,.45)),
 'medical':('life32_hd.jpg',(.388,.532,.811,.858)),
 'hospital':('life33_hd.jpg',(.035,.032,.985,.979)),
 'recovery':('life39_hd.jpg',(.012,.005,.997,.867)),
 'girl':('rescued.jpg',None),
}
def archive(lang,key,title,tag=None,detail=None):
    im=base();header(im,tag or tr(lang,'АРХИВ • НОЯБРЬ 1961','ARCHIVE • NOVEMBER 1961'),title)
    name,crop=CROPS[key];pic=source(name,crop)
    # Every original photo is contained, never cropped to force a face into 9:16.
    if key in ['family','crew']:
        box=(55,365,970,915)
    elif key=='yacht':box=(90,335,900,1045)
    elif key=='girl':box=(125,350,830,1010)
    else:box=(40,330,1000,1080)
    rectphoto(im,pic,box)
    d=ImageDraw.Draw(im)
    if detail:
        d.rectangle((70,1288,1010,1390),fill='#102c38')
        text(d,(540,1337),detail,37,GOLD,875)
    footer(im,'LIFE · 01.12.1961' if key!='girl' else tr(lang,'Газетная фотография · 23.11.1961','Newspaper photograph · 23 Nov 1961'))
    return im

def reconstruction(lang,key,title='',kicker=''):
    refs={'rescue':('recon_triptych_1.png',0),'storm':('recon_triptych_1.png',1),'calm':('recon_triptych_1.png',2),'lookout':('recon_triptych_2.png',0),'interview':('recon_triptych_2.png',1),'motel':('recon_triptych_2.png',2)}
    if key=='cabin':pic=source('recon_cabin.png')
    elif key=='night_cabin':pic=source('recon_dry_stairs.png')
    else:
        name,col=refs[key];sheet=source(name);w,h=sheet.size
        pic=sheet.crop((round(col*w/3)+7,5,round((col+1)*w/3)-7,h-5))
    im=ImageOps.fit(pic,(W,H),Image.Resampling.LANCZOS)
    # Only exposure-friendly translucent gradients; never camera movement.
    overlay=Image.new('RGBA',(W,H));arr=np.zeros((H,W,4),dtype='uint8')
    yy=np.arange(H)
    alpha=np.maximum(np.clip((370-yy)/370,0,1)*190,np.clip((yy-1340)/580,0,1)*170)
    arr[:,:,3]=alpha[:,None];im=Image.alpha_composite(im.convert('RGBA'),Image.fromarray(arr)).convert('RGB')
    d=ImageDraw.Draw(im)
    pill(d,(68,105),tr(lang,'Реконструкция','Reconstruction'),MUTED,24)
    if kicker:text(d,(70,216),kicker,29,GOLD,920,'lm')
    if title:text(d,(70,301),title,49,INK,910,'lm')
    return im

def arrow(d,points,color=AQUA,width=7):
    d.line(points,fill=color,width=width,joint='curve')
    x,y=points[-1];px,py=points[-2];a=math.atan2(y-py,x-px)
    head=[(x,y),(x-22*math.cos(a-.5),y-22*math.sin(a-.5)),(x-22*math.cos(a+.5),y-22*math.sin(a+.5))]
    d.polygon(head,fill=color)

@lru_cache(2)
def geography(lang):
    im=base();header(im,'1961',tr(lang,'БАГАМСКИЕ ОСТРОВА','THE BAHAMAS'))
    d=ImageDraw.Draw(im);x0,y0=55,360;ww,hh=970,950
    def proj(lon,lat):return (x0+(lon+84)/11*ww,y0+(31-lat)/11*hh)
    d.rounded_rectangle((x0,y0,x0+ww,y0+hh),22,fill='#12394b',outline='#35616e',width=2)
    for lon in range(-84,-72,2):
        x,_=proj(lon,25);d.line((x,y0,x,y0+hh),fill='#225064',width=1)
    for lat in range(20,32,2):
        _,y=proj(-80,lat);d.line((x0,y,x0+ww,y),fill='#225064',width=1)
    geo=json.loads((A/'world50.geojson').read_text())
    mask=Image.new('RGBA',(W,H));m=ImageDraw.Draw(mask)
    for feat in geo['features']:
        typ=feat['geometry']['type'];polys=feat['geometry']['coordinates']
        if typ=='Polygon':polys=[polys]
        for poly in polys:
            ring=poly[0]
            if not any(-85<lo<-72 and 19<la<32 for lo,la,*_ in ring):continue
            pts=[proj(lo,la) for lo,la,*_ in ring]
            m.polygon(pts,fill='#7e968b',outline='#c0bda1',width=2)
    mask=mask.crop((x0,y0,x0+ww,y0+hh));im.paste(mask,(x0,y0),mask);d=ImageDraw.Draw(im)
    for lon,lat,label in [(-81.9,28.8,tr(lang,'ФЛОРИДА','FLORIDA')),(-79.6,21.8,tr(lang,'КУБА','CUBA'))]:
        text(d,proj(lon,lat),label,30,INK,330)
    x,y=proj(-77.355,25.048)
    d.ellipse((x-10,y-10,x+10,y+10),fill=GOLD)
    d.line((x+13,y,x+93,y-65),fill=GOLD,width=3)
    text(d,(x+105,y-65),tr(lang,'Нассау','Nassau'),33,GOLD,300,'lm')
    text(d,proj(-75.8,26.7),tr(lang,'БАГАМЫ','BAHAMAS'),34,GOLD,330)
    # Locator, not a fabricated voyage or drift route.
    pill(d,(85,1335),tr(lang,'Район плавания','Sailing region'),AQUA,28)
    footer(im,tr(lang,'География: Natural Earth • точный маршрут не показан','Geography: Natural Earth • no exact voyage route shown'))
    return im

def opening_dates(lang,stage=0,p=1):
    im=base();header(im,tr(lang,'НОЯБРЬ 1961','NOVEMBER 1961'),tr(lang,'ЯХТА ИСЧЕЗЛА НОЧЬЮ','THE YACHT VANISHED AT NIGHT'))
    d=ImageDraw.Draw(im)
    # A simple illustrated vessel and rescue boat avoid repeating the archival photograph.
    d.rounded_rectangle((70,415,510,1275),20,fill='#123744',outline='#43646e',width=2)
    for y in [665,695,725,1080,1110,1140]:
        points=[(x,y+5*math.sin(x/25)) for x in range(95,490,5)]
        d.line(points,fill='#44768b',width=2)
    d.polygon([(115,632),(450,632),(413,685),(167,685)],fill='#dddbca',outline='#799198',width=3)
    d.line((244,473,244,633),fill=GOLD,width=6)
    d.line((355,517,355,633),fill=GOLD,width=5)
    d.polygon([(237,490),(150,620),(237,620)],fill='#a6bfc1')
    d.polygon([(350,531),(285,621),(350,621)],fill='#a6bfc1')
    text(d,(290,780),'BLUEBELLE',32,INK,360)
    if stage:
        d.ellipse((126,1026,455,1110),fill='#bbb9a3',outline='#e0dcca',width=4)
        d.ellipse((153,1038,427,1093),fill='#314f59',outline='#929b90',width=3)
        for x in [207,290,373]:d.line((x,1044,x,1088),fill='#bcaf92',width=11)
        text(d,(290,1210),tr(lang,'ШЛЮПКА','A DINGHY'),32,AQUA,360)
    d.line((585,510,585,1120),fill='#38535d',width=5)
    for i,(day,title,subtitle) in enumerate([
        ('12',tr(lang,'ЯХТА ТОНЕТ','THE YACHT SINKS'),tr(lang,'В море у Багам','Off the Bahamas')),
        ('13',tr(lang,'СПАСЁН КАПИТАН','CAPTAIN RESCUED'),tr(lang,'Джулиан Харви','Julian Harvey'))]):
        y=540+i*420;visible=i<=stage
        if not visible:continue
        d.ellipse((570,y-15,600,y+15),fill=GOLD if i==stage else AQUA)
        text(d,(635,y-35),day,85,GOLD,350,'lm')
        text(d,(635,y+42),tr(lang,'НОЯБРЯ','NOVEMBER'),25,MUTED,330,'lm')
        text(d,(635,y+112),title,31,INK,360,'lm')
        text(d,(635,y+173),subtitle,26,MUTED,350,'lm',False)
    footer(im,'Bluebelle · 1961')
    return im

def survival(lang,p=1):
    im=archive(lang,'hospital',tr(lang,'ТЕРРИ ДЖО • 11 ЛЕТ','TERRY JO • AGE 11'))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((70,1070,1010,1400),20,fill='#102935',outline='#426771',width=2)
    text(d,(340,1174),tr(lang,'≈ 82 ЧАСА','≈ 82 HOURS'),65,GOLD,500)
    text(d,(340,1262),tr(lang,'на маленьком плоту','on a tiny float'),30,INK,500)
    d.line((628,1110,628,1360),fill='#426771',width=2)
    text(d,(810,1164),tr(lang,'БЕЗ ЕДЫ','NO FOOD'),34,INK,330)
    text(d,(810,1270),tr(lang,'БЕЗ ПРЕСНОЙ\nВОДЫ','NO FRESH\nWATER'),31,AQUA,330)
    return im

def chronology(lang,p):
    im=base();header(im,tr(lang,'КЛЮЧЕВОЙ ПОРЯДОК СОБЫТИЙ','THE ORDER MATTERS'),tr(lang,'ОН УЗНАЛ О СПАСЕНИИ','HE LEARNED SHE WAS ALIVE'))
    d=ImageDraw.Draw(im)
    rows=[('16',tr(lang,'НОЯБРЯ','NOVEMBER'),tr(lang,'Терри Джо спасли','Terry Jo was rescued'),AQUA),
          ('17',tr(lang,'НОЯБРЯ','NOVEMBER'),tr(lang,'Харви умер','Harvey died'),GOLD),
          ('→',tr(lang,'ПОЗЖЕ','LATER'),tr(lang,'Терри дала показания','Terry gave her account'),AQUA)]
    d.line((162,485,162,1210),fill='#36535e',width=6)
    active=2 if p>.34 else 1
    for i,(day,month,label,color) in enumerate(rows):
        y=420+i*340
        if i>active:continue
        d.rounded_rectangle((230,y,1000,y+245),18,fill='#132f3d',outline='#3c626e',width=2)
        d.ellipse((141,y+93,183,y+135),fill=color)
        text(d,(285,y+66),day,66,color,160,'lm')
        text(d,(440,y+66),month,30,MUTED,500,'lm')
        text(d,(285,y+164),label,39,INK,645,'lm')
    footer(im,tr(lang,'Известие о спасении — до подробных показаний девочки','News of the rescue preceded the girl’s detailed testimony'))
    return im

def family_detail(lang):
    im=base();header(im,tr(lang,'СЕМЕЙНЫЙ АРХИВ','FAMILY ARCHIVE'),tr(lang,'ЕЁ МАТЬ И БРАТ','HER MOTHER AND BROTHER'))
    original=source(*CROPS['family']);w,h=original.size
    # Keep the complete family picture; identify the two people without cutting other faces.
    pic=ImageOps.contain(original,(970,925),Image.Resampling.LANCZOS)
    px=(W-pic.width)//2;py=380+(925-pic.height)//2
    im.paste(pic,(px,py))
    d=ImageDraw.Draw(im)
    for box,col in [((.275,.365,.50,.665),AQUA),((.56,.025,.85,.345),GOLD)]:
        x1,y1,x2,y2=box
        d.rounded_rectangle((px+x1*pic.width,py+y1*pic.height,px+x2*pic.width,py+y2*pic.height),12,outline=col,width=5)
    text(d,(300,1350),tr(lang,'ДЖИН • МАТЬ','JEAN • MOTHER'),39,AQUA,440)
    text(d,(780,1350),tr(lang,'БРАЙАН • БРАТ','BRIAN • BROTHER'),39,GOLD,440)
    footer(im,'LIFE · 01.12.1961')
    return im

def boat_scene(lang,stage,p):
    im=base();d=ImageDraw.Draw(im)
    titles=[tr(lang,'ТЕРРИ ПОДОШЛА К КАПИТАНУ','TERRY APPROACHED THE CAPTAIN'),
            tr(lang,'КАПИТАН ОТТОЛКНУЛ ЕЁ','THE CAPTAIN SHOVED HER AWAY'),
            tr(lang,'ОНА ОТВЯЗАЛА ПЛОТ','SHE RELEASED THE FLOAT')]
    header(im,tr(lang,'ПОКАЗАНИЯ ТЕРРИ • УСЛОВНЫЙ РАЗРЕЗ','TERRY’S ACCOUNT • SCHEMATIC CUTAWAY'),titles[stage])
    # A coherent cross-section: lower sleeping space, main cabin, companionway, deck.
    hull=[(95,738),(855,738),(980,797),(890,994),(310,1032),(170,946)]
    d.polygon([(95,738),(855,738),(980,797),(952,827),(110,784)],fill='#b5a382')
    d.polygon(hull,fill='#645342',outline='#b8aa8d',width=5)
    d.polygon([(133,786),(922,813),(855,961),(310,997),(200,928)],fill='#283745')
    # Structural ribs and the intact masts, not a real architectural blueprint.
    for x in range(240,890,95):d.line((x,806,x+30,972),fill='#847963',width=3)
    for x,y in [(390,440),(720,480)]:
        d.line((x,y,x,740),fill='#baa98a',width=10)
        d.line((x,y,190 if x==390 else 900,740),fill='#80969c',width=2)
        d.line((x,565,x+130,565),fill='#b4a386',width=7)
    d.line((140,730,878,730),fill='#c4bc9d',width=5)
    for x in range(180,880,80):d.line((x,705,x,732),fill='#bac5bc',width=3)
    # Sleeping space and main cabin are differentiated with real, legible objects.
    d.rectangle((230,901,480,963),fill='#9d9b85');d.rectangle((242,887,463,925),fill='#d3cfb9')
    d.rounded_rectangle((248,892,302,916),8,fill='#efdfbb')
    d.line((535,825,535,978),fill='#c0ad86',width=5)
    d.rectangle((590,879,733,893),fill='#c5ac7d')
    d.line((609,893,609,952),fill='#9d835f',width=7);d.line((713,893,713,952),fill='#9d835f',width=7)
    for x in [618,728,831]:d.ellipse((x-18,825,x+18,861),fill='#688a8e',outline='#d0ba88',width=4)
    # Companionway stairs join cabin and deck.
    for i in range(6):
        x=485+i*20;y=866-i*23;d.line((x,y,x+67,y),fill='#d5c4a3',width=7)
    text(d,(325,1085),tr(lang,'Спальное место','Sleeping area'),30,MUTED,420)
    d.line((325,1047,325,970),fill='#8dabb2',width=2)
    text(d,(725,1085),tr(lang,'Главная каюта','Main cabin'),30,MUTED,400)
    d.line((725,1047,725,967),fill='#8dabb2',width=2)
    text(d,(840,636),tr(lang,'Палуба','Deck'),29,MUTED,280)
    d.line((840,670,840,710),fill='#8dabb2',width=2)
    def person(x,y,color):
        d.ellipse((x-11,y-63,x+11,y-41),fill=color);d.line((x,y-39,x,y-12),fill=color,width=9)
        d.line((x,y-12,x-14,y+9),fill=color,width=6);d.line((x,y-12,x+14,y+9),fill=color,width=6)
        d.line((x-17,y-28,x+17,y-28),fill=color,width=6)
    if stage<2:
        person(780,723,GOLD);text(d,(780,590),tr(lang,'Капитан','Captain'),31,GOLD,290)
        q=min(1,p*1.7)
        if stage==0:
            x=440+180*q;y=885-164*q
            arrow(d,[(455,870),(535,800),(622,716)],AQUA,5)
        else:
            x=630-35*min(1,p);y=721
            arrow(d,[(758,683),(677,683)],GOLD,6)
        person(x,y,AQUA);text(d,(x-70,y-97),tr(lang,'Терри','Terry'),30,AQUA,200)
    else:
        # Flooding stays inside the hull; the float moves away along the water surface.
        mask=Image.new('L',(W,H));m=ImageDraw.Draw(mask);m.polygon(hull,fill=255)
        water=Image.new('RGBA',(W,H));wd=ImageDraw.Draw(water)
        yy=923-27*p;poly=[(0,H),(W,H)]+[(x,yy+6*math.sin(x/65+p*4)) for x in range(W,-1,-10)]
        wd.polygon(poly,fill=(38,119,144,175));water.putalpha(Image.composite(water.getchannel('A'),Image.new('L',(W,H)),mask));im=Image.alpha_composite(im.convert('RGBA'),water).convert('RGB');d=ImageDraw.Draw(im)
        fy=1170;fx=745+130*p
        for n in range(4):
            pts=[(x,fy+30+n*27+4*math.sin(x/70+p*3)) for x in range(45,1035,10)];d.line(pts,fill='#2e5e70',width=2)
        arrow(d,[(865,815),(946,1025),(fx,fy-35)],AQUA,6)
        d.rounded_rectangle((fx-78,fy-15,fx+78,fy+35),18,fill='#ece9d6',outline='#a3a793',width=4)
        d.rounded_rectangle((fx-45,fy-3,fx+45,fy+17),6,fill='#183c4f')
        person(fx,fy-13,AQUA)
        d.line((896,805,913,991),fill='#bba979',width=3)
        text(d,(430,1260),tr(lang,'Пробковый спасательный плот','A cork life float'),34,INK,700)
    pill(d,(75,1340),tr(lang,'По рассказу выжившей','Based on the survivor’s account'),AQUA,26)
    footer(im,tr(lang,'Схема объясняет действия, а не точную планировку яхты','The diagram explains the actions, not the yacht’s exact layout'))
    return im

def newspaper(lang):
    im=base();header(im,tr(lang,'СЛЕДСТВИЕ • НОЯБРЬ 1961','INVESTIGATION • NOVEMBER 1961'),tr(lang,'ЭТО БЫЛО ПРЕСТУПЛЕНИЕ','THIS WAS A CRIME'))
    if (A/'news_headline.jpg').exists():head=source('news_headline.jpg')
    else:
        pg=source('oregon_front.jpg');w,h=pg.size
        head=pg.crop((int(w*.535),int(h*.506),int(w*.752),int(h*.58)))
    rectphoto(im,head,(55,385,970,490))
    # Authentic contemporary report, shown as a document, with an identified translation.
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((70,970,1010,1370),18,fill='#e7dec9')
    text(d,(115,1030),tr(lang,'В ГАЗЕТНОМ РЕПОРТАЖЕ:','THE CONTEMPORARY REPORT:'),28,'#4f534b',855,'lm')
    text(d,(540,1182),tr(lang,'Береговая охрана расследует\nпредполагаемое массовое\nубийство на яхте.','The Coast Guard investigates\nan apparent mass murder\naboard the Bluebelle.'),42,'#172d35',855)
    footer(im,'The Oregon Statesman · AP · 22.11.1961')
    return im

def compare(lang,p):
    im=base();header(im,tr(lang,'ДВЕ НЕСОВМЕСТИМЫЕ ВЕРСИИ','TWO CONTRADICTORY ACCOUNTS'),tr(lang,'КРУШЕНИЕ БЫЛО ПРИКРЫТИЕМ','THE SHIPWRECK WAS A COVER'))
    d=ImageDraw.Draw(im)
    for x,col,title,key in [(70,GOLD,tr(lang,'КАПИТАН','CAPTAIN'),'captain'),(555,AQUA,tr(lang,'ТЕРРИ ДЖО','TERRY JO'),'girl')]:
        d.rounded_rectangle((x,365,x+455,1325),20,fill='#122c3a',outline=col,width=2)
        rectphoto(im,source(*CROPS[key]),(x+60,408,335,355));d=ImageDraw.Draw(im)
        text(d,(x+227,822),title,33,col,420)
    entries=[(tr(lang,'Шторм','Storm'),tr(lang,'Спокойное море','Calm sea')),(tr(lang,'Пожар','Fire'),tr(lang,'Пожара не было','No fire'))]
    for i,(left,right) in enumerate(entries):
        y=990+i*183
        text(d,(297,y),left,40,GOLD,420);text(d,(782,y),right,36,AQUA,410)
        d.line((505,y,575,y),fill='#94b5bf',width=4)
        text(d,(540,y-57),'≠',46,INK,100)
    footer(im,tr(lang,'Показания Терри Джо противоречили рассказу Харви','Terry Jo’s testimony contradicted Harvey’s story'))
    return im

def render(lang,kind,p=1):
    T=lambda r,e:tr(lang,r,e)
    if kind=='rescue':return reconstruction(lang,'rescue',T('КАПИТАН НАЙДЕН ЖИВЫМ','THE CAPTAIN WAS FOUND ALIVE'))
    if kind=='captain':return archive(lang,'captain',T('ОН РАССКАЗАЛ О ШТОРМЕ','HE DESCRIBED A TERRIBLE STORM'))
    if kind=='lookout':return reconstruction(lang,'lookout',T('НО В ОКЕАНЕ БЫЛО КОЕ-ЧТО ЕЩЁ','BUT SOMETHING ELSE WAS OUT THERE'))
    if kind=='map':return geography(lang).copy()
    if kind=='family':return archive(lang,'family',T('СЕМЬЯ ДЮПЕРРО','THE DUPERRAULT FAMILY'),detail=T('Двое взрослых. Трое детей.','Two parents. Three children.'))
    if kind=='yacht':return archive(lang,'yacht',T('ЯХТА «БЛЮБЕЛЛ»','THE BLUEBELLE'),detail=T('Двухмачтовая яхта • около 18 м','A two-masted yacht • about 60 feet'))
    if kind=='night':return opening_dates(lang,0,p)
    if kind=='rescued_date':return opening_dates(lang,1,p)
    if kind=='storm':return reconstruction(lang,'storm',T('СЛОМАЛАСЬ МАЧТА. НАЧАЛСЯ ПОЖАР.','A BROKEN MAST. THEN A FIRE.'),T('ВЕРСИЯ КАПИТАНА','THE CAPTAIN’S ACCOUNT'))
    if kind=='raft':return archive(lang,'raft',T('16 НОЯБРЯ • НАХОДКА В МОРЕ','16 NOVEMBER • A DISCOVERY AT SEA'))
    if kind=='crew':return archive(lang,'crew',T('НА БОРТУ «КАПИТАН ТЕО»','ABOARD THE CAPTAIN THEO'),detail=T('Терри Джо • 11 лет','Terry Jo • 11 years old'))
    if kind=='survival':return survival(lang,p)
    if kind=='interview':return reconstruction(lang,'interview',T('ЕМУ СООБЩИЛИ: ОНА ЖИВА','HE WAS TOLD: SHE WAS ALIVE'),T('17 НОЯБРЯ 1961','17 NOVEMBER 1961'))
    if kind=='motel':return reconstruction(lang,'motel',T('ОН ВЕРНУЛСЯ В ГОСТИНИЦУ','HE RETURNED TO A MOTEL'))
    if kind=='chronology':return chronology(lang,p)
    if kind=='testimony':return archive(lang,'girl',T('ТЕРРИ РАССКАЗАЛА О ТОЙ НОЧИ','TERRY REMEMBERED THAT NIGHT'))
    if kind=='calm':return reconstruction(lang,'calm',T('МОРЕ БЫЛО СПОКОЙНЫМ','THE SEA WAS CALM'),T('ПОКАЗАНИЯ ТЕРРИ ДЖО','TERRY JO’S ACCOUNT'))
    if kind=='night_cabin':return reconstruction(lang,'night_cabin',T('ЕЁ РАЗБУДИЛИ КРИКИ','SCREAMS WOKE HER'),T('ПО РАССКАЗУ ТЕРРИ','BASED ON TERRY’S ACCOUNT'))
    if kind=='family_detail':return family_detail(lang)
    if kind=='cabin_route':return boat_scene(lang,0,p)
    if kind=='captain_route':return boat_scene(lang,1,p)
    if kind=='water':return reconstruction(lang,'cabin',T('ЯХТА НАЧАЛА ТОНУТЬ','THE YACHT BEGAN TO SINK'),T('ПО РАССКАЗУ ТЕРРИ','BASED ON TERRY’S ACCOUNT'))
    if kind=='escape':return boat_scene(lang,2,p)
    if kind=='paper':return newspaper(lang)
    if kind=='compare':return compare(lang,p)
    if kind=='medical':return archive(lang,'medical',T('ЕЁ УДАЛОСЬ СПАСТИ','SHE COULD STILL BE SAVED'))
    if kind=='ending':
        im=archive(lang,'recovery',T('ОНА ВЫЖИЛА. И РАССКАЗАЛА ПРАВДУ.','SHE SURVIVED. AND TOLD THE TRUTH.'))
        return im
    raise ValueError(kind)
