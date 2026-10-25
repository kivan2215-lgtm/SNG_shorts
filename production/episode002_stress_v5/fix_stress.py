from pathlib import Path
import subprocess,wave,json
import numpy as np
p=Path(__file__).parent;src=p.parent/'revision4';sr=48000
with wave.open(str(src/'mix.wav')) as w:a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float64)/32768
# Acoustically identified vowels in native Dmitry: first /o/ 5.775–5.842,
# second vowel 5.945–6.035. Native contour peaks on second vowel.
# Shift prominence to the first through duration, F0, and intensity, while
# preserving exact overall duration and all other words and frames.
x0,x1,y0,y1=[round(v*sr) for v in (5.773,5.844,5.944,6.039)]
first=a[x0:x1];second=a[y0:y1];extra=round(.028*sr)
def change(x,n,pitch,gain):
 # Pad locally for Rubber Band's analysis window; trim padding after transform.
 pad=round(.16*sr);padded=np.pad(x,(pad,pad));tempo=len(x)/n
 raw=subprocess.check_output(['ffmpeg','-v','error','-f','f32le','-ar',str(sr),'-ac','1','-i','pipe:0','-af',f'rubberband=tempo={tempo}:pitch={pitch}:formant=preserved','-f','f32le','pipe:1'],input=padded.astype(np.float32).tobytes())
 z=np.frombuffer(raw,dtype=np.float32);start=round(pad/tempo);z=z[start:start+n].astype(float)
 if len(z)<n:z=np.pad(z,(0,n-len(z)))
 z*=gain
 # Preserve seamless transitions across the narrow phonetic boundaries.
 ramp=min(round(.006*sr),n//4)
 left=np.interp(np.arange(ramp),np.arange(len(x)),x)
 right=x[-ramp:]
 alpha=np.linspace(0,1,ramp);z[:ramp]=left*(1-alpha)+z[:ramp]*alpha;z[-ramp:]=z[-ramp:]*(1-alpha)+right*alpha
 return z
u=change(first,len(first)+extra,1.32,2.15)
v=change(second,len(second)-extra,.76,.72)
b=np.concatenate([a[:x0],u,a[x1:y0],v,a[y1:]])
assert len(b)==len(a)
assert np.array_equal(b[:x0],a[:x0]) and np.array_equal(b[y1:],a[y1:])
assert max(abs(b))<.98
with wave.open(str(p/'mix_stress_corrected.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(b,-1,1)*32768).astype(np.int16).tobytes())
report={'source':'revision4','method':'localized duration, pitch and intensity correction of Boston vowels','first_vowel_interval':[x0/sr,x1/sr],'second_vowel_interval':[y0/sr,y1/sr],'first_vowel_extra_seconds':extra/sr,'same_total_samples':True,'all_other_words_pcm_preserved':True,'no_visual_changes':True,'human_listening_review':'pending; no direct audio perception tool'}
(p/'stress_edit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(report)
