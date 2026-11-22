from PIL import Image,ImageOps,ImageDraw
from functools import lru_cache
keys='loss lawyers jet ads flex arena diploma robe dad grip victory coat deal press jar paperwork raise accountant'.split()
animated=set(keys)
@lru_cache(None)
def base(k):
 i=keys.index(k); im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+4,r*h//2+4,(c+1)*w//3-4,(r+1)*h//2-4)),(750,1334),method=Image.Resampling.LANCZOS)
def draw(k,t,ru):
 im=base(k);u=t*t*(3-2*t);x=round(15+10*(u-.5));y=round(10+23*u);return im.crop((x,y,x+720,y+1280))
