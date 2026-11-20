from pathlib import Path
import re,torch,soundfile as sf
torch.set_num_threads(3)
m=torch.package.PackageImporter('/workspace/jet_stress/v4_ru.pt').load_pickle("tts_models","model")
for i,t in enumerate(Path('stress.txt').read_text().strip().split('\n\n')):
 for w in re.findall(r'[А-Яа-яёЁ+]+',t):
  if len(re.findall('[аеёиоуыэюя]',w.lower()))>1:
   assert w.count('+')==1,w
 assert t.replace('+','')==Path('ru.txt').read_text().strip().split('\n\n')[i]
 y=m.apply_tts(text=t,speaker='aidar',sample_rate=48000,put_accent=False,put_yo=False)
 sf.write(f'ru{i}.wav',y,48000)
