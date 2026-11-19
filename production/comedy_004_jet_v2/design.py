from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from functools import lru_cache
from math import sin,cos,pi
import numpy as np
W,H=720,1280
@lru_cache(None)
def font(n,mono=False):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('Mono' if mono else '')+'-Bold.ttf',n)
def panel(d,box,color,r=15,outline=None):d.rounded_rectangle(box,r,fill=color,outline=outline,width=2)
@lru_cache(None)
def img(k):
 if k=='plane':return Image.open('harrier.jpg').convert('RGB')
 keys=['mail','school','calc','ocean','post','judge','gifts','agency','points','porch']
 i=keys.index(k);rows=3 if i<6 else 2;im=Image.open('a.png' if i<6 else 'b.png').convert('RGB');j=i if i<6 else i-6;w,h=im.size
 return im.crop((w*(j%2)//2+2,h*(j//2)//rows+2,w*(j%2+1)//2-2,h*(j//2+1)//rows-2))
@lru_cache(None)
def bg(theme):
 # Printed radial halftone, built once per palette.
 y,x=np.mgrid[0:H,0:W];light=np.exp(-((x-520)/620)**2-((y-360)/730)**2)
 colors={'blue':([11,20,41],[28,97,130]),'red':([71,19,36],[181,47,64]),'paper':([201,185,154],[249,235,202])}
 a,b=map(np.array,colors[theme]);arr=(a+(b-a)*light[:,:,None]);dots=((x%8<2)&(y%8<2))[:,:,None];arr*=1-.13*dots
 return Image.fromarray(arr.astype('uint8'))
def cover(im,w,h,c=.5):return ImageOps.fit(im,(int(w),int(h)),method=Image.Resampling.LANCZOS,centering=(c,.5))
@lru_cache(None)
def base(k):
 if k=='plane':
  im=bg('blue').copy();d=ImageDraw.Draw(im);asset=img(k).copy();asset.thumbnail((666,680));yy=560-asset.height//2
  panel(d,(20,yy-12,700,yy+asset.height+23),'#f7edd4');im.paste(asset,((720-asset.width)//2,yy))
  d.text((38,yy+asset.height+50),'AV-8B  /  HARRIER II',font=font(30,1),fill='#e6d6a3')
  return im
 if k=='tv' or k=='tag':
  im=bg('red' if k=='tv' else 'blue').copy();d=ImageDraw.Draw(im)
  panel(d,(13,242,708,860),'#231e27',48);panel(d,(23,227,698,842),'#e3d6b9',43,'#fde5c5');panel(d,(44,254,674,753),'#282830',27)
  im.paste(cover(img('school'),604,465),(58,268));d=ImageDraw.Draw(im)
  for x in range(65,330,10):d.line((x,786,x+3,811),fill='#726859',width=3)
  for x in [589,641]:d.ellipse((x-13,775,x+13,801),fill='#574e44',outline='#9c8d76',width=3);d.line((x,780,x+5,787),fill='#fff1c7',width=3)
  return im
 if k in ['math','bill','refund','law','credits']:return bg('paper' if k in ['bill','law'] else 'blue').copy()
 # Square artwork gets a clean full-bleed crop around the main subject.
 return cover(img('points' if k=='paper' else k),W,H,{'judge':.5,'mail':.48,'ocean':.49,'agency':.52}.get(k,.5))
def compose(k,u,ru):
 tr=lambda a,b:a if ru else b
 im=base(k).copy();d=ImageDraw.Draw(im)
 if k in ['tag','credits']:
  if k=='credits':im=base('tv').copy();d=ImageDraw.Draw(im)
  y=int(730-40*min(1,u*3));panel(d,(77,y,643,y+123),'#ffca58',11)
  d.text((360,y+42),'7 000 000',font=font(55,1),fill='#1a2834',anchor='mm')
  d.text((360,y+93),tr('БАЛЛОВ','POINTS'),font=font(29),fill='#8a3231',anchor='mm')
 if k=='math':
  panel(d,(47,252,672,855),'#102532',32,'#6396a3');panel(d,(70,278,649,446),'#c0d6a5',14)
  val=(tr('1 БАЛЛ','1 POINT') if u<.42 else '$0.10');d.text((360,362),val,font=font(74,1),fill='#18372c',anchor='mm')
  for idx,key in enumerate('789÷456×123−0.=+'):
   x=80+idx%4*144;y=479+idx//4*86;l=idx%4==3
   panel(d,(x,y,x+118,y+66),'#dd8d53' if l else '#35515b',10);d.text((x+59,y+31),key,font=font(34,1),fill='white',anchor='mm')
 if k in ['bill','refund']:
  slide=round((1-min(1,u*5))**2*140);y=330+slide
  panel(d,(33,y+12,697,y+455),'#706258',16);panel(d,(23,y,687,y+445),'#faf0d1',15)
  d.text((59,y+44),tr('РАСЧЁТ ЗАКАЗА','ORDER TOTAL'),font=font(35,1),fill='#1d5659')
  for i,(lab,val) in enumerate([(tr('Баллы','Points'),'6 999 985'),(tr('Цена балла','Per point'),'× $0.10'),(tr('Доставка','Handling'),'+ $10.00')]):
   a=y+122+i*65;d.text((59,a),lab,font=font(30),fill='#4a5552');d.text((651,a),val,font=font(30,1),fill='#283c41',anchor='ra')
  d.line((58,y+330,650,y+330),fill='#5d7a74',width=3);d.text((356,y+380),'$700,008.50',font=font(56,1),fill='#1e5150',anchor='mm')
  if k=='bill':
   step=min(1,int(u*4)/3); d.line((60,y+422,61+int(580*step),y+422),fill='#d99239',width=6)
  if k=='refund' and u>.16:panel(d,(115,611,608,731),'#bc433b');d.text((361,671),tr('ВОЗВРАТ','RETURNED'),font=font(55),fill='white',anchor='mm')
 if k=='law':
  x=45;y=276;panel(d,(x,y,675,872),'#fff8e9',8);d.rectangle((x,y,x+12,872),fill='#93383c')
  d.text((79,322),'U.S. DISTRICT COURT',font=font(29,1),fill='#815653');d.line((79,386,624,386),fill='#bcb1a3',width=2)
  d.multiline_text((79,423),'LEONARD\nv. PEPSICO',font=font(66),fill='#253a48',spacing=12)
  d.text((80,642),'88 F. Supp. 2d 116',font=font(30,1),fill='#535853');d.text((80,706),'1999',font=font(40),fill='#a94540')
 if k=='points':
  # Fifteen paper tokens, punched in three rows over the coupon-cutting scene.
  panel(d,(96,715,624,905),'#183949',18,'#e6c580')
  count=min(15,1+int(u*21))
  for h in range(15):
   xx=143+53*(h%5);yy=757+49*(h//5)
   d.ellipse((xx-18,yy-18,xx+18,yy+18),fill='#ddb75b' if h<count else '#45616b',outline='#dce3d0',width=2)
   if h<count:d.text((xx,yy),'1',font=font(20,1),fill='#24333a',anchor='mm')
  d.text((519,798),str(count)+'/15',font=font(34,1),anchor='mm',fill='#fff0bf')
 if k=='tv':
  # Brief analog scan during the ad cut, kept within the television screen.
  yy=269+int(u*454)
  overlay=Image.new('RGBA',im.size)
  od=ImageDraw.Draw(overlay);od.rectangle((59,yy,659,min(732,yy+12)),fill=(228,244,246,24))
  im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB')
 return im
