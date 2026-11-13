import json,wave,subprocess
from pathlib import Path
import numpy as np
P=Path(__file__).parent
for lang in ('ru','en'):
 if not (P/lang/'voice.wav').exists() or (P/lang/'dialogue.json').exists():continue
 d=P/lang;words=json.loads((d/'words.json').read_text());script=(d/'narration.txt').read_text()
 needle='Но полицейские' if lang=='ru' else 'But officers'
 wordseq=needle.split();i=next(i for i in range(len(words)-1) if words[i]['text'].lower()==wordseq[0].lower() and words[i+1]['text'].lower()==wordseq[1].lower())
 t=round(words[i]['start']*30)/30;duration=7.0
 audio=subprocess.check_output(['ffmpeg','-v','error','-ss','1304','-i',str(P/'assets/interrogation_source.mp4'),'-t','7','-vn','-af','loudnorm=I=-18:TP=-2:LRA=9','-ar','48000','-ac','1','-f','s16le','-'])
 with wave.open(str(d/'voice.wav')) as f:pcm=f.readframes(f.getnframes())
 cut=round(t*48000)*2;audio=audio[:672000].ljust(672000,b'\0')
 with wave.open(str(d/'voice.wav'),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(48000);f.writeframes(pcm[:cut]+audio+pcm[cut:])
 phrases=([(0,2,'То есть сначала выстрелили в вас?'),(2,2.5,'Угу.'),(2.5,3.4,'И что случилось?'),(3.4,4.8,'Вы упали на пол?'),(4.8,7,'Да, я пытался встать и не мог.')] if lang=='ru' else [(0,2,'So you got shot first?'),(2,2.5,'Mm-hmm.'),(2.5,3.4,'And what happened?'),(3.4,4.8,'Did you fall on the ground?'),(4.8,7,'Yeah, I was trying to get up and could not.')])
 extra=[]
 for a,b,s in phrases:
  ws=s.split()
  for n,w in enumerate(ws):extra.append({'text':w.strip('.,?!'),'start':t+a+(b-a)*n/len(ws),'end':t+a+(b-a)*(n+1)/len(ws),'paragraph':2,'original_audio':True})
 for w in words[i:]:w['start']+=duration;w['end']+=duration
 (d/'words.json').write_text(json.dumps(words[:i]+extra+words[i:],ensure_ascii=False,indent=2))
 (d/'narration.txt').write_text(script.replace(needle,' '.join(x[2] for x in phrases)+' '+needle))
 (d/'dialogue.json').write_text(json.dumps({'start':t,'duration':duration,'source_start':1304,'source_end':1311,'phrases':phrases},ensure_ascii=False,indent=2))
