"""Confirm a visual-only revision preserved voice/music, duration and captions."""
from pathlib import Path
import subprocess,json,hashlib,struct
P=Path(__file__).resolve().parents[1];mf=P/'v4/revision_manifest.json';meta=json.loads(mf.read_text())
for lang in ['ru','en']:
 files=[P/lang/f'SNG_032_Squalus_{lang.upper()}_PREVIEW_{v}.mp4' for v in ['V3','V4']]
 hashes=[subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip() for f in files]
 assert hashes[0]==hashes[1],(lang,'audio stream changed')
 probes=[json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,duration,r_frame_rate','-of','json',str(f)]))['streams'][0] for f in files]
 assert probes[0]==probes[1],(lang,'duration/frame count changed',probes)
 for name in ['voice.wav','mix.wav','subtitles.ass','timeline.json']:
  sha=hashlib.sha256((P/lang/name).read_bytes()).hexdigest();assert sha==meta['languages'][lang][name]['sha256']
 data=files[1].read_bytes();pos=0;boxes=[]
 while pos+8<=len(data):
  size,typ=struct.unpack('>I4s',data[pos:pos+8]);boxes.append(typ.decode('ascii','replace'))
  if size==1:size=struct.unpack('>Q',data[pos+8:pos+16])[0]
  if size==0:break
  assert size>=8;pos+=size
 assert boxes.index('moov')<boxes.index('mdat'),(lang,'MP4 metadata is not at the front')
 meta['languages'][lang].update(faststart_verified=True,aac_identical_to_v3=True,aac_sha256=hashes[1],video_timing_identical_to_v3=True,video_timing=probes[1]);print(lang,'audio bytes, timing and captions unchanged',flush=True)
mf.write_text(json.dumps(meta,ensure_ascii=False,indent=2))
