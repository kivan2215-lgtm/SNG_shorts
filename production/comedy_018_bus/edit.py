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
phrase_blocks = Path(L+"_phrases.txt").read_text().strip().split("\n\n")
from art import draw,animated
plan=[[(0,'finish'),(pick(7,6),'shock'),(pick(17,20),'passengers')],
[(0,'lake'),(pick(12,11),'pack'),(pick(16,16),'shoes'),(pick(27,25),'rider')],
[(0,'bus'),(pick(11,14),'driver')],
[(0,'return'),(7,'bronze'),(pick(25,18),'rival')],
[(0,'solo'),(pick(18,19),'vests'),(pick(25,27),'rear')],
[(0,'clipboard'),(4,'medal'),(pick(14,11),'bus')],
[(0,'shoes'),(pick(10,12),'podium')]]
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
 # Inspect 10 ms RMS windows before music is mixed in.
 a=a.copy()
 block=480
 levels=np.sqrt(np.mean(np.pad(a,(0,(-len(a))%block)).reshape(-1,block)**2,axis=1))
 quiet=levels<.0045
 bounds=np.where(np.diff(np.r_[False,quiet,False].astype(int)))[0].reshape(-1,2)
 cuts=[]
 for l,r in bounds:
  leading=l==0; trailing=r==len(levels)
  if (r-l)<(28 if leading or trailing else 69):continue
  start=0 if leading else l*block+(6 if trailing else 16)*block
  end=min(len(a),r*block) if trailing else r*block-(7 if leading else 17)*block
  if end>start:cuts.append((start,end))
 ts=[t-sum(max(0,min(t*sr,end)-start) for start,end in cuts)/sr for t in b['times']]
 parts=[];prev=0
 for start,end in cuts:
  part=a[prev:start].copy()
  fade=min(144,len(part))
  if fade:part[-fade:]*=np.linspace(1,0,fade)
  parts.append(part);a[end:end+144]*=np.linspace(0,1,len(a[end:end+144]));prev=end
 parts.append(a[prev:]);a=np.concatenate(parts)
 print(L,i,[(round(l/sr,2),round((r-l)/sr,2)) for l,r in cuts],flush=True)
 if ru:
  a=sosfilt(butter(2,65,fs=sr,btype='highpass',output='sos'),a)
  active=a[np.abs(a)>.018]
  if active.size:
   gain=np.clip(.13/(np.sqrt(np.mean(active*active))+1e-8),.84,1.20)
   a=a*gain
 voice.extend([a,np.zeros(6000)]); words=b['script']
 for j,k in plan[i]:shots.append((offset+(ts[j] if j else 0),k))
 j=0
 for phrase in phrase_blocks[i].split('|'):
  end=j+len(phrase.split())
  assert words[j:end]==phrase.split()
  txt=' '.join(words[j:end]); size=60 if len(txt)>31 else 66
  for term in ('третьим','пассажиров','автобус','third','fourth','bus'):
   txt=txt.replace(term,'{\\c&H006DDCFF&}'+term+'{\\r}')
  head+=f'Dialogue: 0,{stamp(offset+ts[j])},{stamp(offset+ts[end])},Main,,0,0,0,,{{\\fs{size}}}{txt}\n';j=end
 assert j==len(words)
 offset+=(len(a)+6000)/sr
Path(L+'.ass').write_text(head);v=np.concatenate(voice);t=np.arange(len(v))/sr
from mix import score
m=score(len(v),sr,shots,v)
write(L+'mix.wav',sr,np.int16(np.clip(v+m,-.98,.98)*32767))
out='SNG_COMEDY_018_BUS_'+L.upper()+ '.mp4'
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','30','-i','-','-i',L+'mix.wav','-vf',f'scale=1080:1920,ass={L}.ass','-af','highpass=f=60,equalizer=f=290:t=q:w=1.1:g=-1,equalizer=f=2900:t=q:w=1:g=1.2,loudnorm=I=-16:TP=-1.5:LRA=10','-c:v','libx264','-threads','2','-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',out]
import os
final=out
out=final[:-4]+'.'+str(os.getpid())+ '.mp4'
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
