from pathlib import Path
import sys,json,math,subprocess,functools
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance
from scipy.io.wavfile import write
from scipy.signal import butter, sosfilt
L=sys.argv[1]; ru=L=='ru'; blocks=json.load(open(L+'.json'))
W,H=720,1280; tau=math.tau
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def F(n):return ImageFont.truetype(font,n)
pick=lambda a,b:a if ru else b
from pacing import tighten
from art import draw,animated
plan=[[(0,'salute'),(pick(7,11),'speech'),(pick(11,16),'whisper'),(pick(20,23),'prop')],
[(0,'hills'),(pick(4,3),'students'),(pick(10,12),'inventory'),(pick(22,32),'salute')],
[(0,'flight'),(pick(12,16),'students'),(pick(17,21),'prop'),(pick(23,28),'escort'),(pick(34,39),'close')],
[(0,'salute'),(pick(5,7),'palm'),(pick(14,15),'prop'),(pick(19,21),'whisper'),(pick(27,30),'speech'),(pick(32,34),'tram')],
[(0,'real'),(pick(13,12),'transit'),(pick(20,18),'cheers'),(pick(26,28),'exam'),(pick(30,31),'score')]]
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
 a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',f'{L}{i}.'+('wav' if ru else 'mp3'),'-ar',str(sr),'-ac','1','-f','f32le','-']),np.float32);  
 ts=b["times"]
 if ru:
  a,ts=tighten(a,ts,sr)
  a=sosfilt(butter(2,65,fs=sr,btype='highpass',output='sos'),a)
  active=a[np.abs(a)>.018]
  if active.size:
   gain=np.clip(.13/(np.sqrt(np.mean(active*active))+1e-8),.84,1.20)
   a=a*gain
 voice.extend([a,np.zeros(6000)]); words=b['script']
 for j,k in plan[i]:shots.append((offset+(ts[j] if j else 0),k))
 j=0
 while j<len(words):
  end=min(len(words),j+4)
  for h in range(j+2,end):
   if words[h-1][-1] in '.!?':end=h;break
  if len(words)-end==1 and end-j<5:end+=1
  txt=' '.join(words[j:end]); size=60 if len(txt)>31 else 66
  for term in ('трусы','трамвай','факел','экзамен','underpants','tram','torch','exam'):
   txt=txt.replace(term,'{\\c&H006DDCFF&}'+term+'{\\r}')
  head+=f'Dialogue: 0,{stamp(offset+ts[j])},{stamp(offset+ts[end])},Main,,0,0,0,,{{\\fs{size}}}{txt}\n';j=end
 offset+=(len(a)+6000)/sr
Path(L+'.ass').write_text(head);v=np.concatenate(voice);t=np.arange(len(v))/sr
from mix import score
m=score(len(v),sr,shots,v)
write(L+'mix.wav',sr,np.int16(np.clip(v+m,-.98,.98)*32767))
out='SNG_COMEDY_006_TORCH_'+L.upper()+'.mp4'
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','30','-i','-','-i',L+'mix.wav','-vf',f'scale=1080:1920,ass={L}.ass','-af','highpass=f=60,equalizer=f=290:t=q:w=1.1:g=-1,equalizer=f=2900:t=q:w=1:g=1.2,loudnorm=I=-16:TP=-1.5:LRA=10','-c:v','libx264','-threads','2','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',out]
import os
final=out
out=final[:-4]+'.'+str(os.getpid())+'.mp4'
cmd[-1]=out
p=subprocess.Popen(cmd,stdin=subprocess.PIPE);shots.append((offset,None))
for (a,k),(b,_) in zip(shots,shots[1:]):
 n=round(b*30)-round(a*30)
 if k in animated:
  for j in range(n):p.stdin.write(draw(k,j/max(n-1,1),ru).tobytes())
 else:
  raw=draw(k,1,ru).tobytes()
  for j in range(n):p.stdin.write(raw)
p.stdin.close();assert p.wait()==0

os.replace(out,final)
