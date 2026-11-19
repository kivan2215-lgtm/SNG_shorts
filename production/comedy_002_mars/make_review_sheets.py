from pathlib import Path
from PIL import Image
P=Path(__file__).parent
for lang in ['ru','en']:
 files=sorted((P/lang/'qc/qc_frames').glob('*_1.jpg'))
 assert len(files)>0
 for page in range((len(files)+17)//18):
  sheet=Image.new('RGB',(1080,2310),'#102228')
  for i,f in enumerate(files[page*18:(page+1)*18]):
   im=Image.open(f);im.thumbnail((216,384));sheet.paste(im,(i%3*360+72,i//3*385))
  sheet.save(P/lang/'qc'/f'midreview_{page}.jpg')
