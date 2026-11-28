"""Assemble the fixed tribunal stage and animated deacon. Run after diorama.py."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
import math,json,subprocess
base=Path(__file__).resolve().parent
work=base/'court_frames'
stage=Image.open(work/'stage.png').convert('RGB')
stage=Image.blend(stage,stage.filter(ImageFilter.MedianFilter(3)),.76)
w,h=stage.size
poses=[Image.open(work/f'turn{j:02d}.png').convert('RGBA') for j in range(13)]
ax=json.loads((work/'anchors.json').read_text()); P=np.array(ax['presider']);D=np.array(ax['deacon'])
def ease(x):x=min(1.,max(0.,x));return x*x*(3-2*x)
def interp(a,b,t):return (1-t)*a+t*b
def bez(a,b,bend,t):return (1-t)**2*a+2*t*(1-t)*bend+t*t*b
def vec(v):return tuple(map(float,v))
def xy(x,y):return round(x),round(y)
stageRGBA=stage.convert('RGBA')
# Soft painted-in contact shadow anchors the composited, turning figure to the tiled pavement.
cast=Image.new('RGBA',(w,h))
sh=ImageDraw.Draw(cast)
x=float(D[0]);y=float(D[1])+130
sh.ellipse((x-35,y-6,x+39,y+8),fill=(12,15,13,120))
cast=cast.filter(ImageFilter.GaussianBlur(4))
stageRGBA.alpha_composite(cast)
# Frame the 3D model in a vertical editor-friendly image using the original room lighting and no labels.
def trace(frame,a,b,bend,phase,color):
 if not 0 < phase < 1:return
 k=ease(phase);fade=min(1,phase*10,(1-phase)*9)
 halo=Image.new('RGBA',(w,h));f=ImageDraw.Draw(halo)
 for q in range(29):
  start=max(0,k-.24);t0=start+(k-start)*q/29;t1=start+(k-start)*(q+1)/29;alpha=(.1+.86*(q+1)/29)*fade
  f.line([vec(bez(a,b,bend,t0)),vec(bez(a,b,bend,t1))],fill=(*color,int(150*alpha)),width=3)
 head=bez(a,b,bend,k)
 x,y=head;f.ellipse((x-4.7,y-4.7,x+4.7,y+4.7),fill=(*color,int(245*fade)))
 glow=halo.filter(ImageFilter.GaussianBlur(5));frame.alpha_composite(glow);frame.alpha_composite(halo)
 if fade>.1:
  d=ImageDraw.Draw(frame);d.ellipse((x-1.9,y-1.9,x+1.9,y+1.9),fill=(252,242,202,255))
# The living pope addresses his stand-in. The stand-in turns to the accused, then back to answer.
turnstart=.75;turnend=1.50;backstart=1.63;backend=2.39
for n in range(96):
 sec=n/30
 u=ease((sec-turnstart)/(turnend-turnstart))*(1-ease((sec-backstart)/(backend-backstart)))
 p=u*12;i=min(11,int(p));q=p-i
 layer=Image.blend(poses[i],poses[i+1],q) if q else poses[i]
 frame=stageRGBA.copy()
 frame.alpha_composite(layer,(int(w*.395),h-int(h*.56)))
 # Controls bow gently down toward the foreground, leaving faces clear.
 c=(P+D)*.5+np.array([-8,42])
 trace(frame,P,D,c,(sec-.13)/.91,(247,184,83))
 trace(frame,D+np.array([0,10]),P+np.array([0,7]),c+np.array([0,27]),(sec-2.09)/.88,(122,218,219))
 frame.convert('RGB').save(work/f'{n:03d}.jpg',quality=94,subsampling=0)
subprocess.run(['ffmpeg','-y','-loglevel','error','-threads','1','-framerate','30','-i',str(work/'%03d.jpg'),'-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(base/'court.part.mp4')],check=True)
(base/'court.part.mp4').replace(base/'court.mp4')
