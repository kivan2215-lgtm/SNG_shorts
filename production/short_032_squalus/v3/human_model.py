"""Clothed, rigged generic adult crew using the MakeHuman CC0 base and weights.
No figure depicts an identified historical individual. No MakeHuman application
code is imported: this module interprets the openly licensed mesh/rig data.
"""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).parent/'human'
CACHE=None
PEOPLE=[]

def asset():
 global CACHE
 if CACHE is not None:return CACHE
 verts=[];faces=[];group='';allgroups={}
 for l in (P/'base.obj').read_text().splitlines():
  if l.startswith('v '):verts.append(list(map(float,l.split()[1:])))
  elif l.startswith('g '):group=l[2:]
  elif l.startswith('f ') and group=='body':faces.append([int(x.split('/')[0])-1 for x in l.split()[1:]])
 v=np.array(verts)
 for n in ['male.target','average.target']:
  for l in (P/n).read_text().splitlines():
   if l and not l.startswith('#'):
    q=l.split();v[int(q[0])]+=np.array(list(map(float,q[1:])))
 v=np.stack([v[:,0],-v[:,2],v[:,1]-v[:,1].min()],1)*.1008
 rig=json.loads((P/'default.mhskel').read_text());weights=json.loads((P/'default_weights.mhw').read_text())['weights']
 joints={n:Vector(v[ii].mean(0)) for n,ii in rig['joints'].items()}
 skin=np.zeros(len(v));shoes=np.zeros(len(v))
 for n,pairs in weights.items():
  if n.startswith(('finger','wrist','head','neck','jaw','eye','tongue','special','levator','oris','oculi','risorius','temporalis','temporalis','temporalis','temporalis')):
   for idx,w in pairs:skin[idx]+=w
  if n.startswith(('foot','toe')):
   for idx,w in pairs:shoes[idx]+=w
 # Clothes are a separate, loose silhouette in the covered regions.
 nrm=np.zeros_like(v)
 for f in faces:
  normal=np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]])
  for i in f:nrm[i]+=normal
 lengths=np.linalg.norm(nrm,axis=1);nrm/=np.maximum(lengths[:,None],1e-8)
 covered=(skin<.25)&(v[:,2]>.13)&(v[:,2]<1.55)
 shaped=v.copy();shaped[covered]+=nrm[covered]*.018
 # Clothing creases are subtle geometry, not exposed anatomy painted blue.
 shaped[covered]+=nrm[covered]*(.002*np.sin(v[covered,2]*85+v[covered,0]*11))[:,None]
 # Shape a loose work shirt and trousers, removing anatomical surface detail
 # from garment-covered areas (including the front of the trousers).
 shirt=(v[:,2]>1.00)&(v[:,2]<1.52)&(np.abs(v[:,0])<.19)&(v[:,1]<-.04)
 target=-.125-.018*np.sin((v[shirt,2]-1)/.52*math.pi)
 shaped[shirt,1]=.15*shaped[shirt,1]+.85*target
 crotch=(v[:,2]>.74)&(v[:,2]<1.00)&(np.abs(v[:,0])<.115)&(v[:,1]<-.09)
 shaped[crotch,1]=-.095
 back=(v[:,2]>1.0)&(v[:,2]<1.52)&(np.abs(v[:,0])<.18)&(v[:,1]>.015)
 shaped[back,1]=.15*shaped[back,1]+.85*(.105+.01*np.sin((v[back,2]-1)/.52*math.pi))
 pantsback=(v[:,2]>.74)&(v[:,2]<1.0)&(np.abs(v[:,0])<.17)&(v[:,1]>.04)
 shaped[pantsback,1]=.115-.02*(v[pantsback,0]/.17)**2
 materials=[]
 for f in faces:
  center=v[f].mean(0)
  if center[2]>1.71 and (center[1]>-.09 or center[2]>1.775):mi=4
  elif center[2]>.154 and (skin[f].mean()>.45 or center[2]>1.55):mi=0
  elif shoes[f].mean()>.3 or center[2]<.14:mi=3
  elif center[2]<1.00:mi=2
  else:mi=1
  materials.append(mi)
 CACHE=(shaped,faces,rig,weights,joints,materials)
 return CACHE

