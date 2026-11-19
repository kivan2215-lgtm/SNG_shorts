from pathlib import Path
import shutil
P=Path(__file__).parent;repo=Path('/workspace/sng-publish');dst=repo/'production/comedy_002_mars';dst.mkdir(parents=True,exist_ok=True)
for f in P.iterdir():
 if f.is_file() and f.suffix in ['.py','.md','.json','.txt']:shutil.copy2(f,dst/f.name)
for name in ['assets','models','qc']:
 shutil.copytree(P/name,dst/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
for lang in ['ru','en']:
 d=dst/lang;d.mkdir(exist_ok=True)
 for f in (P/lang).iterdir():
  if f.is_file() and f.suffix in ['.wav','.mp3','.json','.txt','.ass','.srt','.cachekey']:shutil.copy2(f,d/f.name)
 shutil.copytree(P/lang/'qc',d/'qc',dirs_exist_ok=True)
 f=P/lang/f'SNG_COMEDY_002_MARS_{lang.upper()}_PREVIEW.mp4';shutil.copy2(f,repo/f.name)
for k in ['orbit','units']:
 d=dst/'animation_metadata'/k;d.mkdir(parents=True,exist_ok=True)
 for f in (P/'frames'/k).glob('*.json'):shutil.copy2(f,d/f.name)
print(dst)

research=dst/"research";research.mkdir(exist_ok=True)
for n in ["report.pdf","report.txt","nasa_mission.txt","jpl.txt","rights.txt","nasa_image_search.json"]:
 f=P/"research"/n
 if f.exists():shutil.copy2(f,research/n)
