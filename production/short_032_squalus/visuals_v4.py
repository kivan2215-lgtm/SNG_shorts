"""Physically shaded modeled Blender scenes plus narration-linked graphic annotations.

The camera, water, hatches, cable and people belong to the 3-D scene. Overlays
explain their changing states; they do not stand in for the physical mechanism.
"""
from pathlib import Path
from functools import lru_cache
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageColor
from visuals import render as archive_render, font, text, linearrow, ease, seg

P=Path(__file__).parent
V=P/'v4'
TAG_BOXES=[]
WHITE='#f5f3e9'; CYAN='#55dff3'; GOLD='#ffce71'; GREEN='#91efbb'; RED='#ff927f'
KINDS={'hero','question','dive','valve','flood','loss','sealed','depth','cable','dock','seal','drain','dry','open','transfer','rise','trips','saved','final'}

@lru_cache(32)
def index(k):return json.loads((V/'frames'/k/'index.json').read_text())

@lru_cache(1)
def shade():
    a=np.zeros((1920,1080,4),dtype=np.uint8)
    a[:,:,:3]=[4,14,22]
    y=np.arange(1920)
    alpha=np.maximum(np.clip((390-y)/210,0,1)*185,np.clip((y-1390)/410,0,1)*120)
    a[:,:,3]=alpha[:,None].astype(np.uint8)
    return Image.fromarray(a)

def mechanism_seg(p,a,b):
    q=max(0,min(1,(p-a)/(b-a)))
    return q*q*q*(q*(q*6-15)+10)

def tag(d,xy,label,col=WHITE,size=30,maxw=310):
    """A compact readable callout, with no full-width opaque information panels."""
    x,y=xy
    lines=label.split('\n');n=size
    while max(font(n).getlength(s) for s in lines)>maxw:n-=1
    w=max(font(n).getlength(s) for s in lines)+32;h=len(lines)*(n+9)+14
    TAG_BOXES.append((x-w/2,y-h/2,x+w/2,y+h/2))
    d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=13,fill='#102632',outline='#496473',width=2)
    text(d,(x,y-1),label,n,col,width=maxw)
    return (x,y+h/2)

def lead(d,xy,point,col=GOLD,p=1):
    start=xy;elbow=(xy[0],point[1]-36)
    def distance(b):return max(b[0]-xy[0],0,xy[0]-b[2])**2+max(b[1]-xy[1],0,xy[1]-b[3])**2
    if TAG_BOXES:
        b=min(TAG_BOXES,key=distance)
        if distance(b)<80**2:
            left,top,right,bottom=b;px,py=point
            if px>right+12:
                start=(right,max(top+10,min(bottom-10,py)));elbow=(max(right+24,px-40),start[1])
            elif px<left-12:
                start=(left,max(top+10,min(bottom-10,py)));elbow=(min(left-24,px+40),start[1])
            elif py<top:
                start=(max(left+10,min(right-10,xy[0])),top);elbow=(start[0],min(top-24,py+36))
            else:
                start=(max(left+10,min(right-10,xy[0])),bottom);elbow=(start[0],max(bottom+24,py-36))
    if p<=0:return
    x,y=point
    if p>=.995:
        linearrow(d,[start,elbow,point],1,col,3)
        d.ellipse((x-8,y-8,x+8,y+8),outline=col,width=3)
    else:
        # Component callouts fade in with their endpoint fixed on the component.
        pts=[start,elbow,point];ox=int(min(q[0] for q in pts))-24;oy=int(min(q[1] for q in pts))-24
        w=int(max(q[0] for q in pts))-ox+25;h=int(max(q[1] for q in pts))-oy+25
        layer=Image.new('RGBA',(w,h));ld=ImageDraw.Draw(layer);cc=(*ImageColor.getrgb(col),round(255*p))
        linearrow(ld,[(a-ox,b-oy) for a,b in pts],1,cc,3)
        ld.ellipse((x-ox-8,y-oy-8,x-ox+8,y-oy+8),outline=cc,width=3)
        d._image.paste(layer,(ox,oy),layer)

def head(d,title,sub=None):
    d.rounded_rectangle((64,166,115,173),radius=3,fill=GOLD)
    text(d,(66,203),title,44,WHITE,anchor='la',width=905)
    if sub:text(d,(66,270),sub,27,'#b1c7ce',anchor='la',width=905)

