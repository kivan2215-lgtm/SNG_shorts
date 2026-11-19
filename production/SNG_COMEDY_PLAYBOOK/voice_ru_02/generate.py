"""Fit a parallel-utterance spectral transfer to the provided reference."""
from pathlib import Path
import numpy as np
import pyworld as world
from scipy.io import wavfile
from scipy.signal import resample_poly
from scipy.spatial.distance import cdist
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter1d
from scipy.fft import dct
from math import gcd

rate = 24000
period = 10.0
def load(path):
    sr, x = wavfile.read(path)
    g = gcd(sr, rate)
    return resample_poly(x.astype(float)/32768, rate//g, sr//g)

def analyze(x):
    f,t = world.dio(x,rate,frame_period=period,f0_floor=65,f0_ceil=440)
    f = world.stonemask(x,f,t,rate)
    sp = world.cheaptrick(x,f,t,rate,f0_floor=65)
    ap = world.d4c(x,f,t,rate,fft_size=(sp.shape[1]-1)*2)
    return f,np.log(sp.clip(1e-12)),ap

def features(s):
    hz = np.geomspace(140,7000,48)
    m = s[:,np.round(hz / (rate/2) * (s.shape[1]-1)).astype(int)]
    return dct(m,type=2,norm='ortho')[:,1:14]

def align(a,b):
    dist = cdist(a,b,'euclidean')
    cost = np.full((len(a)+1,len(b)+1),np.inf)
    cost[0,0] = 0
    for i in range(len(a)):
        for j in range(max(0,int(i*len(b)/len(a))-80),min(len(b),int(i*len(b)/len(a))+81)):
            cost[i+1,j+1] = dist[i,j]+min(cost[i,j],cost[i,j+1]+.6,cost[i+1,j]+.6)
    i,j = len(a),len(b)
    path = []
    while i and j:
        path.append((i-1,j-1))
        move = np.argmin([cost[i-1,j-1],cost[i-1,j]+.6,cost[i,j-1]+.6])
        i -= move!=2
        j -= move!=1
    return np.asarray(path).T

def train(src,ref):
    f,s,_=analyze(src)
    g,r,_=analyze(ref)
    a,b=features(s),features(r)
    ma,mb=a.mean(0),b.mean(0)
    sa,sb=a.std(0)+.1,b.std(0)+.1
    i,j=align((a-ma)/sa,(b-mb)/sb)
    keep=(f[i]>65)&(g[j]>70)
    i,j=i[keep],j[keep]
    residual=r[j]-s[i]
    residual-=np.median(residual[:,8:145],axis=1,keepdims=True)
    # Preserve fine speech detail; transfer only the smooth spectral shape.
    correction=gaussian_filter1d(residual,5,axis=1).clip(-2.5,2.5)
    np.savez_compressed('preset.npz',keys=((a[i]-ma)/sa).astype('f'),mean=ma,scale=sa,
                        correction=correction[:,::4].astype('f'),pitch=np.percentile(f[f>0],[10,50,90]),
                        target=np.percentile(g[g>0],[10,50,90]))

def render(x):
    model=np.load('preset.npz')
    f,s,ap=analyze(x)
    d,idx=cKDTree(model['keys']).query((features(s)-model['mean'])/model['scale'],k=28)
    weights=1/(d+.25)**2
    grid=np.einsum('ijk,ij->ik',model['correction'][idx],weights/weights.sum(1,keepdims=True))
    corr=np.stack([np.interp(np.arange(s.shape[1]),np.arange(row.size)*4,row) for row in grid])
    voiced=f>0
    orig,target=model['pitch'],model['target']
    semitones=np.log(np.maximum(f,1)/orig[1])
    spread=np.log(target[2]/target[0])/np.log(orig[2]/orig[0])
    f[voiced]=np.clip(target[1]*np.exp(semitones[voiced]*spread),100,390)
    s+=gaussian_filter1d(corr,1,axis=0)*voiced[:,None]*.84
    # Preserve consonant attacks while giving stressed vowels more time.
    speed=np.where(voiced,1.27,1.10)
    time=np.cumsum(speed); timeline=np.arange(time[0],time[-1])
    pos=np.interp(timeline,time,np.arange(len(f))); near=pos.round().astype(int)
    def interpolate(matrix):
        lo=pos.astype(int); hi=np.minimum(lo+1,len(matrix)-1); frac=(pos-lo)[:,None]
        return np.ascontiguousarray(matrix[lo]*(1-frac)+matrix[hi]*frac)
    y=world.synthesize(f[near].copy(),np.exp(interpolate(s)),interpolate(ap),rate,frame_period=period)
    return y*.88/max(abs(y))

if __name__=='__main__':
    src=load('/workspace/SNG_shorts/projects/comedy_002_mars/ru/voice.wav')
    ref=load('/workspace/voice_sample/audio.wav')
    train(src[:int(26.45*rate)],ref[:int(36.75*rate)])
    y=render(src[int(40.04*rate):int(48.515*rate)])
    wavfile.write('sample.wav',rate,(y*32767).astype('int16'))
