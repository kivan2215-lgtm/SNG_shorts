"""Reuse unchanged pixels only; every moving object is ray-traced at 30 fps.
Probe full frames to enclose motion and its shadows. Padding and feathering keep
subtle indirect-light differences from creating a rectangular boundary.
"""
from pathlib import Path
from PIL import Image
import numpy as np,json,sys
mode=sys.argv[1];p=Path(sys.argv[2])
if mode=='bounds':
 files=sorted(p.glob('probe_*.jpg'));base=np.asarray(Image.open(files[0]).convert('RGB')).astype(np.int16);h,w=base.shape[:2]
 mask=np.zeros((h,w),bool)
 for f in files[1:]:
  a=np.asarray(Image.open(f).convert('RGB')).astype(np.int16)
  mask|=np.max(abs(a-base),axis=2)>24
 yy,xx=np.where(mask)
 if len(xx):box=[max(0,int(xx.min())-40),max(0,int(yy.min())-40),min(w,int(xx.max())+41),min(h,int(yy.max())+41)]
 else:box=[0,0,w,h]
 box=[box[0]//4*4,box[1]//4*4,min(w,(box[2]+3)//4*4),min(h,(box[3]+3)//4*4)]
 if (box[2]-box[0])*(box[3]-box[1])>w*h*.85:box=[0,0,w,h]
 err=[];outside=np.ones((h,w),bool);outside[box[1]:box[3],box[0]:box[2]]=False
 for f in files[1:]:
  d=abs(np.asarray(Image.open(f)).astype(np.int16)-base)
  err.append(float(d[outside].mean()) if outside.any() else 0)
 out={'box_top_left_pixels':box,'source_size':[w,h],'outside_mean_abs_error_8bit':err,'probe_count':len(files),'feather_pixels':16}
 (p/'region.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
else:
 meta=json.loads((p/'index.json').read_text());box=meta['region']['box_top_left_pixels'];x0,y0,x1,y1=box
 base=Image.open(p/'probe_0000.jpg').convert('RGB');patchsize=(x1-x0,y1-y0)
 xx,yy=np.meshgrid(np.arange(patchsize[0]),np.arange(patchsize[1]));dist=np.minimum.reduce([xx,yy,patchsize[0]-1-xx,patchsize[1]-1-yy]);alpha=np.clip(dist/16,0,1)[...,None]
 old=np.asarray(base.crop(box),dtype=np.float32)
 for i in range(meta['count']):
  dst=p/f'{i:04d}.jpg';probe=p/f'probe_{i:04d}.jpg'
  if probe.exists():
   # Match outer frozen background at probe frames too; no seams or brightness jumps.
   patch=Image.open(probe).convert('RGB').crop(box)
  else:
   raw=Image.open(p/f'patch_{i:04d}.jpg').convert('RGB')
   # Blender stores border fractions as float32; recover the actual pixel box.
   # Place native pixels at their correct offset, never stretch a cropped frame.
   w,h=meta['region']['source_size']
   actual=meta['region'].get('actual_box_top_left_pixels')
   if actual is None:
    actual=[int(np.float32(x0/w)*np.float32(w)),h-int(np.float32(1-y0/h)*np.float32(h)),int(np.float32(x1/w)*np.float32(w)),h-int(np.float32(1-y1/h)*np.float32(h))]
   ax0,ay0,ax1,ay1=actual
   if raw.size!=(ax1-ax0,ay1-ay0):raise ValueError((i,raw.size,actual,box))
   if max(abs(a-b) for a,b in zip(actual,box))>1:raise ValueError(('unexpected border mismatch',actual,box))
   patch=base.crop(box);patch.paste(raw,(ax0-x0,ay0-y0))
  if patch.size!=patchsize:raise ValueError((i,patch.size,patchsize))
  im=base.copy();arr=np.asarray(patch,dtype=np.float32)*alpha+old*(1-alpha)
  im.paste(Image.fromarray(np.uint8(np.clip(arr,0,255))),(x0,y0));im.save(dst,quality=96)
 meta['processed']=True;(p/'index.json').write_text(json.dumps(meta));print('composited',p.name,meta['count'])
