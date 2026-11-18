"""V3: shorten detected silence, especially around profanity; never accelerate speech."""
import json,re,subprocess,wave
from pathlib import Path
import numpy as np
P=Path(__file__).parent
PROFANE=re.compile(r'^(?:оху|нахуй|пизд|съеб|сран|херн|ёбан|ебан|говн|хуйн|fuck|shit|bastard|crap)',re.I)
for lang in ['ru','en']:
 p=P/lang;raw=p/'voice_uncut.wav';words=json.loads((p/'words_uncut.json').read_text())
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(raw),'-af','silencedetect=noise=-44dB:d=0.12','-f','null','-'],capture_output=True,text=True,check=True)
 spans=[(float(e)-float(d),float(e)) for e,d in re.findall(r'silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)',r.stderr)]
 profanity=[w for w in words if PROFANE.match(w['text'].lower())]
 cuts=[];details=[]
 for a,b in spans:
  near=any(abs(w['start']-b)<.24 or abs(w['end']-a)<.24 for w in profanity)
  keep=.07 if near else .22
  if b-a<=keep+.04:continue
  # Keep both quiet edges, remove only the middle of measured silence.
  x=a+keep/2;y=b-keep/2
  cuts.append((x,y));details.append({'silence':[a,b],'cut':[x,y],'near_profanity':near,'retained':keep})
 def remap(t):return t-sum(max(0,min(t,b)-a) for a,b in cuts if t>a)
 with wave.open(str(raw),'rb') as w:pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
 before=len(pcm)/48000;chunks=[];last=0
 for a,b in cuts:
  chunks.append(pcm[last:round(a*48000)]);last=round(b*48000)
 chunks.append(pcm[last:]);pcm=np.concatenate(chunks)
 with wave.open(str(p/'voice.wav'),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(pcm.tobytes())
 for word in words:word['start']=remap(word['start']);word['end']=remap(word['end'])
 (p/'words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2))
 (p/'pause_edit.json').write_text(json.dumps({'details':details,'cuts_seconds':cuts,'duration_before':before,'duration_after':len(pcm)/48000,'speech_speed_change':False,'normal_silence_retained':.22,'profanity_silence_retained':.07,'threshold_db':-44,'auditory_review':False},indent=2))
 print(lang,round(len(pcm)/48000,3),'sec;',len(cuts),'silence cuts;',sum(d['near_profanity'] for d in details),'near profanity',flush=True)
