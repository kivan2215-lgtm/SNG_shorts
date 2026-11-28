"""Original sparse funk score, with room for the silent solo and final jack click."""
import numpy as np

def score(n,sr,shots,voice,first_end,ru):
    rng=np.random.default_rng(23)
    song=np.zeros(n)
    def hit(at,freq,amp,decay,kind='bass'):
        i=max(0,round(at*sr));j=min(n,i+round(.48*sr))
        if i>=j: return
        t=np.arange(j-i)/sr
        ph=2*np.pi*freq*t
        if kind=='bass':
            wave=np.sin(ph)+.36*np.sin(2*ph)*np.exp(-13*t)+.17*np.sin(3*ph)*np.exp(-20*t)
        elif kind=='chord':
            wave=(np.sin(ph)+.59*np.sin(1.2*ph)+.3*np.sin(1.5*ph))/1.6
        elif kind=='kick':
            wave=np.sin(ph+4*(1-np.exp(-32*t)))
        else:
            noise=rng.standard_normal(len(t))
            wave=np.diff(noise,prepend=noise[0])*.42
        song[i:j]+=amp*wave*(1-np.exp(-1000*t))*np.exp(-decay*t)
    quarter=.49;roots=[82.4069,82.4069,98.,73.416]
    pattern={0:1.,3:1.,6:1.5,10:1.2,14:2.}
    for step,at in enumerate(np.arange(.055,n/sr,quarter/4)):
        tick=step%16;root=roots[(step//16)%4]
        if tick in pattern:hit(at,root*pattern[tick],.077,12)
        if tick in (2,7,11,15):hit(at,root*4,.029,22,'chord')
        if tick in (0,10):hit(at,57,.045,17,'kick')
        if tick in (4,12):hit(at,0,.028,38,'snare')
        if tick%2==0:hit(at,0,.012 if tick%4 else .008,75,'hat')
    # Amplify the groove on arrival at the concert.
    for idx,(start,key) in enumerate(shots):
        if key=='gig':
            end=shots[idx+1][0] if idx+1<len(shots) else n/sr
            i,j=round(start*sr),round(end*sr); edges=min(6000,(j-i)//2)
            env=np.ones(j-i)
            if edges:env[:edges]=np.linspace(0,1,edges);env[-edges:]=np.linspace(1,0,edges)
            song[i:j]*=1+.38*env
    song*=.19
    if first_end:
        z=np.arange(n)/sr
        # Conductor holds still until the word 'Всё'.
        song*=1-np.clip((z-(first_end-.64))/.12,0,1)*np.clip((first_end+.60-z)/.12,0,1)
    if ru:
        i=n-round(.17*sr)
        song[max(0,i-int(.20*sr)):i]*=np.linspace(1,0,min(i,int(.20*sr)))
        song[i:]=0
        hit(i/sr,130,.052,95,'snare')
    return song
