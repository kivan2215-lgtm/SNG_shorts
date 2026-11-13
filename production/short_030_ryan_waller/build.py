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
def tokens(s):return re.findall(r"\w+(?:[-’']\w+)*",s.lower())
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
SCENES=[(0,'v_intro'),
(cue('Он путался','He struggled'),'v_confused'),
(cue('Но они','But they'),'head_hook'),
(cue('Аризона','Arizona'),'house'),
(cue('Райан Уоллер','Ryan Waller'),'family'),
(cue('В доме обнаружили','Inside his house'),'heather'),
(cue('Райан был жив','His face'),'v_face'),
(cue('Вместо','Instead'),'v_room'),
(cue('Райан пытался','Ryan tried'),'v_explain'),
(cue('То есть сначала','So you got shot'),'v_dialogue'),
(cue('Но полицейские','But officers'),'v_listen'),
(cue('Судебное решение','The court decision'),'document'),
(cue('Только заметив','Only after'),'v_help'),
(cue('Фрагмент пули','A bullet fragment was lodged behind'),'medical'),
(cue('Начался отёк','Swelling made'),'surgery'),
(cue('Райан выжил','Ryan survived'),'v_survived'),
(cue('Следствие установило','Investigators established'),'dates'),
(cue('Ричи Карвер и его отец','Richie Carver and his father'),'conviction'),
(cue('Но для Райана','But a conviction'),'v_after'),
(cue('Двадцатого января','On January'),'death'),
(cue('И эта запись','And this recording'),'v_final')]
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
    accents={'записку','луис','хапп','оправдали','страховке','ложь','storm','alive','float','terry','jo','calm','crime','survived','lies','suicide'}
    accents.update({'голосом','убитой','тереситой','шоуэри','украшения','кольцо','кулон','признался','улики','voice','dead','teresita','showery','jewelry','ring','pendant','evidence'})
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
        lines.append(f'Dialogue: 0,{ass_time(start)},{ass_time(end)},S,,0,0,0,,{{\\pos(500,1595)\\fs{size}}}{label}\n')
        srts.append(f'{i+1}\n{srt_time(start)} --> {srt_time(end)}\n'+ ' '.join(w['display'] for w in g)+'\n\n')
        captions.append({'start':start,'end':end,'words':len(g),'text':' '.join(w['display'] for w in g)})
    (P/'subtitles.ass').write_text(header+''.join(lines));(P/'subtitles.srt').write_text(''.join(srts))
    (P/'captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2))

def make_sound():
    sr=48000;n=round(DURATION*sr);v=np.pad(voice,(0,n-len(voice)));t=np.arange(n)/sr
    music=np.zeros(n)
    for i,f in enumerate([73.416,110,174.614]):music+=.007*np.sin(2*np.pi*f*t+i)*(.8+.2*np.sin(t*.4+i))
    for i,start in enumerate(np.arange(0,DURATION,1.9)):
        a=int(start*sr);b=min(n,a+sr*3);tt=np.arange(b-a)/sr;f=[293.665,220,207.652,174.614][i%4]
        music[a:b]+=.017*(1-np.exp(-tt*90))*np.exp(-tt*2)*np.sin(2*np.pi*f*tt)
    reveal=cue('Фрагмент пули','A bullet fragment was lodged behind');ending=cue('Но для Райана','But a conviction')
    env=np.minimum(t/1,1)*np.clip((DURATION-t)/3,0,1)
    env[(t>reveal-.25)&(t<reveal+.35)]=0;env[t>ending]*=.25
    music*=env
    rng=np.random.default_rng(27)
    for instant,length,amp,kind in [(reveal+.3,.11,.016,'click')]:
        a=max(0,int(instant*sr));b=min(n,a+int(length*sr));tt=np.arange(b-a)/sr
        if kind=='ring':sound=(np.sin(2*np.pi*440*tt)+np.sin(2*np.pi*480*tt))*np.sin(np.pi*tt/length)**2
        elif kind=='step':sound=np.sin(2*np.pi*75*tt)*np.exp(-tt*20)
        else:sound=rng.standard_normal(len(tt))*np.exp(-tt*65)
        music[a:b]+=amp*sound
    mix=np.clip(v+music,-.98,.98)
    with wave.open(str(P/'mix.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((mix*32767).astype('<i2').tobytes())

def contact_sheet():
    out=Image.new('RGB',(5*216,math.ceil(len(manifest)/5)*424),'#051019');d=ImageDraw.Draw(out)
    for i,s in enumerate(manifest):
        pic=render(LANG,s['visual'],.7);pic.save(P/f"frame_{i:02}_{s['visual']}.jpg",quality=92)
        pic=pic.resize((216,384));x=i%5*216;y=i//5*424;out.paste(pic,(x,y+30))
        d.text((x+5,y+5),f"{s['start']:.1f}s {s['visual']}",font=font(13),fill='white')
    out.save(P/'contact_sheet.jpg',quality=90)

def movie():
    output=P/f'SNG_030_Ryan_Waller_{LANG.upper()}_PREVIEW.mp4'
    log=(P/'render.log').open('w')
    args=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-i',str(P/'mix.wav'),'-vf',f'ass={P/"subtitles.ass"}',
          '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-threads','3','-g','60','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(DURATION),'-movflags','+faststart',str(output)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log)
    dynamic={'medical','dates','head_hook'}
    try:
        for i,s in enumerate(manifest):
            count=round((s['end']-s['start'])*30)
            still=None
            decoder=None
            if s['visual'].startswith('v_'):
                from visuals import VIDEO_STARTS
                decoder=subprocess.Popen(['ffmpeg','-v','error','-ss',str(VIDEO_STARTS[s['visual']]),'-i',str(ROOT/'assets/interrogation_source.mp4'),'-t',str(count/30),'-vf','crop=640:480:107:0,scale=1080:810,fps=30','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
            elif s['visual'] not in dynamic:still=render(LANG,s['visual']).tobytes()
            for frame in range(count):
                if decoder:
                    raw=decoder.stdout.read(1080*810*3)
                    if len(raw)!=1080*810*3:raise RuntimeError('Short archive decode')
                    pic=render(LANG,s['visual']);pic.paste(Image.frombytes('RGB',(1080,810),raw),(0,430));pixels=pic.tobytes()
                else:pixels=still if still else render(LANG,s['visual'],frame/max(1,count-1)).tobytes()
                proc.stdin.write(pixels)
            if decoder:decoder.stdout.close();decoder.wait()
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
