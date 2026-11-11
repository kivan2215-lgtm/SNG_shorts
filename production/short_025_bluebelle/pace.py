"""Remove only the middle of excessive synthesized silence; never speed speech."""
import json, re, subprocess, wave
from pathlib import Path
import numpy as np

P=Path(__file__).parent
for lang in ['ru','en']:
    p=P/lang
    raw=p/'voice_uncut.wav'
    if not raw.exists():raw.write_bytes((p/'voice.wav').read_bytes())
    original=p/'words_uncut.json'
    if not original.exists():original.write_bytes((p/'words.json').read_bytes())
    words=json.loads(original.read_text())
    r=subprocess.run(['ffmpeg','-hide_banner','-i',str(raw),'-af','silencedetect=noise=-40dB:d=0.75','-f','null','-'],capture_output=True,text=True,check=True)
    spans=[(float(a),float(b)) for a,b in re.findall(r'silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)',r.stderr)]
    death=next(w['start'] for w in words if w['text'].lower().strip('.,')==('вскоре' if lang=='ru' else 'soon'))
    cuts=[]
    for end,duration in spans:
        start=end-duration
        keep=.58 if 0 <= death-end < .8 else .38
        if duration>keep:cuts.append((start+keep/2,end-keep/2))
    def remap(t):return t-sum(max(0,min(t,b)-a) for a,b in cuts if t>a)
    with wave.open(str(raw),'rb') as w:pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
    chunks=[];last=0
    for a,b in cuts:
        chunks.append(pcm[last:round(a*48000)]);last=round(b*48000)
    chunks.append(pcm[last:]);pcm=np.concatenate(chunks)
    with wave.open(str(p/'voice.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(pcm.tobytes())
    for word in words:
        word['start']=remap(word['start']);word['end']=remap(word['end'])
    (p/'words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2))
    (p/'pause_edit.json').write_text(json.dumps({'cuts_seconds':cuts,'duration_before':len(pcm)/48000+sum(b-a for a,b in cuts),'duration_after':len(pcm)/48000,'speech_speed_change':False,'normal_silence_retained':.38,'dramatic_silence_retained':.58},indent=2))
    print(lang,round(len(pcm)/48000,3),'sec;',len(cuts),'pauses shortened')
