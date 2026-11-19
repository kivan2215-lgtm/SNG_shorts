import pyworld as pw
from scipy.io.wavfile import read
from scipy.signal import resample_poly
import numpy as np
def new_take(signal,marks):
 sr=24000
 rate,r=read('/workspace/jet_stress/ref0.wav');ref=r.astype(float)/32768
 assert rate==sr
 x=resample_poly(signal,1,2)
 def analyse(z):
  z=np.ascontiguousarray(z,dtype=float)
  f,t=pw.dio(z,sr,f0_floor=65,f0_ceil=440);f=pw.stonemask(z,f,t,sr)
  s=pw.cheaptrick(z,f,t,sr,f0_floor=65);a=pw.d4c(z,f,t,sr,fft_size=(s.shape[1]-1)*2)
  return f,t,s,a
 f,t,s,a=analyse(ref);g,gt,_,_=analyse(x[int(3.22*sr):int(4.13*sr)])
 timeline=np.arange(0,.54,.005)
 # Full, emphasized first vowel; brief reduced second vowel.
 refpos=np.interp(timeline,[0,.05,.12,.22,.33,.386,.437,.49,.54],[.46,.52,.60,.654,.74,.77,.805,.86,.91])
 def interp(mat):
  i=refpos/.005;lo=np.floor(i).astype(int);v=(i-lo)[:,None]
  return np.ascontiguousarray(mat[lo]*(1-v)+mat[lo+1]*v)
 near=np.rint(refpos/.005).astype(int);pitch=f[near].copy();v=pitch>0
 med=np.median(g[g>0]);pitch[v]*=med/np.median(pitch[v]);pitch*=2**((2.5*np.exp(-.5*((timeline-.21)/.065)**2)-1.8*np.exp(-.5*((timeline-.426)/.033)**2))/12)
 spec=interp(s);bins=np.arange(spec.shape[1]);spec=np.stack([np.interp(bins/1.08,bins,row) for row in spec]);sig=pw.synthesize(pitch,np.ascontiguousarray(spec),interp(a),sr)
 y=resample_poly(sig,2,1);start=round(3.425*48000);n=round(.54*48000);y=y[:n];old=signal[start:start+n];u=np.arange(n)/48000
 y*=10**((2.3*np.exp(-.5*((u-.21)/.07)**2)-3.5*np.exp(-.5*((u-.425)/.035)**2))/20)
 y*=np.linalg.norm(old)/np.linalg.norm(y)
 fade=np.minimum(np.clip(u/.022,0,1),np.clip((.54-u)/.023,0,1))
 signal[start:start+n]=old*(1-fade)+y*fade
