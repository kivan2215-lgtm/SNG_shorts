import numpy as np
def score(n,sr,shots,voice):
    music=np.zeros(n); tau=2*np.pi
    def hit(at,f,level,decay=12,length=.26):
        st=max(0,int(sr*at));ed=min(n,st+int(length*sr))
        if ed<=st:return
        t=np.arange(ed-st)/sr
        music[st:ed]+=level*(1-np.exp(-150*t))*np.exp(-decay*t)*(np.sin(tau*f*t)+.22*np.sin(tau*2*f*t))
    roots=[138.59,116.54,155.56,103.83]
    for i,beat in enumerate(np.arange(.12,n/sr,.29)):
        f=roots[(i//8)%4]
        if i%8 in (0,3,6):hit(beat,f,.54,13)
        if i%8 in (2,5,7):hit(beat,f*[2,2.5,3][i%3],.21,18)
    rms=lambda a:np.sqrt(np.mean(a*a))
    music*=.042*rms(voice)/(rms(music)+1e-10)
    for start,key in shots:
        if key in ('reverse','cutaway','escorted','grading'):
            hit(start+.07,311,.024,16);hit(start+.21,233,.015,19)
        if key=='prof':
            a=int(start*sr);b=min(n,a+int(.38*sr));music[a:b]*=.15
    return music
