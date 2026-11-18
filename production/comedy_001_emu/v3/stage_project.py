from pathlib import Path
import shutil
P=Path(__file__).parent;repo=Path('/workspace/sng-publish');dst=repo/'production/comedy_001_emu/v3';dst.mkdir(parents=True,exist_ok=True)
for f in P.iterdir():
 if f.is_file() and f.suffix in ['.py','.md','.json','.txt']:shutil.copy2(f,dst/f.name)
for name in ['assets','models','qc']:
 shutil.copytree(P/name,dst/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
for lang in ['ru','en']:
 d=dst/lang;d.mkdir(exist_ok=True)
 for f in (P/lang).iterdir():
  if f.is_file() and f.suffix in ['.wav','.mp3','.json','.txt','.ass','.srt','.cachekey']:shutil.copy2(f,d/f.name)
 shutil.copytree(P/lang/'qc',d/'qc',dirs_exist_ok=True)
 f=P/lang/f'SNG_COMEDY_001_EMU_{lang.upper()}_PREVIEW_V3.mp4';shutil.copy2(f,repo/f.name)
for k in ['scatter','truck']:
 d=dst/'animation_metadata'/k;d.mkdir(parents=True,exist_ok=True)
 for f in (P/'frames'/k).glob('*.json'):shutil.copy2(f,d/f.name)
print(dst)
