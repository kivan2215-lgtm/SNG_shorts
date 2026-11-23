from PIL import Image, ImageDraw, ImageFont, ImageOps
from functools import lru_cache
import math
keys='climb wobble worry exterior reserve jam farmer drip dry aisle audit empty scale water taste clerk plumber pancake'.split()
animated={'wobble','reserve','drip','audit','empty','water','clerk','pancake'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+4,r*h//2+4,(c+1)*w//3-4,(r+1)*h//2-4)),(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def draw(k,t,ru):
 im=base(k).copy()
 if k not in animated:return im
 layer=Image.new('RGBA',(720,1280));d=ImageDraw.Draw(layer);u=min(t*1.8,1);u=u*u*(3-2*u);gold='#f5ad46';ink='#162c38';pale='#ffedc5'
 def txt(x,y,s,n=25,col=pale):d.text((x,y),s,font=font(n),fill=col,anchor='mm')
 def box():d.rounded_rectangle((60,699,660,864),20,fill=(12,34,46,233),outline='#d49e4e',width=2)
 def barrel(x,y,fill,tilt=0):
  item=Image.new('RGBA',(88,108));b=ImageDraw.Draw(item);b.rounded_rectangle((8,6,80,99),11,fill='#415867',outline=pale,width=3)
  if fill:b.rounded_rectangle((14,26,74,92),6,fill=fill)
  for z in [19,58,90]:b.line((8,z,79,z),fill='#9aabb0',width=2)
  layer.alpha_composite(item.rotate(tilt,Image.Resampling.BICUBIC),(x,y))
 if k=='wobble':
  box();barrel(136,733,None,10*math.sin(t*math.pi*3)*(1-t));txt(429,785,'ПУСТАЯ?' if ru else 'EMPTY?',36)
 elif k=='reserve':
  box();txt(360,728,'СТРАТЕГИЧЕСКИЙ ЗАПАС' if ru else 'STRATEGIC RESERVE')
  for i in range(5):barrel(129+92*i,752,gold if i<=u*5 else None)
 elif k in ['empty','water']:
  box();barrel(102,730,'#7cbfce' if k=='water' else None)
  txt(425,776,('ПУСТО' if ru else 'EMPTY') if k=='empty' else ('ВОДА' if ru else 'WATER'),38)
 elif k=='drip':
  for j in range(3):
   f=(t*2+j/3)%1;x=553;y=int(559+180*f*f);d.ellipse((x-6,y-10,x+6,y+7),fill=gold)
 elif k=='audit':
  box();txt(360,730,'ПО ОПИСИ' if ru else 'INVENTORY')
  for i in range(3):
   x=156+i*173;barrel(x-24,751,None)
   if u>(i+.4)/3:d.line([(x+21,807),(x+31,819),(x+55,783)],fill=gold,width=7)
 elif k=='clerk':
  box();txt(360,733,'СТОИМОСТЬ ДОБЫЧИ' if ru else 'VALUE OF THE HAUL');txt(360,802,'≈ '+format(round(18*u)*1000000,',').replace(',',' ')+' CAD',43,gold)
 else:
  box();txt(360,731,'ВЫДАЧА СОГЛАСОВАНА' if ru else 'WITHDRAWAL APPROVED')
  for j in range(2):d.ellipse((260,801+j*10,460,825+j*10),fill='#d79b55',outline=pale,width=2)
  y=755+int(59*min(1,t*2)**2);d.ellipse((352,y-9,368,y+6),fill='#ac5920')
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
