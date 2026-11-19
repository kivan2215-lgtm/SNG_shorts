import torch,soundfile as sf
from qwen_tts import Qwen3TTSModel
torch.set_num_threads(4)
torch.manual_seed(51)
m=Qwen3TTSModel.from_pretrained('model',device_map='cpu',dtype=torch.float32,attn_implementation='sdpa')
print('model ready',flush=True)
w,s=m.generate_voice_clone(text='Числа передали. А единицы? Один, блядь, считает в бананах, другой смотрит на цифры и думает: ну всё, физика сходится.',language='Russian',ref_audio=sf.read('ref.wav',dtype='float32'),ref_text='НАСА отправило аппарат к Марсу и потеряло его из-за единиц измерения. Не пришельцы, не чёрная дыра, а ёбаная путаница в числах.',max_new_tokens=250,temperature=.78,top_p=.9)
sf.write('v4.wav',w[0],s)
