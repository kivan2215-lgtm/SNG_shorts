"""Original illustrations and bilingual motion graphics for the Sleepify edit."""
from functools import lru_cache
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
SHEETS = {
    'A': 'listener band engineer tracklist cat airguitar',
    'B': 'loop sleeper dawn bouncer moderator removed',
    'C': 'royalties van doors gig star pluck',
    'D': 'solo drummer clock snore memo unplug',
}
LAYOUT = {key: (sheet, i) for sheet, names in SHEETS.items() for i, key in enumerate(names.split())}
keys = list(LAYOUT)
animated = {'solo', 'tracklist', 'clock', 'loop', 'removed', 'royalties', 'doors', 'snore'}
TEAL = '#91eed6'
MINT = '#d1fbac'
GOLD = '#ffd585'
PINK = '#ff879e'
CREAM = '#fff5dc'
INK = '#11282b'
STEEL = '#466463'


@lru_cache(None)
def font(size, family='sans'):
    name = {
        'sans': 'DejaVuSans-Bold',
        'mono': 'DejaVuSansMono-Bold',
        'plain': 'DejaVuSans',
        'serif': 'DejaVuSerif-Bold',
    }[family]
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + name + '.ttf', size)


@lru_cache(None)
def plate(key):
    sheet, i = LAYOUT[key]
    with Image.open(ROOT / (sheet + '.png')) as picture:
        w, h = picture.size
        col, row = i % 3, i // 3
        box = (col*w//3 + 4, row*h//2 + 4, (col+1)*w//3 - 4, (row+1)*h//2 - 4)
        tile = picture.crop(box).convert('RGB')
    if key=='band':
        # Present the group as a record sleeve: a full square, all players visible.
        base=Image.new('RGB',(720,1280),'#12383c')
        d=ImageDraw.Draw(base)
        for i in range(17):
            d.ellipse((-572+i*17,-440+i*16,1312-i*17,1402-i*16),outline='#1c484b',width=3)
        with Image.open(ROOT/'band_original.jpg') as source:
            original=source.convert('RGB').resize((710,554),Image.Resampling.LANCZOS)
        d.rectangle((0,194,719,769), fill='#ecdbbc')
        base.paste(original,(5,204))
        d.line((24,92,696,92),fill='#88a99c',width=2)
        d.text((29,809),'ROCKWOOD MUSIC HALL  /  NYC  /  2013',font=font(23,'mono'),fill=GOLD,anchor='lm')
        d.text((29,846),'EvanLBerent  ·  CC BY 2.0',font=font(20,'plain'),fill=CREAM,anchor='lm')
        d.line((24,865,696,865),fill='#88a99c',width=2)
        d.text((28,900),'VULFPECK',font=font(36),fill=CREAM,anchor='lm')

        return base
    return ImageOps.fit(tile, (720, 1280), method=Image.Resampling.LANCZOS)


def meter(draw, t):
    x, y = 68, 757
    draw.rounded_rectangle((x,y,x+284,y+74), 12, fill=INK, outline='#68827e', width=2)
    draw.text((x+18,y+17), 'VU', font=font(19,'mono'), fill=CREAM)
    for i in range(18):
        dx = x+58+i*11
        draw.rounded_rectangle((dx,y+20,dx+7,y+38), 2, fill=('#273f3d' if i < 13 else '#52383b'))
    c = TEAL if sin(pi*t*2) > -.35 else '#69a9a1'
    draw.ellipse((x+21,y+49,x+30,y+58),fill=c)
    draw.line((x+58,y+53,x+246,y+53), fill='#79978c', width=1)
    # The meter remains unlit; a transport lamp confirms the hypothetical solo is playing.


def draw(key, t, ru):
    img = plate(key).copy()
    if key not in animated:
        return img
    d = ImageDraw.Draw(img)
    t = min(1., max(0., t))
    tr = lambda a,b: a if ru else b

    def txt(x,y,s,size,fill=CREAM,family='sans',anchor='lm'):
        d.text((x,y), s, font=font(size,family), fill=fill, anchor=anchor)

    if key=='solo':
        meter(d, t)
    elif key=='tracklist':
        # Lay a complete studio cue sheet over the printed page in the studio scene.
        # Painting edge-to-edge inside the paper area keeps every signal trace flat.
        d.polygon(((-5,243),(724,240),(725,1123),(-5,1128)),fill='#e5c68f')
        for i in range(62):
            y=255+i*14
            d.line((0,y,720,y-4),fill='#d3b685',width=1)
        txt(51,322,'SLEEPIFY',53,INK)
        txt(665,325,'2014',26,INK,'mono','rm')
        txt(53,387,'VULFPECK',25,INK)
        txt(667,387,tr('10 ТРЕКОВ','10 TRACKS'),25,INK,'mono','rm')
        d.line((49,425,669,425),fill=INK,width=3)
        for i in range(10):
            y=465+i*41
            txt(53,y,f'{i+1:02}',22,INK,'mono')
            txt(118,y,'Z'+'z'*i,19,INK,'mono')
            x1,x2=280,666
            d.line((x1,y,x2,y),fill='#657876',width=2)
            if i==0:
                xpos=x1+round((x2-x1)*t)
                d.line((x1,y,xpos,y),fill='#174f52',width=4)
                d.line((xpos,y-9,xpos,y+9),fill='#a53136',width=3)
        txt(53,906,tr('ЗВУКОВОЙ СИГНАЛ','AUDIO SIGNAL'),20,INK,'mono')
    elif key=='clock':
        # A fixed waveform with a moving playhead communicates elapsed, silent audio.
        d.rounded_rectangle((53,620,653,847),15,fill='#142d33',outline='#77c8bc',width=2)
        txt(81,660,tr('ДЛИНА ТРЕКА','TRACK LENGTH'),23,CREAM)
        secs=30*min(1,t/.70) if t<=.70 else 30+(t-.70)/.30
        txt(624,665,f'00:{int(secs):02d}',39,MINT,'mono','rm')
        left, right, y=86, 616, 740
        for i in range(32):
            x=round(left+(right-left)*i/31)
            d.line((x,y-25 if i%5==0 else y-9,x,y+25 if i%5==0 else y+9),fill=STEEL,width=1)
        d.line((left,y,right,y),fill='#87a7a3',width=2)
        cursor=round(left+(right-left)*secs/31)
        d.line((left,y,cursor,y),fill=TEAL,width=3)
        d.polygon(((cursor-7,y-40),(cursor+7,y-40),(cursor,y-30)),fill=GOLD)
        d.line((cursor,y-30,cursor,y+28),fill=GOLD,width=3)
        txt(84,804,tr('ТИШИНА','SILENCE'),19,TEAL,'mono')
        txt(622,804,tr('ПОРОГ: 30 СЕК','30s TO COUNT') if secs<30 else tr('ПРОСЛУШИВАНИЕ ЗАСЧИТАНО','STREAM COUNTED'),19,MINT if secs>=30 else CREAM,'mono','rm')
    elif key=='loop':
        # Illustrate the whole album looping, with its ten tracks, rather than a single track on repeat.
        d.rounded_rectangle((58,686,644,844),14,fill='#18243b',outline='#91b9d7',width=2)
        txt(88,722,tr('АЛЬБОМ НА ПОВТОРЕ','REPEAT ALBUM'),25)
        d.rounded_rectangle((87,772,581,809),12,outline='#7392a5',width=2)
        focus=round(t*12)%10
        for i in range(10):
            x=113+i*45
            d.rounded_rectangle((x,780,x+27,801),3,fill=MINT if focus==i else '#3b5461')
        d.line((596,797,609,797,609,762,584,762),fill=TEAL,width=3)
        d.polygon(((581,762),(590,756),(590,768)), fill=TEAL)
    elif key=='removed':
        x,y=66,694
        d.rounded_rectangle((x,y,643,839),13,fill='#202c35',outline='#78878d',width=2)
        c=tuple(round(a+(b-a)*min(1,t*1.75)) for a,b in zip((255,213,133),(80,89,97)))
        d.rounded_rectangle((x+23,y+22,x+122,y+123),4,fill=c)
        for j in range(3):
            d.arc((x+38+j*6,y+39+j*6,x+105-j*6,y+105-j*6),20,320,fill='#394852',width=3)
        txt(214,738,'SLEEPIFY',33)
        txt(214,792,tr('СНЯТ С ПЛАТФОРМЫ','REMOVED FROM CATALOG'),24,PINK)
        amount=min(1,t*2)
        d.line((x+42,y+101,x+42+62*amount,y+101-59*amount),fill='#fff4dd',width=5)
    elif key=='royalties':
        d.rounded_rectangle((62,646,642,835),10,fill='#f2ddaf',outline='#654e39',width=3)
        d.line((90,716,614,716),fill='#998365',width=2)
        txt(92,683,tr('ДОХОД ОТ ПРОСЛУШИВАНИЙ','STREAMING ROYALTIES'),24,INK)
        ease=1-(1-min(1,t*1.85))**3
        amount=round(20000*ease / 100)*100
        number=f'{amount:,}'.replace(',',' ' if ru else ',')
        txt(355,774,'≈ $'+number,53,INK,'mono','mm')
    elif key=='doors':
        # Ticket with a perforated stub: the social outcome reads immediately.
        x=round(59-130*(1-min(1,t*3))**3)
        y=690
        d.rounded_rectangle((x,y,x+582,y+145),14,fill='#ffe1a0',outline='#a76949',width=3)
        for dy in range(13,136,15):
            d.line((x+438,y+dy,x+438,y+dy+6),fill='#896044',width=2)
        txt(x+30,y+40,'VULFPECK',21,INK,'mono')
        txt(x+30,y+93,tr('ВХОД СВОБОДНЫЙ','FREE ADMISSION'),33,INK)
        txt(x+509,y+73,'$0',42,INK,'mono','mm')
    elif key=='snore':
        # Deliberately distinguish a snore gag from the album's truly silent tracks.
        x,y=76,768
        d.rounded_rectangle((x,y,x+370,y+70),11,fill='#20283b',outline='#8291a5',width=2)
        txt(x+16,y+34,tr('ХРАП','SNORE'),19,CREAM,'mono')
        pts=[]
        for i in range(214):
            phase=i/213
            amp=(max(0,sin(phase*2*pi-1.3*pi*t)))**2*18
            pts.append((x+122+i,y+35+round(sin(phase*22*pi-t*5)*amp)))
        d.line(pts,fill='#b6e9cd',width=2)
    return img
