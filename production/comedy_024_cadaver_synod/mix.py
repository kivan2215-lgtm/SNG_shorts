"""Original plucked-string rondo. No sampled music."""
import numpy as np

def score(n,sr,shots,voice,ru):
    music=np.zeros(n)
    def string(at,freq,level,short=False):
        i=max(0,round(at*sr));j=min(n,i+round((.27 if short else .70)*sr))
        if j<=i:return
        t=np.arange(j-i)/sr
        e=np.exp(-t*(16 if short else 7.5))
        y=np.zeros_like(t)
        for h,portion in ((1,1.),(2,.34),(3,.23),(4,.10),(6,.05)):
            y+=portion*np.sin(2*np.pi*freq*h*t)*np.exp(-t*(h-1)*4.)
        music[i:j]+=level*y*e*(1-np.exp(-t*850))
    def seal(at):
        i=round(at*sr);j=min(n,i+round(.19*sr))
        t=np.arange(j-i)/sr;rng=np.random.default_rng(241)
        music[i:j]+=(.014*np.sin(2*np.pi*82*t)+.008*rng.standard_normal(len(t)))*np.exp(-34*t)*(1-np.exp(-t*670))
    half=.244
    melody=(0,None,7,3,None,5,7,None,0,12,None,10,7,None,5,None)
    for beat,t in enumerate(np.arange(.05,n/sr,half)):
        note=melody[beat%16]; root=(164.81,146.83,130.81,146.83)[beat//16%4]
        if beat%8 in (0,5):string(t,root*.50,.65)
        if note is not None:string(t,root*2**(note/12),.43 if beat%4 else .56,beat%4!=0)
    rms=lambda x:np.sqrt(np.mean(x*x))
    music*=.081*rms(voice)/(rms(music)+1e-10)
    for i,(start,key) in enumerate(shots):
        end=shots[i+1][0] if i+1<len(shots) else n/sr
        if key in ('seal','restored'):seal(start+.18)
        if key in ('sandal','guard','summons','boss'):
            a=max(0,round(start*sr));b=min(n,round((min(start+.52,end))*sr))
            if b>a:music[a:b]*=np.interp(np.arange(b-a)/sr,[0,.035,.34,.52],[1,.04,.04,1])
    return music
