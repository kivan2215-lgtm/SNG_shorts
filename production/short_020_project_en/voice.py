import asyncio,os,json
from pathlib import Path
import edge_tts,edge_tts.communicate as ec
p=Path(__file__).parent
text=(p/'narration.txt').read_text()
(p/'tts_script.txt').write_text(text)
ca=os.environ.get('SSL_CERT_FILE') or os.environ.get('CODEX_PROXY_CERT')
import ssl
original_context=ssl.create_default_context
def trusted_context(*a,**kw):
 ctx=original_context(*a,**kw)
 if ca:ctx.load_verify_locations(cafile=ca)
 return ctx
ssl.create_default_context=trusted_context
import re
lines=[x.replace('\n',' ') for x in text.split('\n\n') if x.strip()]
async def main():
 import subprocess
 boundaries=[];offset=0
 for i,line in enumerate(lines):
  import unicodedata
  line=unicodedata.normalize('NFC',line)
  for attempt in range(6):
   try:
    c=edge_tts.Communicate(line,'en-US-GuyNeural',rate=['+0%','+2%','+1%','-3%','-2%'][i],pitch=['+1Hz','+0Hz','+1Hz','-2Hz','-2Hz'][i],boundary='WordBoundary',proxy=os.environ.get('HTTPS_PROXY'))
    b=[];out=p/f'v{i}.mp3'
    with out.open('wb') as f:
     async for m in c.stream():
      if m['type']=='audio':f.write(m['data'])
      else:b.append(m)
    for w in b:w['offset']+=round(offset*1e7)
    boundaries.extend(b)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)]))
    offset+=dur
    print(i,dur,flush=True);break
   except edge_tts.exceptions.NoAudioReceived:
    if attempt==5:raise
    await asyncio.sleep(2)
 (p/'boundaries.json').write_text(json.dumps(boundaries,ensure_ascii=False))
 (p/'voice_concat.txt').write_text(''.join(f"file '{p/f'v{i}.mp3'}'\n" for i in range(len(lines))))
asyncio.run(main())
import subprocess
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(p/'voice_concat.txt'),'-ar','48000','-ac','1',str(p/'narration_full.wav')],check=True)
