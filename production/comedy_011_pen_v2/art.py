from PIL import Image, ImageDraw, ImageFont, ImageOps
from functools import lru_cache
from pathlib import Path
import math
panels={'macro':0,'press':1,'look':2,'hands':3,'jacket':4,'palms':5,'salad':6,'news':7,'internet':8,'official':9,'post':10,'cookies':11,'meatball':12,'mother':13,'camera':14,'home':15,'mail':16,'sack':17}
@lru_cache(None)
def panel(k):
    i=panels[k]; sheet=Image.open(['A.png','B.png','C.png'][i//6]).convert('RGB')
    col=i%3; row=i%6//3; w,h=sheet.size
    return sheet.crop((round(col*w/3)+4,round(row*h/2)+4,round((col+1)*w/3)-4,round((row+1)*h/2)-4))
def fit(im,size):return ImageOps.fit(im,size,method=Image.Resampling.LANCZOS)
@lru_cache(None)
def base(k):return fit(panel(k),(720,1280))
@lru_cache(None)
def renderframe(n):return Image.open(f'model/{n:04d}.jpg').convert('RGB')
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
animated={'open','close','take','stamp','internet','receipt'}
def draw(k,t,ru):
    if k in ('open','close','take'):
        a,b={'open':(1,25),'take':(25,44),'close':(45,65)}[k]
        fr=renderframe(round(a+(b-a)*t))
        canvas=base('macro' if k=='open' else 'hands').copy()
        enlarged=fr.resize((720,666),Image.Resampling.BICUBIC)
        canvas.paste(enlarged,(0,250))
        return canvas
    if k=='archive':
        im=base('press').copy(); orig=Image.open('archive.jpg').convert('RGB'); orig.thumbnail((720,900))
        y=(1280-orig.height)//2-85; d=ImageDraw.Draw(im); d.rectangle((0,y-6,720,y+orig.height+36),fill='#201c24'); im.paste(orig,((720-orig.width)//2,y));d.text((20,y+orig.height+5),'Chile presidency agency · CC BY 3.0 CL',font=font(17),fill='white');return im
    im=base({'stamp':'official','receipt':'cookies'}.get(k,k)).copy()
    if k=='receipt':
        d=ImageDraw.Draw(im); x=round(60-460*(1-min(1,t*3))**2);y=690
        d.rounded_rectangle((x,y,x+570,y+138),radius=10,fill='#fff2cf',outline='#53384a',width=4)
        d.text((x+24,y+15),'ЗАЯВКА НА ПЕЧЕНЬЕ' if ru else 'BISCUIT REQUEST',font=font(31),fill='#542a38')
        d.text((x+24,y+76),'Количество: 1 шт.' if ru else 'Quantity requested: 1',font=font(25),fill='#26483c')
    if k=='stamp':
        d=ImageDraw.Draw(im); y=round(725+75*(1-min(1,t*5))**2); label='ПОДАРОК' if ru else 'A GIFT'; d.rounded_rectangle((145,y,575,y+90),radius=14,fill='#185848',outline='#ffe8a9',width=4);d.text((360,y+45),label,font=font(50),fill='#ffedcc',anchor='mm')
    if k=='internet':
        d=ImageDraw.Draw(im); d.arc((195,405,485,680),-85,-84+round(345*min(t*2,1)),fill='#eb5340',width=7)
    return im
