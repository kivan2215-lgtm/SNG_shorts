from pathlib import Path
import torch,soundfile as sf
from qwen_tts import Qwen3TTSModel
root=Path('/workspace/voice_sample/v4')
torch.set_num_threads(4);torch.manual_seed(51)
m=Qwen3TTSModel.from_pretrained(str(root/'model'),device_map='cpu',dtype=torch.bfloat16,attn_implementation='sdpa')
ref=m.create_voice_clone_prompt(ref_audio=sf.read(root/'ref.wav',dtype='float32'),ref_text='НАСА отправило аппарат к Марсу и потеряло его из-за единиц измерения. Не пришельцы, не чёрная дыра, а ёбаная путаница в числах.')
for i,t in enumerate(Path('ru.txt').read_text().strip().split('\n\n')):
 w,s=m.generate_voice_clone(text=t,language='Russian',voice_clone_prompt=ref,max_new_tokens=320,temperature=.72,top_p=.9)
 sf.write(f'ru{i}.wav',w[0],s);print(i,len(w[0])/s,flush=True)
