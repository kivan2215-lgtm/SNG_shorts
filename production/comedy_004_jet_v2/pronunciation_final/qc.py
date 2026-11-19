from scipy.io.wavfile import read
import numpy as np,json
a=read('/workspace/jet_v2/rumix.wav')[1].astype(float);sr,b=read('corrected.wav');b=b.astype(float);d=b-a
mask=np.abs(d)>8;idx=np.flatnonzero(mask);groups=np.split(idx,np.flatnonzero(np.diff(idx)>sr*.09)+1);groups=[x for x in groups if len(x)>100]
print('isolated word edits:',[(round(g[0]/sr,3),round(g[-1]/sr,3)) for g in groups], 'duration:',len(a)/sr)
assert len(a)==len(b) and len(groups)==7
