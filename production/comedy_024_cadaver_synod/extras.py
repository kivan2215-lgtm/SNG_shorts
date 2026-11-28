from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageOps

EXTRAS = ('ordination', 'appointed', 'boss', 'sleeves', 'porto', 'guard')
ROOT=Path(__file__).resolve().parent

@lru_cache(None)
def extra(key):
    i=EXTRAS.index(key)
    with Image.open(ROOT/'E.png') as picture:
        w,h=picture.size
        col,row=i%3,i//3
        tile=picture.crop((col*w//3+3,row*h//2+3,(col+1)*w//3-3,(row+1)*h//2-3)).convert('RGB')
    return ImageOps.fit(tile,(720,1280),method=Image.Resampling.LANCZOS)

@lru_cache(None)
def court_labels(ru):
    from PIL import ImageDraw, ImageFont
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',23)
    overlay=Image.new('RGBA',(720,1280))
    pen=ImageDraw.Draw(overlay)
    for x,y,txt,line_col in ((149,818,'Стефан VI' if ru else 'Stephen VI','#ecb65b'),
                              (360,885,'Диакон' if ru else 'Deacon','#77d1d3'),
                              (553,818,'Формоз' if ru else 'Formosus','#bd99ca')):
        w=round(pen.textlength(txt,font=font)/2)+13
        pen.rounded_rectangle((x-w,y-19,x+w,y+18),radius=5,fill=(37,32,32,240),outline=line_col,width=2)
        pen.text((x,y),txt,font=font,fill='#fff5d8',anchor='mm')
    return overlay
