"""One source project, two independent narration/caption timelines."""
from pathlib import Path
import sys, json, re, math, subprocess, wave, difflib
import numpy as np
from PIL import Image,ImageDraw
from visuals import render,font

ROOT=Path(__file__).parent
LANG=sys.argv[1] if len(sys.argv)>1 else 'ru'
P=ROOT/LANG; P.mkdir(exist_ok=True)
WORDS=json.loads((P/'words.json').read_text())
# Some TTS word events contain two words. Preserve their interval and divide only
# that grouped event proportionally for caption grouping; record this explicitly.
expanded=[];grouped=[]
for w in WORDS:
 parts=w['text'].split()
 if len(parts)>1:
  grouped.append(w);total=sum(len(x) for x in parts);at=w['start']
  for part in parts:
   end=at+(w['end']-w['start'])*len(part)/total
   expanded.append(dict(w,text=part,start=at,end=end));at=end
 else:expanded.append(w)
WORDS=expanded
(P/'caption_grouped_events.json').write_text(json.dumps(grouped,ensure_ascii=False,indent=2))

T=lambda ru,en:ru if LANG=='ru' else en
def tokens(s):return re.findall(r"\w+(?:[’']\w+)*",s.lower())
flat=[]
for w in WORDS:
    for x in tokens(w['text']):flat.append((x,w['start']))
def cue(ru,en):
    needle=tokens(T(ru,en))
    hits=[flat[i][1] for i in range(len(flat)-len(needle)+1) if [a for a,b in flat[i:i+len(needle)]]==needle]
    if len(hits)!=1:raise ValueError((LANG,T(ru,en),hits))
    return hits[0]
with wave.open(str(P/'voice.wav')) as w:
    voice=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype('float32')/32768
    assert w.getframerate()==48000
DURATION=math.ceil((len(voice)/48000+.28)*30)/30
SCENES=[
(0,'hold'),
(cue('Остальная часть','The rest'),'outside'),
(cue('На высоте','More than'),'height'),
(cue('Втащить','They could not'),'grip'),
(cue('Но экипаж','But the crew'),'braced'),
(cue('Англия','England'),'date'),
(cue('Самолёт летел','The plane was flying'),'normal'),
(cue('Вдруг левое','Suddenly'),'blow'),
(cue('Командира Тима','Captain Tim'),'ejected'),
(cue('Бортпроводник успел','A flight attendant grabbed'),'grab'),
(cue('На помощь','His colleagues'),'help'),
(cue('Второй пилот','The copilot'),'copilot'),
(cue('и искал аэродром','and searched for an airport'),'airport'),
(cue('Ветер','Wind'),'radio'),
(cue('Руки спасателей','The rescuers'),'numb'),
(cue('Экипаж почти','The crew feared'),'believed'),
(cue('Но продолжали','But they kept'),'holding'),
(cue('И при снижении','During the descent'),'kick'),
(cue('Он был жив','He was alive'),'alive'),
(cue('Около двадцати','They held him outside'),'duration'),
(cue('Самолёт сел','Then the plane landed'),'landing'),
(cue('Все восемьдесят','All eighty'),'survived'),
(cue('Но почему','But why'),'why'),
(cue('Следователи обнаружили','Investigators found'),'evidence'),
(cue('Окно недавно','The window had recently'),'repair'),
(cue('Из девяноста','Of its ninety'),'ninety'),
(cue('восемьдесят четыре','eighty four were'),'thin'),
(cue('Всего на','By just'),'difference'),
(cue('Остальные шесть','The other six'),'short'),
(cue('Давление внутри','Pressure inside'),'pressure'),
(cue('В отчёте','The report'),'report'),
(cue('но и на недостатки','and failures of oversight'),'oversight'),
(cue('Неверно подобранный','A tiny mismatch'),'stakes'),
(cue('Это вина','Was this'),'mechanic'),
(cue('Или системы','Or a system'),'end')
]
SCENES=[(round(t*30)/30,k) for t,k in SCENES]
assert all(b[0]>a[0] for a,b in zip(SCENES,SCENES[1:]))
manifest=[]
for i,(start,kind) in enumerate(SCENES):
    end=SCENES[i+1][0] if i+1<len(SCENES) else DURATION
    manifest.append({'start':start,'end':end,'visual':kind})
