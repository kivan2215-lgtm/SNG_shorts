"""Illustrations for the spoken comic asides."""
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageOps

keys = ('meeting','courier','coupons','can','trailer','pancreas')

@lru_cache(None)
def plate(key):
    i=keys.index(key)
    with Image.open(Path(__file__).with_name('D.png')) as source:
        w,h=source.size
        x,y=i%3,i//3
        crop=source.crop((w*x//3+4,h*y//2+4,w*(x+1)//3-4,h*(y+1)//2-4)).convert('RGB')
    centering=(.84,.5) if key=="courier" else (.5,.5)
    return ImageOps.fit(crop,(720,1280),method=Image.Resampling.LANCZOS,centering=centering)

def counted(t,ru):
    from art import plate as base, font
    from PIL import ImageDraw
    im=base('points').copy()
    g=ImageDraw.Draw(im)
    g.rounded_rectangle((50,665,670,848),20,fill='#102349',outline='#fff3cb',width=2)
    g.text((360,711),'БАЛЛЫ В КОНВЕРТЕ' if ru else 'POINTS IN THE ENVELOPE',font=font(26),fill='#90d2ce',anchor='mm')
    n=min(15,round(15*min(1,t*2.5)))
    for i in range(15):
        x=82+i*38
        g.rounded_rectangle((x,759,x+27,799),4,fill='#ffd66d' if i<n else '#314262')
    g.text((360,823),str(n)+' / 15',font=font(22,True),fill='white',anchor='mm')
    return im