def create(name,loc,M,empty,uv,cyl,curve,parent=None,diver=False,pose='stand'):
 v,faces,desc,weights,joints,face_mats=asset()
 root=empty(name,loc,parent)
 armdata=bpy.data.armatures.new(name+' skeleton');arm=bpy.data.objects.new(name+' rig',armdata);bpy.context.collection.objects.link(arm);arm.parent=root
 bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n,b in desc['bones'].items():
  eb=armdata.edit_bones.new(n);eb.head=joints[b['head']];eb.tail=joints[b['tail']]
  if (eb.head-eb.tail).length<1e-5:eb.tail.z+=.001
 for n,b in desc['bones'].items():
  eb=armdata.edit_bones[n]
  if b['parent']:eb.parent=armdata.edit_bones[b['parent']]
  plane=desc['planes'].get(b['rotation_plane'])
  if plane:
   a,bp,c=[joints[q] for q in plane];normal=(bp-a).cross(c-a)
   if normal.length>1e-6:eb.align_roll(normal)
 bpy.ops.object.mode_set(mode='OBJECT');arm.select_set(False)
 me=bpy.data.meshes.new(name+' body mesh');me.from_pydata(v.tolist(),[],faces);me.update();body=bpy.data.objects.new(name+' dressed crew',me);bpy.context.collection.objects.link(body);body.parent=root
 names=['skin','canvas' if diver else 'cloth','canvas' if diver else 'trousers','boot','hair']
 for n in names:me.materials.append(M[n])
 for f,mi in zip(me.polygons,face_mats):f.material_index=mi;f.use_smooth=True
 for n,pairs in weights.items():
  vg=body.vertex_groups.new(name=n)
  for i,w in pairs:vg.add([i],w,'REPLACE')
 mod=body.modifiers.new('anatomical skinning','ARMATURE');mod.object=arm;mod.use_deform_preserve_volume=True
 sub=body.modifiers.new('smooth anatomy','SUBSURF');sub.levels=1;sub.render_levels=1
 targets={}
 for side,sign in [('L',1),('R',-1)]:
  for limb,bone,loc0,pole0 in [('arm','lowerarm02.'+side,(sign*.24,-.07,.86),(sign*.5,-.8,1.2)),('leg','lowerleg02.'+side,(sign*.14,-.015,.10),(sign*.15,-.9,.6))]:
   target=empty(name+' '+limb+side+' target',loc0,root);pole=empty(name+' '+limb+side+' pole',pole0,root)
   con=arm.pose.bones[bone].constraints.new('IK');con.target=target;con.pole_target=pole;con.chain_count=4;con.use_stretch=False;con.iterations=64
   targets[limb+side]=target
  # Keep the ankle's orientation stable as IK changes the hip/knee angles.
  foot=arm.pose.bones['foot.'+side]
  orient=empty(name+' shoe orientation '+side,(0,0,0),root)
  orient.rotation_euler=armdata.bones['foot.'+side].matrix_local.to_euler()
  con=foot.constraints.new('COPY_ROTATION');con.target=orient;con.owner_space='POSE';con.target_space='LOCAL'
 # The eye spheres sit in real sockets, instead of dots on an oval head.
 for side in ['L','R']:
  b=desc['bones']['eye.'+side];center=joints[b['head']]
  eye=uv(name+' eye',center,(.010,.010,.010),'eyewhite',root)
  iris=uv(name+' iris',(center.x,center.y-.009,center.z),(.0045,.002,.0045),'iris',root)
 # Simple period work-shirt details are small enough not to obstruct movement.
 if not diver:
  for z in [1.09,1.17,1.25,1.33,1.41]:cyl(name+' shirt button',(0,-.151,z),.008,.007,'brass',(0,-1,0),root)
  curve(name+' shirt placket',[(0,-.151,1.04),(0,-.153,1.43)],.003,'seam',root)
  curve(name+' collar left',[(-.065,-.065,1.565),(-.09,-.13,1.52),(0,-.145,1.47)],.014,'cloth',root)
  curve(name+' collar right',[(.065,-.065,1.565),(.09,-.13,1.52),(0,-.145,1.47)],.014,'cloth',root)
 else:
  uv(name+' copper diving helmet',(0,-.03,1.70),(.18,.175,.205),'brass',root)
  uv(name+' helmet window',(0,-.195,1.70),(.105,.035,.105),'dark',root)
  cyl(name+' helmet neck ring',(0,0,1.52),.22,.065,'brass',parent=root)
 boots={}
 for side,sgn in [('L',1),('R',-1)]:
  boots[side]=uv(name+' leather boot '+side,(sgn*.14,-.07,.09),(.068,.143,.065),'boot',root)
 state={'boots':boots,'root':root,'armature':arm,'targets':targets,'pose':pose,'phase':len(PEOPLE)*1.7,'diver':diver}
 PEOPLE.append(state);root['human_index']=len(PEOPLE)-1
 pose_person(root,0)
 return root

