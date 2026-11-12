from pathlib import Path
import json,subprocess,sys
R=Path(__file__).parent
lang=sys.argv[1];p=R/lang
scenes={x['visual']:x for x in json.loads((p/'timeline.json').read_text())}
# Different original tape segments; the school scene returns deliberately at the final reveal.
words=json.loads((p/'words.json').read_text())
greetings=[w['start'] for w in words if w['text'].lower() in ['привет','hi']]
source={'opening':717.96-greetings[0],'court':914.0,'return':717.96-(greetings[-1]-scenes['return']['start']),'recorded':1084.0}
args=['ffmpeg','-y','-v','warning','-i',str(p/f'SNG_027_Cassie_Stoddart_{lang.upper()}_PREVIEW.mp4')]
for key,ss in source.items():
 s=scenes[key];args+=['-ss',str(ss),'-t',str(s['end']-s['start']),'-i',str(R/'assets/original_tape.mp4')]
f=[];last='0:v'
for i,key in enumerate(source,1):
 s=scenes[key];start=s['start'];end=s['end']
 f.append(f'[{i}:v]fps=30,scale=1080:810:flags=lanczos,setsar=1,pad=1080:1120:0:155:color=0x101e29,setpts=PTS-STARTPTS+{start}/TB[a{i}]')
 f.append(f'[{last}][a{i}]overlay=x=0:y=330:enable=\'gte(t,{start})*lt(t,{end})\':eof_action=pass:repeatlast=0[o{i}]');last=f'o{i}'
args+=['-filter_complex',';'.join(f),'-map',f'[{last}]','-map','0:a','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','3','-c:a','copy','-movflags','+faststart',str(p/f'SNG_027_Cassie_Stoddart_{lang.upper()}_PREVIEW_V2.mp4')]
(p/'archive_insertions.json').write_text(json.dumps([dict(scene=k,source_start=v,output_start=scenes[k]['start'],output_end=scenes[k]['end'],audio='existing narration; source muted') for k,v in source.items()],indent=2))
subprocess.run(args,check=True)
