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
from visuals import diagram,calendar,passage
G=Image.open(p/'recon.png').convert('RGB')
def recon(i,title):
 w,h=G.size;pic=G.crop((i*w//3+6,6,(i+1)*w//3-6,h-6));im=ImageOps.fit(pic,(1080,1920),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,0,1080,240),fill=(8,19,28,215));txt(d,(540,125),title,43);return im
scenes=[(0,photo('archive0.jpg',T('В ДОМЕ НАШЛИ ПОГИБШЕГО','A MAN WAS FOUND DEAD'))),(cue('А его','His younger'),recon(0,T('КУДА ИСЧЕЗ ЕГО БРАТ?','WHERE WAS HIS BROTHER?'))),(cue('Восемнадцать','Eighteen'),calendar(LANG,18)),(cue('Нью-Йорк','New York'),photo('archive3.jpg',T('НЬЮ-ЙОРК • 1947','NEW YORK • 1947'))),(cue('Внутри вещи','Inside belongings'),photo('archive2.jpg',T('ВЕЩИ ДО ПОТОЛКА','BELONGINGS PILED TO THE CEILING'))),(cue('Среди завалов','They find Homer'),photo('homer.jpg',T('ГОМЕР КОЛЛАЙЕР • ФОТО 1939','HOMER COLLYER • PHOTO: 1939'))),(cue('Но где','But where'),photo('langley.jpg',T('ЛЭНГЛИ • СПРАВА • ФОТО 1946','LANGLEY • RIGHT • PHOTO: 1946'))),(cue('Дом начинают','Workers begin'),photo('archive1.jpg',T('РАСЧИСТКА ДОМА И ПОИСКИ','CLEARING THE HOUSE, SEARCHING'))),(cue('Тысячи книг','Thousands of books'),recon(1,T('КНИГИ • ДЕТАЛИ • 14 ПИАНИНО','BOOKS • CAR PARTS • 14 PIANOS')))]
start=cue('Между вещами','Narrow tunnels');end=cue('Восьмого апреля','On April eighth')
# A factual progression of the search, without a false exact floor plan.
for t in np.arange(start,end,.3):scenes.append((float(t),passage(LANG,min(1,(t-start)/max(1,end-start-.3)))))
scenes += [(end,diagram(LANG,0)),(cue('Он мёртв','Dead'),diagram(LANG,0))]
start=cue('По версии полиции','Police believed');end=cue('Гомер остался','Homer was left')
for t in np.arange(start,end,.2):scenes.append((float(t),diagram(LANG,min(1,(t-start)/max(1,end-start-1)))))
scenes += [(end,recon(2,T('ГОМЕР ОСТАЛСЯ БЕЗ ПОМОЩИ','HOMER WAS LEFT WITHOUT HELP'))),(cue('Экспертиза','His death'),diagram(LANG,1)),(cue('Помощь была','Help was only'),diagram(LANG,1))]
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
 labels=[('{\\c&H0066DDFF&}'+z+'{\\c&H00FFFFFF&}') if z.strip('.,:!?') in ['ГОМЕР', 'ЛЭНГЛИ', 'ЛОВУШКУ', 'ТРИ', 'ВОСЕМНАДЦАТЬ', 'HOMER', 'LANGLEY', 'TRAP', 'EIGHTEEN', 'TEN'] else z for z in labels]
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
reveal=cue('Восьмого апреля','On April eighth')
music[(t>reveal-.6)&(t<reveal+.3)]=0
music[t>cue('Помощь была','Help was only')]*=.25
mix=np.clip(v.astype(float)/32768+music,-1,1)
with wave.open(str(p/'mix.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes((mix*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(p/'video.txt'),'-i',str(p/'mix.wav'),'-vf',f'fps=30,ass={p/"subtitles.ass"}','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(duration),'-movflags','+faststart',str(p/'SNG_023_Collyer_RU_PREVIEW.mp4')],check=True)
print('DURATION',duration,'SCENES',len(scenes))