def stage(d,k,lang):
    names=['dock','seal','drain','dry','open','transfer']
    if k not in names:return
    active=names.index(k)
    for i in range(6):
        x=66+i*151
        d.rounded_rectangle((x,268,x+132,274),radius=3,fill=GREEN if i<active else GOLD if i==active else '#39535e')
    labels={'dock':('01  СТЫКОВКА','01  DOCKING'),'seal':('02  ГЕРМЕТИЧНЫЙ СТЫК','02  SEALED CONNECTION'),'drain':('03  УДАЛЕНИЕ ВОДЫ','03  DEWATERING'),'dry':('04  СУХОЙ ПРОХОД','04  DRY PASSAGE'),'open':('05  ОТКРЫТИЕ ЛЮКОВ','05  OPENING THE HATCHES'),'transfer':('06  ПЕРЕХОД ЛЮДЕЙ','06  PEOPLE TRANSFER')}
    text(d,(67,300),labels[k][lang=='en'],23,GOLD,anchor='la',width=890)

def render(lang,k,p=0,test=False):
    if k not in KINDS:return archive_render(lang,k,p)
    T=lambda a,b:a if lang=='ru' else b
    if test:
        im=Image.open(V/'tests'/f'{k}.jpg').convert('RGBA')
        anchors=json.loads((V/'tests'/f'{k}_anchors.json').read_text())
    else:
        meta=index(k);i=round(max(0,min(1,p))*(meta['count']-1))
        im=Image.open(V/'frames'/k/f'{i:04}.jpg').convert('RGBA');anchors=meta['anchors'][i]
    im=im.resize((1080,1920),Image.Resampling.LANCZOS)
    im=Image.alpha_composite(im,shade()).convert('RGB');d=ImageDraw.Draw(im);TAG_BOXES.clear()
    titles={
        'hero':T('ПОДЛОДКА НА ДНЕ.','A SUBMARINE ON THE SEABED.'),
        'question':T('КАК ОТКРЫТЬ ЛЮК ПОД ВОДОЙ?','HOW CAN THEY OPEN THE HATCH?'),
        'dive':T('ИСПЫТАТЕЛЬНОЕ ПОГРУЖЕНИЕ','A TEST DIVE'),
        'valve':T('КЛАПАН НЕ ЗАКРЫЛСЯ','THE VALVE FAILED TO CLOSE'),
        'flood':T('МОРЕ ВРЫВАЕТСЯ В ОТСЕКИ','SEAWATER FLOODS THE AFT SECTION'),
        'loss':T('26 ЧЕЛОВЕК ПОГИБЛИ','26 PEOPLE LOST THEIR LIVES'),
        'sealed':T('ПЕРЕБОРКА ОСТАНОВИЛА ВОДУ','A BULKHEAD HELD BACK THE WATER'),
        'depth':T('ДО ПОВЕРХНОСТИ — 74 МЕТРА','243 FEET BELOW THE SURFACE'),
        'cable':T('ВОДОЛАЗ ЗАКРЕПЛЯЕТ ТРОС','THE DIVER ATTACHES A CABLE'),
        'dock':T('КАМЕРА ОПУСКАЕТСЯ НА ЛЮК','THE CHAMBER MEETS THE HATCH'),
        'seal':T('МОРЕ ОСТАЁТСЯ СНАРУЖИ','KEEPING THE SEA OUT'),
        'drain':T('СНАЧАЛА НУЖНО УБРАТЬ ВОДУ','FIRST, REMOVE THE WATER'),
        'dry':T('ПРОХОД ТЕПЕРЬ СУХОЙ','THE PASSAGE IS NOW DRY'),
        'open':T('ТОЛЬКО ТЕПЕРЬ — ОТКРЫТЬ','ONLY NOW CAN THE HATCHES OPEN'),
        'transfer':T('ИЗ ПОДЛОДКИ — В КАМЕРУ','FROM SUBMARINE TO CHAMBER'),
        'rise':T('ПОДЪЁМ К ПОВЕРХНОСТИ','BACK TOWARD THE SURFACE'),
        'trips':T('ЧЕТЫРЕ СПАСАТЕЛЬНЫХ РЕЙСА','FOUR RESCUE TRIPS'),
        'saved':T('33 ИЗ 33 СПАСЕНЫ','ALL 33 RESCUED'),
        'final':T('ВЫХОД ДОСТАВИЛИ НА ДНО','THEY BROUGHT THE WAY OUT DOWN')}
    subs={
        'hero':T('ВНУТРИ ОСТАЮТСЯ ЖИВЫЕ ЛЮДИ','PEOPLE ARE STILL ALIVE INSIDE'),
        'flood':T('НОС СЛЕВА • КОРМА СПРАВА','BOW LEFT • STERN RIGHT'),
        'loss':T('ЗАТОПЛЕННЫЕ КОРМОВЫЕ ОТСЕКИ','THE FLOODED AFT COMPARTMENTS'),
        'question':T('СНАРУЖИ ВОДА. ВНУТРИ — ЛЮДИ.','WATER OUTSIDE. PEOPLE INSIDE.'),
        'depth':T('САМОСТОЯТЕЛЬНО НЕ ВЫБРАТЬСЯ','THEY CANNOT ESCAPE ON THEIR OWN')}
    head(d,titles[k],subs.get(k));stage(d,k,lang)

    if k=='hero':
        tag(d,(540,560),T('33 ЧЕЛОВЕКА В ЛОВУШКЕ','33 PEOPLE TRAPPED'),GOLD,40,840)
        lead(d,(400,605),anchors['hatch'],GOLD,seg(p,.05,.6))
    elif k=='question':
        tag(d,(530,495),T('ДАВЛЕНИЕ МОРЯ','PRESSURE FROM THE SEA'),CYAN,33,760)
        tag(d,(530,1290),T('ЛЮК ЗАКРЫТ','HATCH CLOSED'),GOLD,33,760)
        lead(d,(530,1240),anchors['hatch'],GOLD,seg(p,.1,.6))
    elif k=='dive':
        linearrow(d,[(785,490),(785,755)],seg(p,.05,.7),CYAN,7)
        tag(d,(430,560),T('ПОГРУЖЕНИЕ','DESCENDING'),CYAN,36,530)
    elif k=='valve':
        tag(d,(275,520),T('ОСТАЛСЯ\nОТКРЫТ','STUCK\nOPEN'),GOLD,31,290)
        lead(d,(275,570),anchors['valve'],GOLD,seg(p,.05,.6))
        linearrow(d,[(842,665),(842,1210)],seg(p,.1,.9),CYAN,7)
        tag(d,(775,1290),T('ВОДА ВНУТРЬ','WATER ENTERS'),CYAN,29,380)
    elif k in ['flood','loss']:
        tag(d,(270,600),T('СУХИЕ ОТСЕКИ','DRY SECTION'),GOLD,29,370)
        lead(d,(270,630),anchors['fore'],GOLD,seg(p,0,.35))
        tag(d,(760,650),T('ЗАТОПЛЕНИЕ','FLOODING') if k=='flood' else T('26 ПОГИБШИХ','26 LIVES LOST'),CYAN if k=='flood' else RED,30,380)
        lead(d,(760,680),anchors['aft'],CYAN if k=='flood' else RED,seg(p,.1,.5))
        if k=='flood':
            linearrow(d,[(630,740),(710,850),(730,980)],seg(p,.08,.9),CYAN,6)
            tag(d,(520,1290),T('УРОВЕНЬ ВОДЫ РАСТЁТ','THE WATER LEVEL RISES'),CYAN,30,790)
    elif k=='sealed':
        tag(d,(300,1300),T('СУХОЙ ОТСЕК','DRY SECTION'),GOLD,30,400)
        tag(d,(780,1300),T('ЗАТОПЛЕНО','FLOODED'),CYAN,30,330)
        tag(d,(540,520),T('ВОДОНЕПРОНИЦАЕМАЯ ДВЕРЬ','WATERTIGHT DOOR'),GREEN,31,800)
        lead(d,(540,552),anchors['door'],GREEN,seg(p,.1,.65))
    elif k=='cable':
        tag(d,(270,530),T('НАПРАВЛЯЮЩИЙ\nТРОС','GUIDE\nCABLE'),GOLD,32,350)
        lead(d,(270,580),anchors['cable'],GOLD,seg(p,.1,.6))
        tag(d,(710,1280),T('КРЕПЛЕНИЕ У ЛЮКА','ATTACHED AT THE HATCH'),GREEN,28,490)
        lead(d,(710,1235),anchors['hatch'],GREEN,seg(p,.35,.9))
    elif k=='dock':
        linearrow(d,[(915,650),(915,1150)],seg(p,.03,.75),GOLD,5)
        tag(d,(180,1110),T('ТОЧКА\nСТЫКОВКИ','DOCKING\nPOINT'),GOLD,32,225)
        lead(d,(180,1150),anchors['seal'],GOLD,seg(p,.25,.9))
    elif k=='seal':
        lead(d,(790,1280),anchors['seal'],GREEN,seg(p,.1,.6))
        tag(d,(790,1320),T('РЕЗИНОВОЕ\nКОЛЬЦО','RUBBER\nSEAL'),GREEN,32,260)
        # Flow terminates outside the steel skirt, not through the dry passage.
        linearrow(d,[(950,990),(870,990)],seg(p,.1,.65),CYAN,6)
    elif k=='drain':
        level=1-mechanism_seg(p,.28,.93)
        x,y,w,h=880,920,32,265
        d.rounded_rectangle((x,y,x+w,y+h),radius=10,fill='#102632',outline='#8bb8c3',width=2)
        if level>.01:d.rounded_rectangle((x+4,y+4+(h-8)*(1-level),x+w-4,y+h-4),radius=5,fill=CYAN)
        status=T('ВЕНТИЛЬ\nОТКРЫВАЕТСЯ','OPENING\nTHE VALVE') if p<.28 else T('ВОДА\nУХОДИТ','WATER\nLEAVING') if p<.93 else T('ВОДА\nУДАЛЕНА','WATER\nREMOVED')
        tag(d,(810,1260),status,CYAN,32,380)
        linearrow(d,[(755,1020),(820,1020),(820,1170)],seg(p,.28,.93),CYAN,5)
    elif k in ['dry','open','transfer']:
        tag(d,(177,1060),T('СУХОЙ\nПРОХОД','DRY\nPASSAGE'),GREEN,32,235)
        lead(d,(285,1060),anchors['path'],GREEN,seg(p,.04,.45))
        if k=='open':
            tag(d,(855,1330),T('ОТКРЫТИЕ\nЛЮКОВ','HATCHES\nOPENING') if p<.85 else T('ДВА ЛЮКА\nОТКРЫТЫ','BOTH HATCHES\nOPEN'),GOLD,30,300)
        if k=='transfer':
            linearrow(d,[(900,1240),(900,760)],seg(p,.02,.93),GREEN,6)
    elif k in ['depth','rise','trips','saved','final']:
        # A shared vertical reference system remains fixed across the overview.
        top,bottom=anchors['surface'][1],anchors['bottom'][1]
        x=925
        d.line((x,top,x,bottom),fill='#5b8290',width=3)
        for q,label in [(0,'0'),(.27,'20' if lang=='ru' else '65'),(.54,'40' if lang=='ru' else '130'),(.81,'60' if lang=='ru' else '195'),(1,'74' if lang=='ru' else '243')]:
            q=float(label)/(74 if lang=='ru' else 243)
            yy=top+(bottom-top)*q;d.line((x-11,yy,x+11,yy),fill=CYAN,width=3)
            d.text((x-23,yy),label,font=font(23),fill=WHITE,anchor='rm',stroke_width=2,stroke_fill='#0a1d29')
        tag(d,(825,top-55),T('МЕТРЫ','FEET'),CYAN,23,180)
        if k=='depth':
            text(d,(500,770),T('74 м','243 ft'),112,CYAN,width=650)
            linearrow(d,[(700,460),(700,1220)],seg(p,.02,.92),GOLD,6)
            tag(d,(450,980),T('ПОДЛОДКА НА ДНЕ','SUBMARINE ON THE SEABED'),WHITE,29,650)
        elif k=='rise':
            linearrow(d,[(600,1160),(600,550)],seg(p,.05,.9),GREEN,6)
            tag(d,(590,910),T('ЛЮДИ В КАМЕРЕ','PEOPLE IN THE CHAMBER'),GREEN,30,500)
        elif k=='trips':
            for i in range(4):
                on=p>i/4;y=640+i*130;c=GREEN if on else '#59717b'
                d.ellipse((480,y-28,536,y+28),fill=c)
                text(d,(508,y),str(i+1),30,'#102632',width=50)
                text(d,(575,y),T('РЕЙС','TRIP'),34,WHITE if on else '#96adb6',anchor='lm',width=240)
                if on:linearrow(d,[(730,y+18),(760,y-18)],1,GREEN,4)
        elif k=='saved':
            text(d,(530,690),'33 / 33',103,GREEN,width=690)
            text(d,(530,800),T('ВЕРНУЛИСЬ ЖИВЫМИ','BROUGHT UP ALIVE'),33,WHITE,width=720)
            # Each of 33 marks corresponds to one rescued person, not trip capacity.
            for i in range(33):
                x=310+(i%11)*43;y=910+(i//11)*62
                d.ellipse((x-7,y-20,x+7,y-6),fill=GREEN)
                d.rounded_rectangle((x-9,y-3,x+9,y+22),radius=5,fill=GREEN)
        else:
            text(d,(620,755),'33',125,GREEN,width=300)
            text(d,(620,875),T('СПАСЁННЫЕ ЖИЗНИ','LIVES SAVED'),29,WHITE,width=430)
            linearrow(d,[(715,1190),(715,980)],seg(p,.05,.7),GREEN,6)
    return im
