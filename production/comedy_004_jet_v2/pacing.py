import numpy as np
def tighten(samples,times,sr):
    frame=round(sr*.01)
    frames=np.array_split(samples[:len(samples)//frame*frame],len(samples)//frame)
    quiet=np.max(np.abs(np.asarray(frames)),axis=1)<.006
    edges=np.flatnonzero(np.diff(np.r_[False,quiet,False]))
    ranges=[]
    for lo,hi in edges.reshape(-1,2):
        if hi-lo<34:continue
        start=lo*frame;end=hi*frame
        a=start+(0 if lo==0 else round(.13*sr))
        b=end-round((.055 if lo==0 else .12)*sr)
        if b>a:ranges.append((a,b))
    if not ranges:return samples,times
    mask=np.ones(len(samples),bool)
    t=np.asarray(times)
    removed=np.zeros_like(t)
    for a,b in ranges:
        mask[a:b]=False
        removed+=np.clip(t-a/sr,0,(b-a)/sr)
    return samples[mask],(t-removed).tolist()
