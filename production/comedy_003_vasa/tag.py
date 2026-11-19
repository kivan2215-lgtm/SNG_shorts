from pathlib import Path
import subprocess,sys,json
lang=sys.argv[1];p=Path(f'SNG_COMEDY_003_VASA_{lang}.mp4')
meta=Path('SOURCES.md').read_text()
tmp=p.with_suffix('.tmp.mp4')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(p),'-map','0','-c','copy','-movflags','+faststart','-metadata','comment='+meta,'-metadata','title='+('Васа — испытание остановили' if lang=='RU' else 'Vasa — They Stopped the Test'),str(tmp)],check=True)
tmp.replace(p)