(P/'timeline.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))

def make_subtitles():
    script=(P/'narration.txt').read_text()
    # Recover original punctuation while keeping the final recorded word timings.
    canonical=re.findall(r"[«\"]?\w+(?:[-’']\w+)*[.,:!?»\"]*",script)
    norm=lambda s:' '.join(tokens(s))
    matcher=difflib.SequenceMatcher(None,[norm(w['text']) for w in WORDS],[norm(s) for s in canonical],autojunk=False)
    mapped=0
    for block in matcher.get_matching_blocks():
        for j in range(block.size):WORDS[block.a+j]['display']=canonical[block.b+j];mapped+=1
    if mapped!=len(WORDS):raise ValueError(f'Caption mismatch: {mapped}/{len(WORDS)}')
    sentences=[];g=[]
    for w in WORDS:
        g.append(w)
        if w['display'].rstrip('»"').endswith(('.', '!', '?')):sentences.append(g);g=[]
    if g:sentences.append(g)
    groups=[]
    numeric_display=[]
    for sentence in sentences:
        phrase=' '.join(norm(w['display']) for w in sentence)
        if phrase in ['всего на шестьдесят шесть сотых миллиметра','by just zero point six six millimeters']:
            numeric_display.append({'spoken':phrase,'display':'0,66' if LANG=='ru' else '0.66','start':sentence[2]['start'],'end':sentence[-2]['end']})
            number=dict(sentence[2],display='0,66' if LANG=='ru' else '0.66',end=sentence[-2]['end'])
            sentence=[sentence[0],sentence[1],number,sentence[-1]]
        while len(sentence)>5:
            count=3 if len(sentence)==6 else 4
            groups.append(sentence[:count]);sentence=sentence[count:]
        if sentence:groups.append(sentence)
    (P/'numeric_caption_display.json').write_text(json.dumps(numeric_display,ensure_ascii=False,indent=2))
    def ass_time(t):
        cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
    def srt_time(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: S,DejaVu Sans,58,&H00FFFFFF,&H0073CCF0,&H0010161D,&H8010161D,-1,0,0,0,100,100,0,0,1,4,1.5,2,65,145,315,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    accents={'ноги','снаружи','высоте','держать','жив','спаслись','болтов','тоньше','короткими','контроля','dead','alive','outside','survived','bolts','narrow','short','oversight'}
    lines=[];srts=[];captions=[]
    for i,g in enumerate(groups):
        start=g[0]['start'];natural_end=g[-1]['end']+.13
        next_start=groups[i+1][0]['start'] if i+1<len(groups) else DURATION
        end=min(next_start,natural_end)
        end=max(start+.08,end)
        labels=[w['display'].upper() for w in g]
        widths=[font(58).getlength(x) for x in labels]
        if sum(widths)+22*(len(labels)-1)>850:
            candidates=range(1,len(labels))
            split=min(candidates,key=lambda n:abs(sum(widths[:n])+22*(n-1)-sum(widths[n:])-22*(len(labels)-n-1)))
            label_lines=[labels[:split],labels[split:]]
        else:label_lines=[labels]
        max_width=max(font(58).getlength(' '.join(z)) for z in label_lines)
        size=min(58,int(58*850/max_width))
        def color(s):return ('{\\c&H0073CCF0&}'+s+'{\\c&H00FFFFFF&}') if norm(s) in accents else s
        label='\\N'.join(' '.join(color(s) for s in ln) for ln in label_lines)
        lines.append(f'Dialogue: 0,{ass_time(start)},{ass_time(end)},S,,0,0,0,,{{\\pos(500,1550)\\fs{size}}}{label}\n')
        srts.append(f'{i+1}\n{srt_time(start)} --> {srt_time(end)}\n'+ ' '.join(w['display'] for w in g)+'\n\n')
        captions.append({'start':start,'end':end,'words':len(g),'text':' '.join(w['display'] for w in g)})
    (P/'subtitles.ass').write_text(header+''.join(lines));(P/'subtitles.srt').write_text(''.join(srts))
    (P/'captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2))

def make_sound():
    sr=48000;n=round(DURATION*sr);t=np.arange(n)/sr
    rng=np.random.default_rng(37);v=np.pad(voice,(0,max(0,n-len(voice))))[:n]
    # Original restrained minor motif: clearer than a constant low drone.
    music=np.zeros(n,dtype='float64')
    reveal=cue('Он был жив','He was alive');verdict=cue('В отчёте','The report')
    tension=np.clip(t/max(1,reveal),0,1)
    for h,a in [(1,.65),(2,.22),(3,.08)]:music+=a*np.sin(2*np.pi*55*h*t)*(1+.10*np.sin(2*np.pi*.12*t))
    for beat in np.arange(.5,DURATION,1.5):
        a=int(beat*sr);b=min(n,a+int(.9*sr));tt=np.arange(b-a)/sr
        pitch=[220,261.63,207.65,246.94][int(beat/1.5)%4]
        music[a:b]+=.32*np.sin(2*np.pi*pitch*tt)*np.exp(-tt*6)*(1-np.exp(-tt*80))
    pulse=np.maximum(0,np.sin(2*np.pi*1.5*t))**14
    music+=.16*pulse*np.sin(2*np.pi*82.4*t)*(0.4+.6*tension)
    music*=.7+.3*tension
    # Brief space before the reveal and a quieter, serious closing question.
    music*=1-.96*np.exp(-((t-(reveal-.10))/.22)**4)
    cause=cue('Но почему','But why');music*=1-.93*np.exp(-((t-(cause+.05))/.30)**4)
    ending=np.clip((t-verdict)/.6,0,1);ending=ending*ending*(3-2*ending);music*=1-.45*ending
    rms_voice=np.sqrt(np.mean(v*v));music*=rms_voice*10**(-23/20)/np.sqrt(np.mean(music*music))
    for ru,en in [('Вдруг левое','Suddenly'),('Но почему','But why')]:
        start=cue(ru,en);a=int(start*sr);b=min(n,a+int(.22*sr));tt=np.arange(b-a)/sr
        music[a:b]+=.012*np.sin(2*np.pi*180*tt)*np.exp(-tt*24)
    # Original restrained air rush, no fake original cockpit recording.
    start=cue('Вдруг левое','Suddenly');stop=cue('Самолёт сел','Then the plane landed')
    air=np.convolve(rng.normal(0,1,n),np.ones(24)/24,mode='same')
    gate=np.clip((t-start)/.16,0,1)*np.clip((stop-t)/.5,0,1)
    air*=gate*rms_voice*10**(-36/20)/(np.sqrt(np.mean(air*air))+1e-12)
    mix=v+music+air
    for name,arr in [('music.wav',music),('mix.wav',mix)]:
        with wave.open(str(P/name),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(arr,-.98,.98)*32767).astype('<i2').tobytes())
    (P/'mix_settings.json').write_text(json.dumps({'music':'original procedural minor motif and pulse','music_relative_rms_db':-23,'reveal':reveal,'voice_rms':float(rms_voice),'listening_review':False},indent=2))

def contact_sheet():
    out=Image.new('RGB',(5*216,math.ceil(len(manifest)/5)*424),'#051019');d=ImageDraw.Draw(out)
    for i,s in enumerate(manifest):
        pic=render(LANG,s['visual'],.7,seconds=0);pic.save(P/f"frame_{i:02}_{s['visual']}.jpg",quality=92)
        pic=pic.resize((216,384));x=i%5*216;y=i//5*424;out.paste(pic,(x,y+30))
        d.text((x+5,y+5),f"{s['start']:.1f}s {s['visual']}",font=font(13),fill='white')
    out.save(P/'contact_sheet.jpg',quality=90)

def movie():
    output=P/f'SNG_037_BA5390_{LANG.upper()}_PREVIEW.mp4'
    log=(P/'render.log').open('w')
    args=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-i',str(P/'mix.wav'),'-vf',f'ass={P/"subtitles.ass"}',
          '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-threads','3','-g','60','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(DURATION),'-movflags','+faststart',str(output)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log)
    dynamic={'height','blow','ninety','thin','difference','short','pressure','duration','kick','oversight','end'}
    try:
        for i,s in enumerate(manifest):
            count=round((s['end']-s['start'])*30)
            still=None
            if s['visual'] not in dynamic:still=render(LANG,s['visual']).tobytes()
            for frame in range(count):
                pixels=still if still else render(LANG,s['visual'],frame/max(1,count-1),seconds=frame/30).tobytes()
                proc.stdin.write(pixels)
            print(LANG,i,s['visual'],f"{s['end']:.1f}/{DURATION:.1f}",flush=True)
    finally:proc.stdin.close()
    code=proc.wait();log.close()
    if code:raise RuntimeError(f'ffmpeg exited {code}; see {P}/render.log')
    print('READY',output,flush=True)

if '--audio-only' in sys.argv:
    make_sound()
else:
    make_subtitles()
    contact_sheet()
    if '--stills' not in sys.argv:
        make_sound()
        movie()
