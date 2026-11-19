from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageOps
import math
W,H=720,1280
names='salute whisper prop students flight escort palm speech tram real cheers exam'.split()
@lru_cache(None)
def font(n):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',n)
@lru_cache(None)
def panel(k):
 i=names.index(k);im=Image.open('A.png' if i<6 else 'B.png').convert('RGB');w,h=im.width//3,im.height//2;i%=6
 return im.crop((i%3*w+4,i//3*h+4,(i%3+1)*w-4,(i//3+1)*h-4))
ink='#103b3a';cream='#fff1cd';gold='#edb749';red='#ae4036'
@lru_cache(None)
def photo(k):
 if k=='hills':return Image.open('hills.jpg').convert('RGB')
 return panel(k)
@lru_cache(None)
def framed(k,ru):
 if k=='hills':
  im=Image.new('RGB',(W,H),ink);p=photo(k);p.thumbnail((660,760));im.paste(p,((W-p.width)//2,150));d=ImageDraw.Draw(im);d.text((48,178+p.height),'Пэт Хиллс' if ru else 'Pat Hills',font=font(55),fill=cream);return im
 pairs={'salute':'students','whisper':'palm','escort':'students','tram':'speech','real':'salute','cheers':'exam'}
 if k in pairs:
  im=Image.new('RGB',(W,H),ink)
  im.paste(ImageOps.fit(panel(k),(W,848),centering=(.42,.40)),(0,0))
  im.paste(ImageOps.fit(panel(pairs[k]),(W,426),centering=(.5,.34)),(0,854))
  return im
 return ImageOps.fit(panel(k),(W,H),centering=(.50,.45))
animated={'inventory','transit','score','close'}
def draw(k,t,ru):
 lang=lambda a,b:a if ru else b
 if k not in animated:return framed(k,ru)
 if k=='close':
  p=panel('escort');w,h=p.size
  return ImageOps.fit(p.crop((.12*w,.04*h,.91*w,.86*h)),(W,H))
 im=Image.new('RGB',(W,H),ink);d=ImageDraw.Draw(im)
 if k=='inventory':
  im.paste(ImageOps.fit(panel('prop'),(720,690)),(0,0))
  for i,(a,b) in enumerate([('Ножка стула','Chair leg'),('Банка пудинга','Pudding tin'),('Трусы','Underpants')]):
   if t+0.01>=i*.30:
    y=692+i*69;d.rectangle((0,y,720,y+67),fill=[cream,gold,red][i]);d.text((47,y+6),lang(a,b),font=font(41),fill=ink if i<2 else cream)
 elif k=='transit':
  im.paste(ImageOps.fit(panel('real'),(720,600)),(0,0))
  y=780;d.line((65,y,652,y),fill=gold,width=6)
  x=94+int(505*t);d.rounded_rectangle((x-48,y-58,x+48,y-4),10,fill=red,outline=cream,width=3)
  for i in (-33,-9,15):d.rectangle((x+i,y-48,x+i+16,y-31),fill=cream)
  for e in (-29,29):d.ellipse((x+e-7,y-9,x+e+7,y+5),fill=gold)
  d.text((40,657),lang('Барри уже в трамвае','Barry is already on the tram'),font=font(42),fill=cream)
 else:
  im.paste(ImageOps.fit(panel('exam'),(720,710)),(0,0))
  for i,(a,b,c,e) in enumerate([('Мэр','Mayor','СДАЛ','PASS'),('Экзамен','Exam','ПРОВАЛ','FAIL')]):
   if t+.01>=i*.42:
    y=723+i*83;d.text((42,y),lang(a,b),font=font(43),fill=cream);d.rounded_rectangle((330,y-2,661,y+62),7,fill=red if i else gold);d.text((355,y+2),lang(c,e),font=font(40),fill=cream if i else ink)
 return im
