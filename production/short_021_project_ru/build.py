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
LANG='ru'
def T(ru,en):return ru if LANG=='ru' else en
def phrase(text):
 target=re.findall(r"[\w]+",text.lower());tokens=[]
 for w in words:
  for token in re.findall(r"[\w]+",w['text'].lower()):tokens.append((token,w['offset']/1e7))
 for i in range(len(tokens)-len(target)+1):
  if [z[0] for z in tokens[i:i+len(target)]]==target:return tokens[i][1]
 raise ValueError(text)
def cue(ru,en):return phrase(T(ru,en))
G=Image.open(p/'recon.png').convert('RGB')
def recon(i,title):
 w,h=G.size;x=(i%2)*w//2;y=(i//2)*h//3;pic=G.crop((x+5,y+5,x+w//2-5,y+h//3-5));im=ImageOps.fit(pic,(1080,1920),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,0,1080,240),fill=(8,19,28,215));txt(d,(540,125),title,43);return im
def evidence(stage):
 im,d=canvas(T('ЦИФРОВОЙ СЛЕД','THE DIGITAL TRAIL'))
 d.rounded_rectangle((150,340,930,770),25,fill='#14202b',outline='#8eacb7',width=10)
 d.rectangle((185,380,895,720),fill='#1b3c4a')
 txt(d,(540,485),T('КОМПЬЮТЕР','COMPUTER'),50);txt(d,(540,610),T('СОХРАНЁННЫЕ ДАННЫЕ','RECOVERED DATA'),34,color='#edc46a')
 d.polygon([(150,780),(930,780),(1000,835),(80,835)],fill='#7c929b')
 y=840+int(150*min(1,stage));d.line((540,840,540,y),fill='#f8ce65',width=12)
 if stage>.6:
  d.rounded_rectangle((160,1010,920,1300),25,fill='#224650',outline='#f8ce65',width=4)
  txt(d,(540,1100),T('БИТКОИН-ПЛАТЁЖ','BITCOIN PAYMENT'),48);txt(d,(540,1210),T('СВЯЗЬ С ЗАКАЗОМ УБИЙСТВА','LINK TO THE MURDER ORDER'),30)
 return im
def clues():
 im,d=canvas(T('ЧТО НЕ СХОДИЛОСЬ','WHAT DID NOT ADD UP'))
 for i,(h,b) in enumerate([(T('ЭМИ — ПРАВША','AMY WAS RIGHT-HANDED'),T('Оружие у левой руки','Gun by her left arm')),(T('ЭКСПЕРТИЗА','TOXICOLOGY'),T('В организме обнаружен препарат','A drug found in her system'))]):
  y=420+i*420;d.rounded_rectangle((75,y,1005,y+320),25,fill='#1e3d48',outline='#8d9f9b',width=4);txt(d,(540,y+95),h,48,color='#f4c96a');txt(d,(540,y+215),b,37)
 return im
