import json,re,sys,subprocess,time
from difflib import SequenceMatcher
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
lang=sys.argv[1]; model=WhisperModel('base',device='cpu',compute_type='int8',download_root='/workspace/.sng-shorts/models',local_files_only=True,cpu_threads=1)
chunks=[]
for i,script in enumerate(Path(lang+'.txt').read_text().strip().split('\n\n')):
 path=Path(f'{lang}{i}.'+('mp3' if lang=='en' else 'wav'))
 while not path.exists():time.sleep(1)
 time.sleep(.5)
 a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar','16000','-ac','1','-f','f32le','-']),np.float32)
 words=[w for s in model.transcribe(a,language=lang,word_timestamps=True,beam_size=3)[0] for w in s.words]; tokens=script.split()
 norm=lambda s:re.sub(r'[^\w]','',s.lower()).replace('ё','е')
 match=SequenceMatcher(None,[norm(w.word) for w in words],[norm(w) for w in tokens],autojunk=False)
 times={0:.03,len(tokens):len(a)/16000-.04}
 for k,j,n in match.get_matching_blocks():
  for z in range(n):times[j+z]=words[k+z].start
 keys=sorted(times); out=np.interp(np.arange(len(tokens)+1),keys,[times[k] for k in keys]);out=np.maximum.accumulate(out)
 chunks.append({'duration':len(a)/16000,'script':tokens,'times':out.tolist(),'heard':' '.join(w.word.strip() for w in words)})
 print(i,chunks[-1]['heard'],flush=True)
Path(lang+'.json').write_text(json.dumps(chunks,ensure_ascii=False))
