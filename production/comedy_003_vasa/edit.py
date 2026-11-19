from pathlib import Path
import sys,json,math,subprocess,functools
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance
from scipy.io.wavfile import write
L=sys.argv[1]; ru=L=='ru'; blocks=json.load(open(L+'.json'))
W,H=720,1280; tau=math.tau
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def F(n):return ImageFont.truetype(font,n)
pick=lambda a,b:a if ru else b
plan=[[(0,21),(pick(7,6),'crew'),(pick(13,16),1)],[(0,'roll'),(pick(6,9),'stop'),(pick(14,16),'sail')],[(0,4),(pick(8,9),3),(pick(11,12),11),(pick(14,16),10)],[(0,'sail'),(pick(3,7),'wind'),(pick(5,11),'flood'),(pick(11,17),'dist')],[(0,'court'),(pick(7,6),'crew'),(pick(13,11),17),(pick(20,21),1),(pick(27,27),'court')]]
@functools.lru_cache(None)
def photo(k):
 im=Image.open('art.png' if isinstance(k,str) else f'{k}.jpg').convert('RGB')
 if isinstance(k,str):
  j=['crew','stop','sail','court'].index(k);w,h=im.size;im=im.crop((w*(j%2)//2,h*(j//2)//2,w*(j%2+1)//2,h*(j//2+1)//2))
 return ImageOps.fit(im,(W,H),centering=(.52,.43))
# Model viewed across the hull; gunports drawn as openings in the sides.
ship=Image.new('RGBA',(560,560));d=ImageDraw.Draw(ship)
d.polygon([(64,181),(495,181),(489,258),(459,330),(392,396),(298,437),(262,437),(163,401),(94,322)],fill='#824932',outline='#ffc990',width=5)
d.polygon([(84,203),(477,203),(465,255),(433,323),(373,376),(280,417),(180,381),(116,310)],fill='#271f22')
for y,w in [(219,196),(273,180),(330,135)]:
 d.rounded_rectangle((280-w,y,280+w,y+9),radius=3,fill='#dda364')
 for x in range(280-w+18,280+w-10,37):d.line((x,y+9,x-7,y+34),fill='#92613e',width=4)
for x in (80,449):
 d.rectangle((x,242,x+29,262),fill='#f0a844');d.rectangle((x+2,245,x+26,259),fill='#132834')
d.line((279,182,279,60),fill='#ce9c6b',width=8);d.line((124,180,279,75,437,180),fill='#bc9372',width=3)
gradient=Image.fromarray(np.uint8(np.tile(np.linspace([20,47,55],[8,22,31],H)[:,None,:],(1,W,1))))
def diagram(kind,u):
 im=gradient.copy();dr=ImageDraw.Draw(im); u=min(1,u)
 for y in range(180,1000,80):dr.line((38,y,682,y),fill='#23434b')
 roll=kind=='roll';theta=(-15*math.sin(u*tau*1.5) if roll else -(4+16*u) if kind=='wind' else -20)
 layer=ship.copy();ld=ImageDraw.Draw(layer)
 if roll:
  offset=80*math.sin(u*tau*1.5)
  for j in range(6):
   x=int(180+offset+30*j);ld.ellipse((x-5,148,x+5,158),fill='#f5c47e');ld.line((x,159,x-2,172,x+6,179),fill='#f0d9b1',width=5);ld.line((x-2,171,x-9,180),fill='#f0d9b1',width=4)
 layer=layer.rotate(theta,Image.Resampling.BICUBIC)
 im.paste(layer,(80,320),layer)
 water=Image.new('RGBA',(W,H));wd=ImageDraw.Draw(water);level=642 if roll else 626 if kind=='wind' else 615-int(14*u)
 pts=[(x,level+4*math.sin(x*.021+u*4)) for x in range(0,W+5,4)];wd.polygon(pts+[(W,1000),(0,1000)],fill=(26,133,149,96));wd.line(pts,fill='#78d6d2',width=3)
 im=Image.alpha_composite(im.convert('RGBA'),water).convert('RGB');dr=ImageDraw.Draw(im)
 title=pick('ПЕРЕБЕЖКА','DECK RUN')+'  '+str(min(3,1+int(u*3)))+' / 3' if roll else pick('КРЕН','HEEL') if kind=='wind' else pick('ВОДА ВХОДИТ В ПОРТ','WATER ENTERS THE PORT')
 dr.text((360,825),title,font=F(34),anchor='mm',fill='#ffd18a')
 if kind=='flood':
  # The lowered starboard opening; draw inward flow from starboard.
  a=math.sin(u*8)*5;dr.line([(630,602),(575,611),(532,614),(492,610+a)],fill='#8ce5ec',width=7);dr.polygon([(487,611+a),(507,600+a),(506,621+a)],fill='#8ce5ec')
 return im
def distance(u):
 im=gradient.copy();d=ImageDraw.Draw(im);d.text((360,445),pick('ПЕРВЫЙ РЕЙС','MAIDEN VOYAGE'),anchor='mm',font=F(34),fill='#bde3dc')
 d.line((90,675,630,675),fill='#42656c',width=8)
 x=int(90+540*min(1,u*1.5));d.line((90,675,x,675),fill='#e7b975',width=10);d.ellipse((x-11,664,x+11,686),fill='#fff1bc')
 d.text((360,565),('≈ %.1f '%(1.3*min(1,u*1.5))).replace('.',',' if ru else '.')+pick('км','km'),font=F(78),anchor='mm',fill='white')
 return im
def stamp(t):
 n=round(100*t);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,DejaVu Sans,66,&H00FFFFFF,&H00FFFFFF,&H00101518,&H00101518,-1,0,0,0,100,100,0,0,1,5,1,2,85,125,325,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
shots=[];voice=[];offset=0;sr=48000
for i,b in enumerate(blocks):
 a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',f'{L}{i}.'+('wav' if ru else 'mp3'),'-ar',str(sr),'-ac','1','-f','f32le','-']),np.float32); voice.extend([a,np.zeros(6000)]);ts=b['times']; words=b['script']
 for j,k in plan[i]:shots.append((offset+(ts[j] if j else 0),k))
 j=0
 while j<len(words):
  end=min(len(words),j+4)
  for h in range(j+2,end):
   if words[h-1][-1] in '.!?':end=h;break
  if len(words)-end==1 and end-j<5:end+=1
  txt=' '.join(words[j:end]); size=60 if len(txt)>31 else 66
  txt=txt.replace('тридцать','{\\c&H006DDCFF&}тридцать{\\r}').replace('thirty','{\\c&H006DDCFF&}thirty{\\r}')
  head+=f'Dialogue: 0,{stamp(offset+ts[j])},{stamp(offset+ts[end])},Main,,0,0,0,,{{\\fs{size}}}{txt}\n';j=end
 offset+=(len(a)+6000)/sr
Path(L+'.ass').write_text(head);v=np.concatenate(voice);t=np.arange(len(v))/sr
m=np.zeros_like(t)
for j,start in enumerate(np.arange(.15,offset,.43)):
 sel=slice(int(sr*start),min(len(t),int(sr*(start+.38))));x=t[sel]-start;f=[146.83,220,164.81,196,130.81,220,174.61,196][j%8];m[sel]+=(np.sin(tau*f*x)+.28*np.sin(tau*2*f*x))*np.exp(-13*x)*(1-np.exp(-100*x))
m*=.065*np.sqrt(np.mean(v*v))/np.sqrt(np.mean(m*m));write(L+'mix.wav',sr,np.int16(np.clip(v+m,-.98,.98)*32767))
out='SNG_COMEDY_003_VASA_'+L.upper()+'.mp4'
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','30','-i','-','-i',L+'mix.wav','-vf',f'scale=1080:1920,ass={L}.ass','-af','loudnorm=I=-16:TP=-1.5:LRA=10','-c:v','libx264','-threads','2','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',out]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE);shots.append((offset,None))
for (a,k),(b,_) in zip(shots,shots[1:]):
 n=round(b*30)-round(a*30)
 if k in ['wind','flood','roll','dist']:
  for j in range(n):p.stdin.write((distance(j/max(n-1,1)) if k=='dist' else diagram(k,j/max(n-1,1))).tobytes())
 else:
  raw=photo(k).tobytes()
  for j in range(n):p.stdin.write(raw)
p.stdin.close();assert p.wait()==0