scenes=[(0,recon(0,T('ФБР ПРЕДУПРЕДИЛО ЕЁ','THE FBI WARNED HER'))),(cue('Кто-то','Someone had'),photo('amy-allwine-training.jpg',T('ЗА ЕЁ УБИЙСТВО ЗАПЛАТИЛИ','SOMEONE PAID TO HAVE HER KILLED'))),(cue('Она не знала','She had no'),recon(3,T('КТО ХОТЕЛ ЕЁ СМЕРТИ?','WHO WANTED HER DEAD?'))),(cue('Миннесота','Minnesota'),photo('amy-allwine-training.jpg',T('ЭМИ ОЛЛВАЙН • МИННЕСОТА, 2016','AMY ALLWINE • MINNESOTA, 2016'))),(cue('Заказ нашли','The order'),recon(2,T('ЗАКАЗ В ДАРКНЕТЕ','A DARK WEB MURDER ORDER'))),(cue('После предупреждения','After the warning'),recon(1,T('КАМЕРЫ ДЛЯ ЗАЩИТЫ','CAMERAS FOR PROTECTION'))),(cue('и купила','and bought'),recon(5,T('КУПИЛИ ПИСТОЛЕТ','THEY BOUGHT A GUN'))),(cue('Затем пришли','Then anonymous'),recon(2,T('АНОНИМНЫЕ УГРОЗЫ','ANONYMOUS THREATS'))),(cue('Иначе','Otherwise'),photo('amy-allwine-training.jpg',T('УГРОЖАЛИ ЕЁ БЛИЗКИМ','HER LOVED ONES WERE THREATENED'))),(cue('Через несколько','Months later'),recon(3,T('ЗВОНОК В ПОЛИЦИЮ','A CALL TO POLICE'))),(cue('Рядом пистолет','with a gun'),recon(5,T('ВЕРСИЯ: САМОУБИЙСТВО','AN APPARENT SUICIDE'))),(cue('Но Эми','But Amy'),clues()),(cue('В её организме','A powerful drug'),photo('allwine-luminol-footsteps.jpg',T('КРИМИНАЛИСТЫ ИЩУТ СЛЕДЫ','FORENSIC EVIDENCE'))),(cue('Следователи поняли','Investigators suspected'),recon(3,T('СЦЕНУ МОГЛИ ПОДСТРОИТЬ','A POSSIBLY STAGED SCENE'))),(cue('Записи домашних','Home cameras'),recon(1,T('КАМЕРЫ НЕ ПОКАЗАЛИ ПОСТОРОННИХ','NO OUTSIDERS ON CAMERA'))),(cue('Тогда исследовали','Investigators examined'),recon(4,T('ПРОВЕРКА КОМПЬЮТЕРА','EXAMINING THE COMPUTER')))]
start=cue('И нашли','They found');end=cue('След привёл','The trail')
for t in np.arange(start,end,.2):scenes.append((float(t),evidence(min(1,(t-start)/2))))
scenes += [(end,recon(4,T('СЛЕД ПРИВЁЛ К БЛИЗКОМУ ЧЕЛОВЕКУ','THE TRAIL LED CLOSE TO HOME'))),(cue('Это был','Her husband Stephen'),photo('stephen-allwine-mug.jpg',T('ЕЁ МУЖ • СТИВЕН ОЛЛВАЙН','HER HUSBAND • STEPHEN ALLWINE'))),(cue('Сайт киллеров','The hitman'),recon(2,T('САЙТ КИЛЛЕРОВ — МОШЕННИЧЕСТВО','THE HITMAN SITE WAS A SCAM'))),(cue('И Стивен','So Stephen'),photo('allwine-interrogation.jpg',T('ОН УБИЛ ЭМИ САМ','HE KILLED AMY HIMSELF'))),(cue('Его признали','He was convicted'),photo('stephen-allwine-mug.jpg',T('ПРИЗНАН ВИНОВНЫМ В УБИЙСТВЕ','CONVICTED OF MURDER'))),(cue('А пистолет','The gun bought'),recon(5,T('КУПЛЕН ДЛЯ ЗАЩИТЫ','BOUGHT FOR PROTECTION'))),(cue('стал орудием','became the weapon'),photo('amy-allwine-training.jpg',T('ЭМИ ОЛЛВАЙН','AMY ALLWINE')))]
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
 labels=[('{\\c&H0066DDFF&}'+z+'{\\c&H00FFFFFF&}') if z.strip('.,:!?') in ['ВОСЕМЬ','ВЫЖИЛИ','СЛЕД','ОПЕКЕ','EIGHT','SURVIVED','SHOEPRINT','CUSTODY'] else z for z in labels]
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
reveal=cue('Это был','Her husband Stephen')
music[(t>reveal-.6)&(t<reveal+.3)]=0
music[t>cue('А пистолет','The gun bought')]*=.25
mix=np.clip(v.astype(float)/32768+music,-1,1)
with wave.open(str(p/'mix.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes((mix*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(p/'video.txt'),'-i',str(p/'mix.wav'),'-vf',f'fps=30,ass={p/"subtitles.ass"}','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(duration),'-movflags','+faststart',str(p/'SNG_021_Amy_Allwine_RU_PREVIEW.mp4')],check=True)
print('DURATION',duration,'SCENES',len(scenes))
