import torch,soundfile as sf
torch.set_num_threads(3)
m=torch.package.PackageImporter('v4_ru.pt').load_pickle("tts_models","model")
refs=['Кепка вл+езет в почтовый ящик.','Куда вы пол+ожите истребитель?','Юмор к+ончился.','Начал+ась бухгалтерия.','Я носк+и дороже пересылал.','У п+арня шопинг.','Судья сочл+а шутку очевидной.']
for i,t in enumerate(refs):
 try:y=m.apply_tts(text=t,speaker='aidar',sample_rate=24000)
 except Exception:y=m.apply_tts(text=t,speaker='aidar',sample_rate=24000)
 sf.write(f'ref{i}.wav',y,24000)
