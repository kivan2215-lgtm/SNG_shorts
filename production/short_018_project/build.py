from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance
import numpy as np,subprocess,json,math,wave,re,shutil
p=Path(__file__).parent;voice=p/'narration_full.wav'
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(voice),'-af','silencedetect=noise=-40dB:d=0.55','-f','null','-'],capture_output=True,text=True)
a=list(map(float,re.findall('silence_start: ([0-9.]+)',r.stderr)));b=list(map(float,re.findall('silence_end: ([0-9.]+)',r.stderr)));cuts=[(x+.34,y-.34) for x,y in zip(a,b) if y-x>.95]
subprocess.run(['ffmpeg','-y','-v','error','-i',str(voice),'-ar','48000','-ac','1',str(p/'original.wav')],check=True)
with wave.open(str(p/'original.wav')) as w:v=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
parts=[];last=0
for x,y in cuts:parts.append(v[last:round(x*48000)]);last=round(y*48000)
parts.append(v[last:]);v=np.concatenate(parts)
with wave.open(str(p/'voice.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(v.tobytes())
def remap(t):return t-sum(max(0,min(t,y)-x) for x,y in cuts if t>x)
words=json.loads((p/'boundaries.json').read_text());
for w in words:w['offset']=round(remap(w['offset']/1e7)*1e7)
duration=math.ceil(len(v)/1600)/30
(p/'edited_boundaries.json').write_text(json.dumps(words,ensure_ascii=False))
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def txt(d,xy,s,n=45,color='#f5f0e6',width=940):
 while max(ImageFont.truetype(font,n).getlength(x) for x in s.split('\n'))>width:n-=1
 d.multiline_text(xy,s,font=ImageFont.truetype(font,n),anchor='mm',align='center',fill=color,spacing=15)
def canvas(title):
 im=Image.new('RGB',(1080,1920),'#0b2029');d=ImageDraw.Draw(im);txt(d,(540,140),title,47);return im,d
def photo(name,title):
 pic=Image.open(p/name).convert('RGB')
 backdrop=Image.new('RGB',(1080,1920),'#182631')
 backdrop=ImageEnhance.Brightness(backdrop).enhance(.17)
 im=backdrop.copy();d=ImageDraw.Draw(im,'RGBA')
 d.rectangle((0,0,1080,220),fill=(8,28,38,210))
 pic=ImageOps.contain(pic,(1060,1540),Image.Resampling.LANCZOS)
 x=(1080-pic.width)//2;y=220+(1540-pic.height)//2
 im.paste(pic,(x,y))
 txt(d,(540,112),title,40)
 return im
def at(word,n=0):
 hits=[x['offset']/1e7 for x in words if x['text'].lower().strip('.,:!?«»')==word.lower()]
 return hits[n] if len(hits)>n else 0
def cue(word,n=0):return at(word,n)
def compare():
 im,d=canvas('1989 • СКУЛЬПТУРА И ФОТО ПОСЛЕ АРЕСТА')
 for name,x,label in [('a8.jpg',20,'БЮСТ БЕНДЕРА'),('a9.jpg',550,'ДЖОН ЛИСТ')]:
  pic=Image.open(p/name).convert('RGB')
  if name=='a9.jpg':pic=pic.crop((pic.width//2,0,pic.width,pic.height))
  pic=ImageOps.contain(pic,(510,1000));im.paste(pic,(x+(510-pic.width)//2,400));txt(d,(x+255,1320),label,29,width=490)
 return im
scenes=[(0,photo('a0.jpg','ПОЧТИ МЕСЯЦ ИГРАЛА МУЗЫКА')),(cue('но'),photo('a1.jpg','ХОЗЯЕВ НИКТО НЕ ВИДЕЛ')),(cue('там'),photo('a2.jpg','ПЯТЕРО ПОГИБШИХ')),(cue('нью-джерси'),photo('a0.jpg','НЬЮ-ДЖЕРСИ • 1971')),(cue('здесь'),photo('a3.jpg','СЕМЬЯ ЛИСТ')),(cue('погибли'),photo('a2.jpg','ОДИН ЧЕЛОВЕК ИСЧЕЗ')),(cue('доставку'),photo('a5.jpg','ДОСТАВКУ ПОЧТЫ ОСТАНОВИЛИ')),(cue('учителям'),photo('a2.jpg','ШКОЛЕ СООБЩИЛИ ОБ ОТЪЕЗДЕ')),(cue('музыка'),photo('a1.jpg','ДОМ КАЗАЛСЯ ЖИЛЫМ')),(cue('затем'),photo('a4.jpg','СЛЕДОВАТЕЛИ НАШЛИ ПИСЬМО')),(cue('хозяин'),photo('a6.jpg','ПРИЗНАНИЕ ДЖОНА ЛИСТА')),(cue('даже'),photo('a5.jpg','ОН УНИЧТОЖАЛ СЛЕДЫ')),(cue('годы'),photo('a7.jpg','РОЗЫСК ПО ВСЕЙ СТРАНЕ')),(47.7,photo('a7.jpg','1971 → 1989')),(cue('скульптор'),photo('a8.jpg','БЮСТ ФРЭНКА БЕНДЕРА')),(56.9,photo('a8.jpg','БЮСТ ПОКАЗАЛИ ПО ТЕЛЕВИЗОРУ')),(cue('бывшая'),photo('a8.jpg','СОСЕДКА УЗНАЛА «РОБЕРТА КЛАРКА»')),(62.5,photo('a7.jpg','ПРОВЕРКА ОТПЕЧАТКОВ')),(cue('это'),compare()),(cue('но',3),photo('a9.jpg','НОВАЯ ЖИЗНЬ ПОД ЧУЖИМ ИМЕНЕМ')),(73.4,photo('a10.jpg','ВТОРАЯ ЖЕНА НЕ ЗНАЛА ПРАВДЫ')),(cue('убил',1),photo('a11.jpg','ЕГО ПРЕЖНЯЯ СЕМЬЯ'))]
scenes=sorted([(t,im) for t,im in scenes if t>=0],key=lambda v:v[0])
manifest=[]
for i,(t,im) in enumerate(scenes):
 end=scenes[i+1][0] if i+1<len(scenes) else duration;f=p/f'card{i:02}.png';im.save(f);manifest.append(f"file '{f}'\noption framerate 30\nduration {end-t:.6f}\n")
manifest.append(f"file '{f}'\noption framerate 30\n");(p/'video.txt').write_text(''.join(manifest))
header=(p.parent/'short_004_juliane_v2/subtitles.ass').read_text().split('Dialogue:')[0]
def ts(t):return f'{int(t//3600)}:{int(t//60)%60:02}:{t%60:05.2f}'
import difflib
spoken=re.findall(r'«?[\w]+(?:-[\w]+)*[.,:!?»]*',(p/'narration.txt').read_text(),re.UNICODE)
def norm(x):return re.sub(r'[^\w-]','',x).lower()
matcher=difflib.SequenceMatcher(None,[norm(w['text']) for w in words],[norm(x) for x in spoken],autojunk=False)
for block in matcher.get_matching_blocks():
 for k in range(block.size):words[block.a+k]['display']=spoken[block.b+k]
sentences=[];sentence=[]
for w in words:
 sentence.append(w)
 if w.get('display',w['text']).rstrip('»').endswith(('.', '?','!')):sentences.append(sentence);sentence=[]
if sentence:sentences.append(sentence)
groups=[]
for sentence in sentences:
 while len(sentence)>5:
  n=3 if len(sentence)==6 else 4;groups.append(sentence[:n]);sentence=sentence[n:]
 if sentence:groups.append(sentence)
lines=[]
for index,g in enumerate(groups):
 a=g[0]['offset']/1e7;b=groups[index+1][0]['offset']/1e7 if index+1<len(groups) else duration
 labels=[x.get('display',x['text']).upper() for x in g];split=2 if len(labels)<5 else 3
 label=' '.join(labels[:split])+('\\N'+' '.join(labels[split:]) if len(labels)>split else '')
 lines.append(f'Dialogue: 0,{ts(a)},{ts(b)},S,,0,0,0,,{{\\pos(500,1510)}}{label}\n')
(p/'subtitles.ass').write_text(header+''.join(lines))
# A restrained, tonal minor-key score: warm dark chords, slow bell notes and a low heartbeat.
rate=48000;t=np.arange(len(v))/rate;music=np.zeros(len(v),dtype=np.float32)
chords=[(146.83,174.61,220.0),(116.54,146.83,174.61),(98.0,116.54,146.83),(110.0,138.59,164.81)]
for bar in range(int(duration//8)+1):
 start=bar*8;frequencies=chords[bar%4];a=int(start*rate);b=min(len(v),int((start+8)*rate))
 if a>=b:continue
 tt=np.arange(b-a,dtype=np.float32)/rate
 for f in frequencies:
  music[a:b]+=.0018*np.sin(2*np.pi*f*tt+0.1*bar).astype(np.float32)
for j,start in enumerate(np.arange(0,duration,1.75)):
 a=int(start*rate);b=min(len(v),a+int(1.6*rate));tt=np.arange(b-a,dtype=np.float32)/rate
 f=[293.66,261.63,233.08,220.0,174.61,164.81,146.83,138.59][j%8]
 bell=np.exp(-2.7*tt)*(np.sin(2*np.pi*f*tt)+.18*np.sin(2*np.pi*2*f*tt))
 music[a:b]+=.007*bell.astype(np.float32)
for start in np.arange(0,duration,.78):
 a=int(start*rate);b=min(len(v),a+int(.24*rate));tt=np.arange(b-a,dtype=np.float32)/rate
 music[a:b]+=(.008*np.exp(-22*tt)*np.sin(2*np.pi*55*tt)).astype(np.float32)
# The detective's clue briefly drops the score; the last question fades into quiet.
music*=np.minimum(np.maximum(t/1.5,0),1)*np.minimum(np.maximum((duration-t)/3,0),1)
music[(t>47)&(t<48)]=0
music[(t>77)&(t<79)]=0
mix=np.clip(v.astype(float)/32768+music,-1,1)
with wave.open(str(p/'mix.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes((mix*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(p/'video.txt'),'-i',str(p/'mix.wav'),'-vf',f'fps=30,ass={p/"subtitles.ass"}','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(duration),'-movflags','+faststart',str(p/'SNG_018_John_List_PREVIEW.mp4')],check=True)
print('DURATION',duration,'SCENES',len(scenes))
