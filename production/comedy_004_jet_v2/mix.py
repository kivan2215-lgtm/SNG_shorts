import numpy as np
def score(n,sr,shots,voice):
    music=np.zeros(n); tau=2*np.pi
    def hit(at,f,level,decay=12,length=.26):
        st=max(0,int(sr*at));ed=min(n,st+int(length*sr))
        if ed<=st:return
        t=np.arange(ed-st)/sr
        music[st:ed]+=level*(1-np.exp(-150*t))*np.exp(-decay*t)*(np.sin(tau*f*t)+.22*np.sin(tau*2*f*t))
    roots=[130.81,164.81,146.83,98.]
    for i,beat in enumerate(np.arange(.12,n/sr,.345)):
        f=roots[(i//8)%4]
        if i%8 in (0,3,6):hit(beat,f,.54,13)
        if i%8 in (2,5,7):hit(beat,f*[2,2.5,3][i%3],.21,18)
    rms=lambda a:np.sqrt(np.mean(a*a))
    music*=.042*rms(voice)/(rms(music)+1e-10)
    for start,key in shots:
        if key in ('balance','purchase','shipping','total','refund','chat'):
            hit(start+.05,{'balance':420,'purchase':490,'shipping':580,'total':740,'refund':170,'chat':670}[key],.019,20,.14)
        if key=='total':hit(start+.16,990,.017,16,.23)
        if key in ('ledger','wink'):
            a=int(start*sr);b=min(n,a+int(.34*sr));music[a:b]*=.18
    return music
