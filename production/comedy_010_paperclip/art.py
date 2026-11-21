from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageOps
import math
W,H=720,1280
ink='#103a43';paper='#fff1cb';gold='#efb34b';red='#b93637';mint='#a9dad0'
keys='globeowner clip fish knob stove flat alice landlord globe collector role desk'.split()
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',n)
@lru_cache(None)
def panel(k):
 if k in ('original','house','monument'):return Image.open(k+'.jpg').convert('RGB')
 i=keys.index(k);im=Image.open('A.png' if i<6 else 'B.png').convert('RGB');w,h=im.width//3,im.height//2;i%=6
 return im.crop((i%3*w+3,i//3*h+3,(i%3+1)*w-3,(i//3+1)*h-3))
@lru_cache(None)
def fit(k,w,h):return ImageOps.fit(panel(k),(w,h),centering=(.50,.43))
def put(d,x,y,s,n,c=paper):d.text((x,y),s,font=font(n),fill=c)
@lru_cache(None)
def still(k,ru):
 if k in ('original','house','monument'):
  im=Image.new('RGB',(W,H),ink);p=ImageOps.contain(panel(k),(W,752))
  im.paste(p,((W-p.width)//2,400-p.height//2));d=ImageDraw.Draw(im)
  label={'original':('Скрепка Кайла','Kyle’s paperclip'),'house':('Киплинг, Канада','Kipling, Canada'),'monument':('Киплинг','Kipling')}[k][0 if ru else 1]
  put(d,38,788,label,45);put(d,40,855,{'original':'Kyle MacDonald · CC BY 2.0','house':'OisinisiO · CC BY-SA 3.0','monument':'purecanucks · CC BY 2.0'}[k],24,mint);return im
 pairs={'globeowner':'alice','fish':'clip','knob':'fish','stove':'knob','flat':'stove','landlord':'alice','collector':'globe','role':'collector'}
 if k not in pairs:return fit(k,W,H)
 im=Image.new('RGB',(W,H),ink);im.paste(fit(k,W,850),(0,0));im.paste(fit(pairs[k],W,423),(0,857));return im
animated={'snow','trade','rent','choice','wire','last'}
def ease(t):
 t=min(1,max(0,t));return t*t*(3-2*t)
@lru_cache(58)
def wireframe(n):return Image.open('model/%04d.jpg'%n).convert('RGB').resize((720,803),Image.Resampling.LANCZOS)
def draw(k,t,ru):
 w=lambda a,b:a if ru else b
 if k not in animated:return still(k,ru)
 if k=='snow':
  im=fit('globe',W,H).copy();d=ImageDraw.Draw(im)
  for j in range(65):
   x=360+int(201*math.sin(j*4.97+t*(1+j%5)*1.3));y=290+(j*73+int(188*t*(1+j%2)))%380
   if ((x-358)/212)**2+((y-477)/216)**2<1:
    r=1+j%3;d.ellipse((x-r,y-r,x+r,y+r),fill=paper)
  return im
 im=Image.new('RGB',(W,H),ink);d=ImageDraw.Draw(im)
 if k=='wire':
  im.paste(wireframe(1+round(53*t)),(0,0));d.line((40,816,680,816),fill=red,width=6)
  put(d,37,839,w('14 обменов · 1 год','14 trades · 1 year'),53);return im
 pic={'trade':'stove','rent':'flat','choice':'alice','last':'desk'}[k]
 im.paste(fit(pic,W,706),(0,0))
 entries={'trade':(w('Плита','Camp stove'),w('Генератор','Generator')),
          'rent':(w('Год аренды','One year’s rent'),w('Встреча с Купером','Meet Alice Cooper')),
          'choice':(w('Встреча','An afternoon'),w('Снежный шар','Snow globe')),
          'last':(w('Скрепка','Paperclip'),w('Две бумажки','Two sheets of paper'))}
 for i,s in enumerate(entries[k]):
  y=724+i*84;x=round(38-745*(1-ease(3*t-i)));d.rounded_rectangle((x,y,x+645,y+67),9,fill=mint if i==0 else gold)
  put(d,x+21,y+7,('−  ' if i==0 else '+  ')+s,38,ink)
 return im
