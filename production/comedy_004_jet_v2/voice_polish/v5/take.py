"""Match native speech grains to the approved take's timing and stress envelope."""
import numpy as np
from scipy.signal import correlate
from scipy.ndimage import gaussian_filter1d
from approved import new_take as approved_take

def new_take(signal,marks):
    sr=48000
    ref=signal.copy()
    approved_take(ref,marks)
    start=round(3.33*sr);end=round(4.06*sr)
    x=signal[start:end].copy();r=ref[start:end]
    u=(np.arange(len(x))+start)/sr
    # Word edges and letter landmarks aligned between original narration and approved V4.
    dst=np.array([3.33,3.445,3.475,3.525,3.62,3.755,3.845,3.915,3.95,4.06])
    src=np.array([3.33,*marks,4.06])
    m=np.interp(u,dst,src)*sr-start
    n=1152;hop=192;wing=216
    y=np.zeros_like(x);weight=np.zeros_like(x);win=np.hanning(n)
    for p in range(0,len(x)-n+1,hop):
        q=int(np.clip(m[p+n//2]-n//2,0,len(x)-n))
        if p==0 or u[p]<3.395 or u[p]>3.974:i=p
        else:
            l=max(0,q-wing);h=min(len(x)-n,q+wing);nn=n-hop
            w=np.minimum(weight[p:p+nn],1)
            target=y[p:p+nn]/np.maximum(weight[p:p+nn],1e-7)
            candidate=x[l:h+nn]
            sim=correlate(candidate,target*w,'valid')/np.sqrt(np.maximum(correlate(candidate**2,w,'valid'),1e-8)*max(np.sum(target**2*w),1e-8))
            i=l+np.argmax(sim-.065*((np.arange(l,h+1)-q)/wing)**2)
        y[p:p+n]+=x[i:i+n]*win;weight[p:p+n]+=win
    y=np.where(weight>.01,y/np.maximum(weight,.001),x)
    rms=lambda z:np.sqrt(gaussian_filter1d(z*z,380)+1e-6)
    # Match vowel prominence, preserving consonant transients.
    v=np.clip((u-3.52)/.047,0,1)*np.clip((3.90-u)/.046,0,1)
    y*=np.exp(v*np.clip(np.log(rms(r)/rms(y)),-1.15,1.15))
    fade=np.clip((u-3.415)/.045,0,1)*np.clip((3.969-u)/.042,0,1)
    signal[start:end]=x*(1-fade)+y*fade
