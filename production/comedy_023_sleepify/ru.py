from pathlib import Path
import torch,soundfile as sf
from qwen_tts import Qwen3TTSModel
root=Path('/workspace/voice_sample/v4')
torch.set_num_threads(4);torch.manual_seed(51)
m=Qwen3TTSModel.from_pretrained(str(root/'model'),device_map='cpu',dtype=torch.bfloat16,attn_implementation='sdpa')
ref=m.create_voice_clone_prompt(ref_audio=sf.read(root/'ref.wav',dtype='float32'),ref_text='НАСА отправило аппарат к Марсу и потеряло его из-за единиц измерения. Не пришельцы, не чёрная дыра, а ёбаная путаница в числах.')
import numpy as np,re
for i,t in enumerate(Path('spoken.txt').read_text().strip().split('\n\n')):
 tracks=[]
 for part in re.split(r'(?<=[.!?]) ',t):
  if not part:continue
  w,s=m.generate_voice_clone(text=part,language='Russian',voice_clone_prompt=ref,max_new_tokens=max(60,21*len(part.split())),temperature=.68,top_p=.9)
  a=np.array(w[0],copy=True);nz=np.flatnonzero(abs(a)>.013)
  if nz.size:a=a[max(0,nz[0]-1050):nz[-1]+1500]
  n=min(120,len(a));a[:n]*=np.linspace(0,1,n);a[-n:]*=np.linspace(1,0,n)
  tracks.extend([a,np.zeros(round(.085*s))])
 sf.write(f'ru{i}.wav',np.concatenate(tracks),s);print(i,flush=True)
