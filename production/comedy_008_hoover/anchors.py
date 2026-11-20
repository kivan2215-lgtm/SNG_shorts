import json,re,numpy as np,torch,torchaudio,soundfile as sf
from pathlib import Path
from scipy.signal import resample_poly
from transformers import Wav2Vec2ForCTC
root=Path('/workspace/jet_stress/ctc');src=Path('dry')
torch.set_num_threads(3);m=Wav2Vec2ForCTC.from_pretrained(root).eval()
v=json.loads((root/'vocab.json').read_text());result=[]
for i,para in enumerate(Path('ru.txt').read_text().strip().split('\n\n')):
 words=para.split(); pieces=[re.sub('[^а-я|]','','|'.join(re.findall('[а-я]+',w.lower().replace('ё','е')))) for w in words]
 chars='';indices=[]
 for s in pieces:
  if not s:indices.append(None);continue
  if chars:chars+='|'
  start=len(chars);chars+=s;indices.append((start,len(chars)))
 x,sr=sf.read(src/f'ru{i}.wav');u=resample_poly(x,2,3).astype('float32');assert sr==24000
 with torch.inference_mode():lp=m(torch.tensor((u-u.mean())/u.std())[None,:]).logits.log_softmax(-1)
 path,sc=torchaudio.functional.forced_align(lp,torch.tensor([[v[c] for c in chars]]),blank=0)
 spans=torchaudio.functional.merge_tokens(path[0],sc[0]);assert len(spans)==len(chars)
 a=np.array([.01+.01*(s.start+s.end) for s in spans])
 result.append([None if not ix else {'word':w,'first':a[ix[0]],'last':a[ix[1]-1],'letters':a[ix[0]:ix[1]].tolist()} for w,ix in zip(words,indices)])
Path('anchors.json').write_text(json.dumps(result,ensure_ascii=False))
