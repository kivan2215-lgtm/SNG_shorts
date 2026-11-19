from pathlib import Path
import json, subprocess
import numpy as np
from scipy.signal import butter, sosfilt, correlate
from scipy.ndimage import gaussian_filter1d
from scipy.io.wavfile import read, write
p=Path('/workspace/jet_v2')
sr=48000
anchors=json.loads(Path('/workspace/jet_stress/anchors.json').read_text())
stresses=dict(zip(anchors,[2,3,1,5,4,1,4]))
def smoothspeech(signal, marks, key):
    # Overlap real speech grains at locally matching phases. No external voice spectrum.
    marks=np.array(marks); start=max(0,round((marks[0]-.12)*sr)); end=min(len(signal),round((marks[-1]+.12)*sr))
    x=signal[start:end].copy(); a=marks-start/sr; t=np.arange(len(x))/sr
    j=stresses[key]+1; vs=[i+1 for i,c in enumerate(key) if c in 'аеёиоуыэюя']
    knots=np.r_[0,a,len(x)/sr]; lens=np.diff(knots); weights=np.ones(len(lens))
    for i in vs: weights[i:i+2]*=1.32 if i==j else .91
    inner=lens[1:-1]*weights[1:-1];inner*=sum(lens[1:-1])/inner.sum()
    dest=np.r_[0,a[0],a[0]+np.cumsum(inner),len(x)/sr]
    centers=np.interp(t,dest,knots)*sr
    size,hop,search=1056,264,225
    win=np.hanning(size);buf=np.zeros(len(x));norm=np.zeros(len(x))
    for pos in range(0,len(x)-size+1,hop):
        expected=int(np.clip(centers[pos+size//2]-size//2,0,len(x)-size))
        low=max(0,expected-search);high=min(len(x)-size,expected+search)
        near=pos/sr<a[0]-.04 or (pos+size)/sr>a[-1]+.04
        if not pos or near:idx=pos
        else:
            have=norm[pos:pos+size-hop]; part=buf[pos:pos+size-hop]/np.maximum(have,.001)
            taper=np.minimum(have,1);target=part*taper
            cand=x[low:high+size-hop];corr=correlate(cand,target,'valid')
            denom=np.sqrt(np.maximum(correlate(cand*cand,taper,'valid'),1e-10)*max(np.dot(part,target),1e-10))
            merit=corr/denom-.08*((np.arange(low,high+1)-expected)/search)**2
            idx=low+np.argmax(merit)
        buf[pos:pos+size]+=x[idx:idx+size]*win;norm[pos:pos+size]+=win
    y=np.where(norm>.005,buf/np.maximum(norm,1e-9),x)
    db=np.zeros(len(x))
    for i in vs:
        width=np.clip((dest[i+2]-dest[i])*.30,.026,.060)
        db+=(1.35 if i==j else -.75)*np.exp(-.5*((t-dest[i+1])/width)**2)
    edge=np.clip((t-a[0]+.045)/.028,0,1)*np.clip((a[-1]+.045-t)/.028,0,1)
    signal[start:end]=x+(y*10**(db/20)-x)*edge
_,base=read(p/'rumix.wav'); mix=base.astype(float)/32767; offset=0; report=[]
for i in range(5):
    orig=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p/f'ru{i}.wav'),'-ar',str(sr),'-ac','1','-f','f32le','-']),np.float32)
    x=orig.astype(float)
    for key,item in anchors.items():
        if item['block']==i:smoothspeech(x,item['actual'],key)
    n=len(x)//480;quiet=np.max(abs(orig[:n*480].reshape(-1,480)),axis=1)<.006
    mask=np.ones(len(x),bool)
    for lo,hi in np.flatnonzero(np.diff(np.r_[False,quiet,False])).reshape(-1,2):
        if hi-lo>=34:mask[lo*480+(6240 if lo else 0):hi*480-(5760 if lo else 2640)]=False
    filt=butter(2,65,fs=sr,btype='highpass',output='sos');before=sosfilt(filt,orig[mask]);after=sosfilt(filt,x[mask]);gain=np.clip(.13/np.sqrt(np.mean(before[abs(before)>.018]**2)),.84,1.20)
    # Slow, limited phrase levelling; keep local word dynamics and original bed.
    m=int(np.ceil(len(after)/480));frames=np.pad(after,(0,m*480-len(after))).reshape(-1,480)
    power=gaussian_filter1d(np.mean(frames**2,axis=1),22);rms=np.sqrt(power+.00001)
    env=np.clip(.17*20*np.log10(.112/rms),-1.15,1.15)
    env=gaussian_filter1d(env,13)
    af=after*10**(np.interp(np.arange(len(after)),np.arange(m)*480+240,env)/20)
    mix[offset:offset+len(af)]+=(af-before)*gain
    report.append([i,len(af)/sr,float(np.max(abs(af))),float(np.min(env)),float(np.max(env))]);offset+=len(af)+6000
assert offset==len(mix) and np.max(abs(mix))<1
write('mix.wav',sr,(mix*32767).astype(np.int16))
Path('verification.json').write_text(json.dumps(dict(phrases=report,words=list(anchors),duration=len(mix)/sr),ensure_ascii=False,indent=2))
