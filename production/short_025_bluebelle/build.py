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
SCENES=[
 (0,'rescue'),(cue('Он уверял','He said'),'captain'),
 (cue('Но через несколько','But days later'),'lookout'),
 (cue('Багамы','The Bahamas'),'map'),
 (cue('Семья с тремя','A family with three'),'family'),
 (cue('Ночью яхта','One night'),'yacht'),
 (cue('На следующий день','The next day'),'rescued_date'),
 (cue('По его словам','He claims'),'storm'),
 (cue('Но шестнадцатого','But on November'),'raft'),
 (cue('На нём','On it is'),'crew'),
 (cue('Почти четыре','Nearly four'),'survival'),
 (cue('Когда капитан узнал','When the captain learns'),'interview'),
 (cue('Вернулся в гостиницу','He returns to a motel'),'motel'),
 (cue('Ещё до того','Before Terry is'),'chronology'),
 (cue('А её рассказ','And her account'),'testimony'),
 (cue('Море той ночью','The sea that night'),'calm'),
 (cue('Девочка проснулась','Screams woke her'),'night_cabin'),
 (cue('там лежали','she found her mother'),'family_detail'),
 (cue('Когда Терри подошла','When Terry approached'),'cabin_route'),
 (cue('тот грубо','he shoved'),'captain_route'),
 (cue('Яхта начала тонуть','The yacht began'),'water'),
 (cue('Девочка успела отвязать','She managed to release'),'escape'),
 (cue('Следователи пришли','Investigators concluded'),'paper'),
 (cue('Харви расправился','Harvey had killed'),'compare'),
 (cue('Но одного','But there was one'),'medical'),
 (cue('Девочка оставшаяся','The girl left alone'),'ending')]
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
    accents={'шторм','живым','плот','терри','джо','выжила','спокойным','пожара','преступление','ложь','storm','alive','float','terry','jo','calm','crime','survived','lies','suicide'}
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
    sr=48000;n=round(DURATION*sr);v=np.pad(voice,(0,n-len(voice)))
    music=np.zeros((n,2),dtype='float32');rng=np.random.default_rng(25)
    rescue=cue('На нём','On it is');news=cue('Когда капитан узнал','When the captain learns')
    death=cue('И вскоре','Soon afterward');testimony=cue('А её рассказ','And her account')
    ending=cue('Девочка оставшаяся','The girl left alone')
    # Composed harmonic score, not a copied music recording.
    notes=[(73.416,110,174.614),(58.270,87.307,146.832),(65.406,97.999,155.563),(69.296,103.826,164.814)]
    for bar,start in enumerate(np.arange(0,DURATION,5.4)):
        a=int(start*sr);b=min(n,int((start+6.1)*sr));tt=np.arange(b-a,dtype='float32')/sr
        env=np.minimum(tt/.7,1)*np.minimum((len(tt)/sr-tt)/.85,1)
        freq=notes[bar%4]
        if rescue-1<=start<news:freq=(87.307,130.813,174.614)
        for j,f in enumerate(freq):
            for ch in [0,1]:
                ph=2*np.pi*(f*(1+(ch*2-1)*.0008))*tt
                wavelet=np.sin(ph)+.2*np.sin(ph*2+.4)+.07*np.sin(ph*3)
                music[a:b,ch]+=.008*env*wavelet*(1+.08*np.sin(2*np.pi*.19*tt+j))
    # Sparse felt-piano motif; no relentless ticking or startling sound effects.
    seq=[293.665,220,261.626,207.652,174.614,220,155.563,164.814]
    for i,start in enumerate(np.arange(.2,DURATION,2.15)):
        if ending<start:continue
        a=int(start*sr);b=min(n,a+int(3.5*sr));tt=np.arange(b-a,dtype='float32')/sr
        f=seq[i%len(seq)]
        if rescue<=start<news:f=[349.228,329.628,261.626,293.665][i%4]
        env=(1-np.exp(-tt*100))*np.exp(-tt*1.7)
        note=env*(np.sin(2*np.pi*f*tt)+.25*np.sin(2*np.pi*2.003*f*tt)*np.exp(-tt*2)+.11*np.sin(2*np.pi*3.008*f*tt)*np.exp(-tt*4))
        pan=.35 if i%2 else .65
        music[a:b,0]+=.019*note*(1-pan);music[a:b,1]+=.019*note*pan
        # Short stereo reflection, no large vocal reverb.
        delay=int(.17*sr);bb=min(n,b+delay)
        if a+delay<bb:music[a+delay:bb,1]+=.003*note[:bb-a-delay]
    # Subtle low pulse during uncertainty, slightly faster toward the contradiction.
    for start in np.arange(0,ending,1.18):
        if rescue<=start<news:continue
        a=int(start*sr);b=min(n,a+int(.36*sr));tt=np.arange(b-a,dtype='float32')/sr
        pulse=.013*np.sin(2*np.pi*(52*tt-9*tt*tt))*np.exp(-tt*15)*(1-np.exp(-tt*120))
        music[a:b]+=pulse[:,None]
    # Synthesized ocean/wind bed, clearly production sound rather than archival audio.
    from scipy.signal import butter,sosfilt
    noise=sosfilt(butter(2,[100,1400],btype='band',fs=sr,output='sos'),rng.standard_normal(n)).astype('float32')
    tt=np.arange(n,dtype='float32')/sr
    storm=cue('По его словам','He claims');find=cue('Но шестнадцатого','But on November')
    bed=np.zeros(n,dtype='float32')
    for a,b,amp in [(0,2.6,.007),(storm,find,.011),(cue('Море той ночью','The sea that night'),cue('Девочка проснулась','Screams woke her'),.003)]:
        envelope=np.clip((tt-a)/.4,0,1)*np.clip((b-tt)/.5,0,1)
        bed+=amp*envelope*noise*(.75+.25*np.sin(tt*.85))
    music+=bed[:,None]
    # Speech-led ducking measured from the actual voice energy.
    block=480;level=np.repeat(np.sqrt(np.mean(v[:n//block*block].reshape(-1,block)**2,axis=1)),block)
    level=np.pad(level,(0,n-len(level)),mode='edge')
    smooth=sosfilt(butter(1,4,fs=sr,output='sos'),level)
    duck=1-.28*np.clip(smooth/.035,0,1);music*=duck[:,None]
    env=np.minimum(tt/1.0,1)*np.minimum((DURATION-tt)/1.2,1)
    # A short genuine music silence before the death, with a restrained return.
    env*=np.where((tt>death-.43)&(tt<death+.40),0,1)
    env*=np.where((tt>=death+.4)&(tt<testimony),.5,1)
    env*=np.clip((DURATION-tt)/3.8,0,1)
    # Audible but quiet psychological tension, rising by story stage.
    tension=np.interp(tt,[0,rescue,news,death,testimony,ending,DURATION],
                      [1.35,1.75,1.4,1.9,1.55,2.0,.65])
    music*=(env*tension)[:,None]
    out=np.clip(v[:,None]+music,-.99,.99)
    with wave.open(str(P/'mix.wav'),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype('<i2').tobytes())
    with wave.open(str(P/'music.wav'),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((music*32767).astype('<i2').tobytes())
    (P/'sound_plan.json').write_text(json.dumps({'original_score':True,'rescue_hope':rescue,'return_to_tension':news,'music_silence':[death-.43,death+.4],'final_fade_start':DURATION-3.8,'music_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(music**2)))),'voice_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(v*v))))},indent=2))

def contact_sheet():
    out=Image.new('RGB',(5*216,math.ceil(len(manifest)/5)*424),'#051019');d=ImageDraw.Draw(out)
    for i,s in enumerate(manifest):
        pic=render(LANG,s['visual'],.7);pic.save(P/f"frame_{i:02}_{s['visual']}.jpg",quality=92)
        pic=pic.resize((216,384));x=i%5*216;y=i//5*424;out.paste(pic,(x,y+30))
        d.text((x+5,y+5),f"{s['start']:.1f}s {s['visual']}",font=font(13),fill='white')
    out.save(P/'contact_sheet.jpg',quality=90)

def movie():
    output=P/f'SNG_025_Bluebelle_{LANG.upper()}_PREVIEW.mp4'
    log=(P/'render.log').open('w')
    args=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-i',str(P/'mix.wav'),'-vf',f'ass={P/"subtitles.ass"}',
          '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-threads','3','-g','60','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(DURATION),'-movflags','+faststart',str(output)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log)
    dynamic={'cabin_route','captain_route','escape','chronology'}
    try:
        for i,s in enumerate(manifest):
            count=round((s['end']-s['start'])*30)
            still=None
            if s['visual'] not in dynamic:still=render(LANG,s['visual']).tobytes()
            for frame in range(count):
                pixels=still if still else render(LANG,s['visual'],frame/max(1,count-1)).tobytes()
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