def pose_person(root,p,climb=False):
 st=PEOPLE[int(root['human_index'])];t=st['targets'];pose=st['pose']
 if climb:
  # Three distinct reaches, then hands release and feet settle on the platform.
  phase=p*math.pi*5;settle=max(0,min(1,(p-.72)/.20));settle=settle*settle*(3-2*settle)
  for side,sgn in [('L',1),('R',-1)]:
   q=phase+(0 if side=='L' else math.pi);lift=max(0,math.sin(q))*.24*(1-settle)
   if p>.74:
    step=max(0,min(1,(p-(.74 if side=='L' else .84))/(.21 if side=='L' else .16)));lift=.12*math.sin(math.pi*step)
   t['leg'+side].location=(sgn*.12,-.10*(1-settle),.10+lift)
   handz=min(1.42+.17*math.sin(q+math.pi),3.80-root.location.z)
   t['arm'+side].location=(sgn*(.34-.10*settle),-.55*(1-settle)-.055*settle,handz*(1-settle)+.86*settle)
 elif pose=='attach':
  for side,sgn in [('L',1),('R',-1)]:
   t['arm'+side].location=(sgn*.16,-.44,1.02)
 else:
  for side,sgn in [('L',1),('R',-1)]:
   t['arm'+side].location=(sgn*.24,-.07,.86)
 for side,shoe in st['boots'].items():
  q=t['leg'+side].location;shoe.location=(q.x,q.y-.055,q.z-.035)
 return root

def operate_control(root,p):
 """Reach, turn a nearby control wheel and release; no disconnected hand sweep."""
 st=PEOPLE[int(root['human_index'])];t=st['targets']
 smooth=lambda x:(lambda q:q*q*q*(q*(q*6-15)+10))(max(0,min(1,x)))
 reach=smooth(p/.15)*(1-smooth((p-.82)/.18));turn=1.7*smooth((p-.18)/.47)
 a=math.pi/2+turn
 contact=Vector((.47+.16*math.cos(a),-.40,1.15+.16*math.sin(a)))
 rest=Vector((.24,-.07,.86));t['armL'].location=rest.lerp(contact,reach)

def handle_line(root,p):
 st=PEOPLE[int(root['human_index'])];q=max(0,min(1,p/.65));q=q*q*(3-2*q)
 for side,sgn in [('L',1),('R',-1)]:
  st['targets']['arm'+side].location=(sgn*.08,-.45-.10*q,1.02+.035*math.sin(math.pi*p))
