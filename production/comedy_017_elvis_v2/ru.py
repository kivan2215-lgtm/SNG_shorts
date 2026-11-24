from pathlib import Path
import torch,soundfile as sf
from qwen_tts import Qwen3TTSModel
root=Path('/workspace/voice_sample/v4')
torch.set_num_threads(4);torch.manual_seed(51)
m=Qwen3TTSModel.from_pretrained(str(root/'model'),device_map='cpu',dtype=torch.bfloat16,attn_implementation='sdpa')
ref=m.create_voice_clone_prompt(ref_audio=sf.read(root/'ref.wav',dtype='float32'),ref_text='НАСА отправило аппарат к Марсу и потеряло его из-за единиц измерения. Не пришельцы, не чёрная дыра, а ёбаная путаница в числах.')
import numpy as np
for i,parts in {0: ['У людей в самолёте просьбы простые. Воды, плед, уберите нахуй колено соседа.', 'Элвису понадобился федеральный жетон. Он прямо в кресле написал Никсону.', 'Охуеть у человека кнопка вызова: нажал, и вместо стюарда тебе нужен президент.'], 3: ['И ведь сработало, сука. Элвис в Овальном кабинете.', 'Бархатный костюм, бакенбарды, на пузе пряжка, в которую Никсон видит своё отражение.', 'Так выглядит человек, готовый работать под прикрытием. Каким, блядь?', 'Его же фоторобот можно купить в отделе пластинок. Ещё и с песнями, нахуй.']}.items():
 tracks=[]
 for part in parts:
  w,s=m.generate_voice_clone(text=part,language='Russian',voice_clone_prompt=ref,max_new_tokens=210,temperature=.66,top_p=.9)
  a=w[0].copy();ids=np.flatnonzero(abs(a)>.012)
  if ids.size:a=a[max(0,ids[0]-900):ids[-1]+1500]
  n=min(120,len(a));a[:n]*=np.linspace(0,1,n);a[-n:]*=np.linspace(1,0,n)
  tracks.extend([a,np.zeros(round(.07*s))])
 sf.write(f'ru{i}.wav',np.concatenate(tracks),s)
