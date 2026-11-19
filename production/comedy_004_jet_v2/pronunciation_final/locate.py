import json,re,torch,torchaudio,numpy as np,soundfile as sf
from scipy.signal import resample_poly
from transformers import Wav2Vec2ForCTC
from pathlib import Path
from math import gcd
torch.set_num_threads(3)
m=Wav2Vec2ForCTC.from_pretrained('ctc').eval()
v=json.loads(Path('ctc/vocab.json').read_text())
keys=['влезет','положите','кончился','началась','носки','парня','сочла']
blocks=json.loads(Path('/workspace/jet_v2/ru.json').read_text())
refs=['Кепка влезет в почтовый ящик','Куда вы положите истребитель','Юмор кончился','Началась бухгалтерия','Я носки дороже пересылал','У парня шопинг','Судья сочла шутку очевидной']
def locate(path,text):
 x,sr=sf.read(path);g=gcd(sr,16000);x=resample_poly(x,16000//g,sr//g).astype('float32')
 letters='|'.join(re.findall('[а-я]+',text.lower().replace('ё','е')))
 t=torch.tensor([[v[c] for c in letters]],dtype=torch.long)
 with torch.inference_mode():out=m(torch.tensor(((x-x.mean())/(x.std()+1e-6))[None,:])).logits.log_softmax(-1)
 path,scores=torchaudio.functional.forced_align(out,t,blank=0)
 spans=torchaudio.functional.merge_tokens(path[0],scores[0])
 assert len(spans)==len(letters)
 anchors=np.array([.01+.01*(s.start+s.end) for s in spans])
 words={}
 for key in keys:
  hit=re.search(r'(?:^|\|)('+key+r')(?:\||$)',letters)
  if hit:
   a,b=hit.span(1)
   # Bounds separated from neighboring word at boundary token.
   left=max(0,(anchors[a]+anchors[a-1])/2) if a else max(0,anchors[a]-.055)
   right=(anchors[b]+anchors[b-1])/2 if b<len(anchors) else min(len(x)/16000,anchors[b-1]+.07)
   words[key]=[left,*anchors[a:b].tolist(),right]
 return words
out={}
for i in [0,1,3,4]:
 p=Path(f'/workspace/jet_v2/ru{i}.wav')
 for k,val in locate(p,' '.join(blocks[i]['script'])).items():out[k]={'block':i,'actual':val}
for i,key in enumerate(keys):
 out[key]['reference']=locate(f'ref{i}.wav',refs[i])[key]
Path('anchors.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
print(out)
