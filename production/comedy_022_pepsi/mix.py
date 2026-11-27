import numpy as np
def score(n,sr,shots,voice):
    music=np.zeros(n); tau=2*np.pi
    def hit(at,f,level,decay=12,length=.26):
        st=max(0,int(sr*at));ed=min(n,st+int(length*sr))
        if ed<=st:return
        t=np.arange(ed-st)/sr
        music[st:ed]+=level*(1-np.exp(-150*t))*np.exp(-decay*t)*(np.sin(tau*f*t)+.22*np.sin(tau*2*f*t))
    roots=[164.81,130.81,110.,146.83]
    for i,beat in enumerate(np.arange(.12,n/sr,.288)):
        f=roots[(i//8)%4]
        if i%8 in (0,3,6):hit(beat,f,.54,13)
        if i%8 in (2,5,7):hit(beat,f*[2,2.5,3][i%3],.21,18)
    rms=lambda a:np.sqrt(np.mean(a*a))
    music*=.042*rms(voice)/(rms(music)+1e-10)
    rng=np.random.default_rng(22)
    def tap(at,duration,strength):
        start=max(0,round(at*sr));end=min(n,start+round(duration*sr))
        if end<=start:return
        t=np.arange(end-start)/sr
        grain=rng.standard_normal(len(t))
        grain=np.convolve(grain,[.25,.5,.25],mode='same')
        music[start:end]+=strength*grain*(1-np.exp(-1300*t))*np.exp(-75*t)
    for start,key in shots:
        if key=='order':
            for i in range(4):tap(start+.14+i*.092,.06,.027)
        elif key=='reject':
            tap(start+.22,.17,.058)
            hit(start+.22,96,.036,29)
        elif key=='courier':
            hit(start+.04,573,.022,9);hit(start+.25,471,.020,10)
        elif key=='finale':
            hit(start+.28,523,.025,9);hit(start+.48,659,.021,10)
    return music
