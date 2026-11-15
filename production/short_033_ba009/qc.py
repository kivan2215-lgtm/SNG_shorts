from pathlib import Path
import json,subprocess,re,concurrent.futures,hashlib
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).parent
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
def check(lang):
 p=P/lang;f=p/f'SNG_033_BA009_{lang.upper()}_PREVIEW.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');duration=float(probe['format']['duration'])
 dec=subprocess.run(['ffmpeg','-threads','2','-v','error','-i',str(f),'-f','null','-'],capture_output=True,text=True)
 sig=subprocess.run(['ffmpeg','-threads','2','-hide_banner','-i',str(f),'-vf','blackdetect=d=0.15:pix_th=0.05:pic_th=0.98','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True)
 matches=re.findall(r'\{\s*"input_i".*?\}',sig.stderr,re.S);loud=json.loads(matches[-1]) if matches else None
 timeline=json.loads((p/'timeline.json').read_text());caps=json.loads((p/'captions.json').read_text())
 short=[c for c in caps if c['words']<2];long=[c for c in caps if c['words']>5]
 failures=[]
 data=f.read_bytes();moov=data.find(b'moov');mdat=data.find(b'mdat');faststart=0<=moov<mdat
 if not faststart:failures.append('faststart')
 for ok,reason in [(v['width']==1080 and v['height']==1920,'dimensions'),(v['r_frame_rate']=='30/1','fps'),(v['codec_name']=='h264' and v['pix_fmt']=='yuv420p','video format'),(a['codec_name']=='aac' and a['sample_rate']=='48000','audio format'),(dec.returncode==0 and not dec.stderr.strip(),'decode'),(not long,'caption length'),(duration>=60 and duration<=95,'duration'),(max(c['end'] for c in caps)<=duration,'caption range'),(not re.search(r'black_start:',sig.stderr),'black frame detection')]:
  if not ok:failures.append(reason)
 if loud and float(loud['input_tp'])>-.8:failures.append('true peak')
 # Inspect start, middle and end of every shot, from the actual encoded MP4.
 frames=p/'qc'/'qc_frames';frames.mkdir(parents=True,exist_ok=True);entries=[]
 for i,s in enumerate(timeline):
  for j,t in enumerate([s['start']+.08,(s['start']+s['end'])/2,max(s['start']+.1,s['end']-.10)]):
   target=frames/f'{i:02}_{j}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(f),'-frames:v','1','-q:v','3',str(target)],check=True)
   entries.append((target,f'{t:.2f} {s["visual"]}'))
 for page in range((len(entries)+24)//25):
  items=entries[page*25:(page+1)*25];sheet=Image.new('RGB',(5*216,5*415),'#081824');d=ImageDraw.Draw(sheet)
  for i,(file,label) in enumerate(items):
   im=Image.open(file);im.thumbnail((216,384));x=i%5*216;y=i//5*415;sheet.paste(im,(x,y+30));d.text((x+3,y+4),label,font=font,fill='white')
  sheet.save(p/'qc'/f'encoded_sheet_{page}.jpg',quality=90)
 qc={'language':lang,'file':f.name,'duration':duration,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'video':{k:v[k] for k in ['width','height','codec_name','pix_fmt','r_frame_rate']},'audio':{k:a[k] for k in ['codec_name','sample_rate','channels']},'faststart':faststart,'full_decode_ok':dec.returncode==0 and not dec.stderr.strip(),'loudness':loud,'black_frames':re.findall(r'black_start:.*',sig.stderr),'captions':len(caps),'single_word_sentence_exceptions':short,'failures':failures,'auditory_review':False,'encoded_frame_review':'pending','preview_not_approved':True}
 (p/'qc'/'QC.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2));print(lang,duration,'sec',loud,failures,flush=True)
 return qc
if __name__=='__main__':
 (P/'qc').mkdir(exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:out=list(ex.map(check,['ru','en']))
 (P/'qc'/'QC.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));assert all(not x['failures'] for x in out)
