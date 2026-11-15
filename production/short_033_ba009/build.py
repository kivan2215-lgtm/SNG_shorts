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
SCENES=[(0,'fail'),
(cue('Все четыре','All four'),'alloff'),
(cue('За окнами','A strange blue'),'glow'),
(cue('А экипаж','The crew had no idea'),'question'),
(cue('Двадцать четвёртое','June twenty'),'archive'),
(cue('В салон','Smoke enters'),'cabin'),
(cue('Самолёт больше','The aircraft can'),'glide'),
(cue('Пилоты пытаются','The pilots try'),'attempt'),
(cue('Под ними','Below them'),'ocean'),
(cue('Но причина','But fuel'),'turn'),
(cue('Самолёт попал','The aircraft had'),'volcano'),
(cue('Ночью','At night'),'radar'),
(cue('В горячих','Inside the hot'),'deposit'),
(cue('Поток воздуха','Airflow was'),'blocked'),
(cue('И здесь','Then something'),'escape'),
(cue('Остывая','The deposits cooled'),'clear'),
(cue('Примерно через','After roughly'),'restart'),
(cue('Один вскоре','One soon'),'oneoff'),
(cue('Но испытание','But the ordeal'),'cockpit'),
(cue('Они всё же','They still'),'landing'),
(cue('Все на борту','Everyone on board'),'safe'),
(cue('Четыре двигателя','It was not'),'evidence')]
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
    for sentence in sentences:
        while len(sentence)>5:
            count=3 if len(sentence)==6 else 4
            groups.append(sentence[:count]);sentence=sentence[count:]
        if sentence:groups.append(sentence)
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
    accents={'двигатели','четыре','пепел','пепла','выжили','engines','four','ash','survived','дым','smoke','океан','ocean'}
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
    from scipy.signal import butter,sosfilt
    sr=48000;n=round(DURATION*sr);v=np.pad(voice,(0,n-len(voice)));t=np.arange(n)/sr
    music=np.zeros(n,dtype=np.float64);relief=cue('Все на борту','Everyone on board')
    # Original score: warm low strings, sparse damped piano, restrained low pulse.
    for start in np.arange(0,DURATION,7.4):
        a=int(start*sr);b=min(n,a+int(10*sr));tt=np.arange(b-a)/sr
        notes=[73.416,110,146.832] if start<relief else [73.416,110,184.997]
        env=(1-np.exp(-tt/1.4))*np.clip((10-tt)/2,0,1)
        for j,f in enumerate(notes):
            pad=np.sin(2*np.pi*f*tt+j)+.25*np.sin(2*np.pi*f*2*tt+.3)+.09*np.sin(2*np.pi*f*3*tt)
            music[a:b]+=.18*env*pad
    for i,start in enumerate(np.arange(.7,DURATION,1.8)):
        a=int(start*sr);b=min(n,a+sr*3);tt=np.arange(b-a)/sr
        f=([293.665,220,233.082,174.614] if start<relief else [293.665,369.994,440,220])[i%4]
        env=(1-np.exp(-tt*100))*np.exp(-tt*2.2)
        music[a:b]+=.55*env*(np.sin(2*np.pi*f*tt)+.2*np.sin(2*np.pi*f*2.002*tt))
    rng=np.random.default_rng(32);noise=sosfilt(butter(2,450,fs=sr,output='sos'),rng.standard_normal(n))
    music+=noise*.08
    for start in np.arange(14,relief,2.7):
        a=int(start*sr);b=min(n,a+int(.35*sr));tt=np.arange(b-a)/sr
        music[a:b]+=.34*np.sin(2*np.pi*(54*tt-18*tt*tt))*np.exp(-tt*15)
    rms_voice=float(np.sqrt(np.mean(v*v)));rms_music=float(np.sqrt(np.mean(music*music)))
    music*=rms_voice*10**(-22/20)/max(1e-9,rms_music)
    env=np.clip(t/.4,0,1)*np.clip((DURATION-t)/1.5,0,1)
    # Make room for the moment that answers the opening question.
    turn=cue('Но причина','But fuel');env[(t>turn-.18)&(t<turn+.45)]*=.10
    env[t>=relief]*=.7
    music*=env
    for name,instant,amp in [('seal',cue('Один вскоре','One soon')+.2,.035),('open',turn+.55,.024)]:
        a=int(instant*sr);b=min(n,a+int(.45*sr));tt=np.arange(b-a)/sr
        music[a:b]+=amp*np.exp(-tt*14)*(np.sin(2*np.pi*120*tt)+.4*np.sin(2*np.pi*313*tt))
    mix=v+music
    for name,arr in [('music.wav',music),('mix.wav',mix)]:
        with wave.open(str(P/name),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(arr,-.98,.98)*32767).astype('<i2').tobytes())
    (P/'mix_settings.json').write_text(json.dumps({'music':'original synthesized score, project build.py','music_relative_rms_db':-22,'reveal':relief,'voice_rms':rms_voice,'listening_review':False},indent=2))

def contact_sheet():
    out=Image.new('RGB',(5*216,math.ceil(len(manifest)/5)*424),'#051019');d=ImageDraw.Draw(out)
    for i,s in enumerate(manifest):
        pic=render(LANG,s['visual'],.7);pic.save(P/f"frame_{i:02}_{s['visual']}.jpg",quality=92)
        pic=pic.resize((216,384));x=i%5*216;y=i//5*424;out.paste(pic,(x,y+30))
        d.text((x+5,y+5),f"{s['start']:.1f}s {s['visual']}",font=font(13),fill='white')
    out.save(P/'contact_sheet.jpg',quality=90)

def movie():
    output=P/f'SNG_033_BA009_{LANG.upper()}_PREVIEW.mp4'
    log=(P/'render.log').open('w')
    args=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-i',str(P/'mix.wav'),'-vf',f'ass={P/"subtitles.ass"}',
          '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-threads','3','-g','60','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(DURATION),'-movflags','+faststart',str(output)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log)
    dynamic=set(s['visual'] for s in manifest)
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
