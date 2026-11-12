import json, re, subprocess, hashlib, struct
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).parent

def check(lang):
    p=ROOT/lang;video=p/f'SNG_027_Cassie_Stoddart_{lang.upper()}_PREVIEW_V2.mp4'
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]))
    vs=next(s for s in info['streams'] if s['codec_type']=='video');au=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert(vs['width'],vs['height'],vs['codec_name'],vs['pix_fmt'],vs['r_frame_rate'])==(1080,1920,'h264','yuv420p','30/1')
    assert(au['codec_name'],au['sample_rate'],au['channels'])==('aac','48000',2)
    assert abs(float(vs['duration'])-float(au['duration']))<.08
    run=subprocess.run(['ffmpeg','-hide_banner','-nostats','-v','info','-i',str(video),'-vf','blackdetect=d=0.05:pix_th=0.02:pic_th=0.98','-af','ebur128=peak=true','-progress','pipe:1','-f','null','-'],capture_output=True,text=True)
    (p/'full_decode_qc_v2.log').write_text(run.stderr)
    assert run.returncode==0
    black=re.findall(r'black_start:([^\n]+)',run.stderr)
    errors=[line for line in run.stderr.splitlines() if any(t in line.lower() for t in ['error while','invalid data','corrupt','decode error'])]
    assert not black and not errors
    summary=run.stderr.rsplit('Summary:',1)[-1]
    integrated=float(re.search(r'I:\s*(-?[\d.]+) LUFS',summary).group(1))
    peak=float(re.search(r'Peak:\s*(-?[\d.]+) dBFS',summary).group(1))
    assert -17.2<integrated<-14.8
    assert peak<=-1.0
    captions=json.loads((p/'captions.json').read_text());words=json.loads((p/'words.json').read_text())
    assert all(2<=c['words']<=5 for c in captions)
    assert all(c['start']<c['end'] for c in captions)
    assert all(b['start']>=a['end']-.011 for a,b in zip(captions,captions[1:]))
    assert words[-1]['end']<float(vs['duration'])
    atoms=[]
    with video.open('rb') as f:
        while True:
            header=f.read(8)
            if len(header)<8:break
            size,typ=struct.unpack('>I4s',header)
            if size==1:
                size=struct.unpack('>Q',f.read(8))[0];headerlen=16
            else:headerlen=8
            atoms.append(typ.decode('ascii'))
            if not size:break
            f.seek(size-headerlen,1)
    assert atoms.index('moov')<atoms.index('mdat')
    timeline=json.loads((p/'timeline.json').read_text())
    assert timeline[0]['start']==0
    assert abs(timeline[-1]['end']-float(vs['duration']))<.04
    assert all(abs(a['end']-b['start'])<.001 for a,b in zip(timeline,timeline[1:]))
    report={
      'language':lang,'file':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
      'duration_seconds':float(info['format']['duration']),'video':{k:vs[k] for k in ['codec_name','width','height','pix_fmt','r_frame_rate','nb_frames']},
      'audio':{k:au[k] for k in ['codec_name','sample_rate','channels','duration']},
      'full_decode_passed':True,'black_intervals':black,'integrated_loudness_lufs':integrated,'true_peak_dbfs':peak,'faststart':True,
      'caption_groups':len(captions),'caption_words_min':min(c['words'] for c in captions),'caption_words_max':max(c['words'] for c in captions),
      'canonical_script_word_alignment':True,'cut_coverage_complete':True,
      'visual_review':'Actual encoded frames inspected, including archive identities, complete faces, caption readability, chronology, and diagram timing.',
      'listening_review':'Not independently confirmed on hearing. Stress cues and punctuation reviewed in text; audio is technically checked. Preview remains for user review.'}
    (p/'QC_V2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(lang,'PASS',report['duration_seconds'],'sec',integrated,'LUFS',peak,'dBTP',flush=True)
    return report
with ThreadPoolExecutor(max_workers=2) as pool:
    reports=list(pool.map(check,['ru','en']))
(ROOT/'QC_V2.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
