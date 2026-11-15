"""Topic-specific explanatory models, not actual evidence or medical instructions."""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).parent;K=sys.argv[sys.argv.index('--')+1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.use_denoising=True;S.cycles.max_bounces=4
S.render.resolution_x=720;S.render.resolution_y=1280;S.render.resolution_percentage=100;S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=96
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.035,.05,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.4
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast'
def mat(n,c,metal=0,rough=.5,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 if emit:b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=emit
 return m
M={'ivory':mat('Ivory enamel',(.67,.68,.62),.1),'steel':mat('Brushed stainless steel',(.29,.34,.35),.8,.28),'dark':mat('Matte charcoal',(.018,.027,.034),.1,.62),'blue':mat('Blue vinyl',(.025,.095,.16),0,.7),'red':mat('Dark red sample',(.25,.012,.018),0,.38),'glass':mat('Frosted polymer',(.40,.57,.60),.15,.22),'wood':mat('Walnut',(.12,.055,.027),0,.6),'paper':mat('Warm paper',(.77,.74,.63),0,.95),'skin':mat('Neutral anatomical model',(.43,.29,.21),0,.85),'cyan':mat('Indicator cyan',(.05,.46,.53),0,.35,1),'gold':mat('Evidence accent',(.8,.38,.07),.25),'screen':mat('CRT screen',(.015,.065,.055),.15,.27)}
M['glass'].node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.7
M['glass'].node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.45
def finish(o,m):
 o.data.materials.append(M[m] if isinstance(m,str) else m)
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def box(n,l,sc,m,bevel=.06):
 bpy.ops.mesh.primitive_cube_add(size=1,location=l);o=bpy.context.object;o.name=n;o.scale=sc;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,m)
 b=o.modifiers.new('Soft manufactured edges','BEVEL');b.width=bevel;b.segments=3;return o
def sphere(n,l,sc,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=l);o=bpy.context.object;o.name=n;o.scale=sc;return finish(o,m)
def rod(n,a,b,r,m):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,m)
def curve(n,pts,r,m):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for bp,p in zip(sp.bezier_points,pts):bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,cu);S.collection.objects.link(o);finish(o,m);return o
def camera(pos,target,scale):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;S.camera=o
anchors={}
def vial(n,l,col='red',cap='blue',scale=1):
 x,y,z=l;r=.22*scale
 rod(n+' opaque sample container',(x,y,z),(x,y,z+1.2*scale),r,'glass');rod(n+' sample',(x,y-.025,z+.08*scale),(x,y-.025,z+.85*scale),r*.78,col)
 rod(n+' stopper',(x,y,z+1.15*scale),(x,y,z+1.4*scale),r*1.12,cap)
 box(n+' blank identification band',(x,y-.21*scale,z+.65*scale),(.30*scale,.035*scale,.38*scale),'paper',.015)
 for i in range(7):box(n+' barcode',(x-.11*scale+i*.035*scale,y-.233*scale,z+.65*scale),(.012*scale,.008,.25*scale),'dark',.001)
def clinic():
 box('Floor',(0,0,-.18),(8,7,.3),'dark');box('Back wall',(0,3.5,1.7),(8,.18,3.7),'ivory');box('Left wall',(-4,0,1.7),(.18,7,3.7),'ivory')
 for z in [.18,3.25]:box('Wall trim',(0,3.36,z),(8,.08,.09),'wood')
 box('Window',(-1.4,3.36,2.2),(2.5,.08,1.65),'blue')
 for z in [1.5+i*.16 for i in range(10)]:box('Blind slat',(-1.4,3.26,z),(2.48,.05,.055),'paper')
 box('Examination couch',(1.1,.7,.9),(1.7,3.2,.3),'blue');box('Pillow',(1.1,1.7,1.14),(1.45,.70,.19),'paper')
 for x in [.45,1.75]:
  for y in [-.4,1.8]:rod('Couch leg',(x,y,0),(x,y,.75),.065,'steel')
 box('Cabinet',(2.6,2.8,1),(1.4,.8,2),'ivory')
 for z in [.35,.85,1.35]:
  box('Drawer front',(2.6,2.35,z),(1.25,.05,.42),'ivory');rod('Handle',(2.35,2.29,z),(2.85,2.29,z),.025,'steel')
 box('Desk',(-2,-1.3,1.15),(2.8,1.5,.12),'wood')
 for x in [-3.1,-.9]:
  for y in [-1.85,-.75]:rod('Desk leg',(x,y,0),(x,y,1.1),.045,'steel')
 box('Chart',(-2,-1.4,1.23),(.7,.95,.04),'paper');curve('Stethoscope',[(-2.8,-1.4,1.24),(-2.7,-.9,1.24),(-2.1,-.85,1.24)],.025,'dark')
 sphere('Stethoscope chestpiece',(-2.1,-.85,1.26),(.12,.12,.035),'steel')
 # No assault is staged; the empty room locates the account without depicting a victim.
 anchors.update(couch=(1.1,.7,1.2),chart=(-2,-1.4,1.24));camera((9,-12,10),(0,0,1),16)
 if K=='clinic_close':camera((6,-9,7),(.6,1,1),14)
def lab():
 box('Laboratory worktop',(0,0,-.1),(8,4.5,.25),'ivory');box('Bench base',(0,0,-.8),(7.8,4.3,1.2),'dark')
 box('1990s analyzer',(1.65,.7,.65),(3.4,2,1.35),'ivory');box('Analyzer dark control face',(1.65,-.33,.65),(2.9,.07,.85),'dark');box('CRT status',(1,-.39,.72),(1.35,.06,.55),'screen')
 for i in range(4):rod('Analyzer button',(2.05+i*.21,-.42,.45),(2.05+i*.21,-.48,.45),.055,'ivory')
 for x in [1.7+i*.12 for i in range(10)]:box('Vent',(x,1.71,.70),(.04,.02,.65),'dark',.005)
 for i in range(3):vial('Evidence sample '+str(i),(-2.5+i*.75,-.75,.10),'red','blue' if i!=1 else 'gold')
 box('Sample rack',(-1.75,-.75,.25),(2.8,.85,.12),'steel')
 for x in [-3,-.5]:rod('Rack leg',(x,-.75,0),(x,-.75,.35),.05,'steel')
 box('Lab paper',(1.4,-1.45,.08),(2,.65,.035),'paper');anchors.update(sampleA=(-2.5,-.75,1.5),sampleB=(-1.75,-.75,1.5),screen=(1,-.45,.72));camera((8,-13,9),(0,0,.35),15)
def folder():
 box('Desk surface',(0,0,-.12),(8,5,.2),'wood');box('Folder cover',(0,0,.04),(4.9,3.3,.07),'gold')
 for i in range(8):box('Paper leaf',(0,.1,.12+i*.018),(4.6,2.9,.014),'paper',.01)
 box('Folder tab',(-1.65,1.8,.03),(1.3,.5,.05),'gold')
 for i in range(6):box('Unlabelled print rule',(.15,-.9+i*.3,.27),(3.2,.018,.004),'dark',.001)
 box('Binder clip',(-2.2,.6,.32),(.25,.6,.2),'steel');anchors['file']=(0,0,.3);camera((7,-10,11),(0,0,0),13)
def balm(l=(0,0,0),scale=1,opened=False):
 x,y,z=l;rod('Lip balm casing',(x,y,z),(x,y,z+1.5*scale),.36*scale,'blue');rod('Lip balm ring',(x,y,z+1.45*scale),(x,y,z+1.65*scale),.38*scale,'steel');rod('Wax lip balm',(x,y,z+1.6*scale),(x,y,z+2.1*scale),.29*scale,'paper')
 for j in range(10):rod('Grip detail',(x+.36*scale*math.cos(j*math.tau/10),y+.36*scale*math.sin(j*math.tau/10),z+.1*scale),(x+.36*scale*math.cos(j*math.tau/10),y+.36*scale*math.sin(j*math.tau/10),z+.43*scale),.015,'steel')
 rod('Removed cap',(x+1.1*scale,y+.25*scale,z),(x+1.1*scale,y+.25*scale,z+1.1*scale),.39*scale,'blue');anchors['balm']=(x,y,z+2.12*scale)
def car():
 box('Car floor',(0,0,-.15),(5.8,7,.3),'dark')
 for x in [-1.55,1.55]:
  box('Fabric seat cushion',(x,0,.6),(1.65,1.8,.4),'blue');o=box('Seat back',(x,.85,1.7),(1.65,.4,2),'blue');o.rotation_euler.x=-.12;box('Head restraint',(x,1.05,2.8),(1.05,.35,.65),'blue')
  for xx in [x-.6,x+.6]:box('Seat seam',(xx,-.1,.82),(.025,1.5,.012),'steel',.005)
 box('Center console',(0,-.7,.50),(.85,2.1,.9),'dark');box('Console recess',(0,-.65,.98),(.65,1,.025),'wood')
 box('Dashboard',(0,-2.55,1.7),(5.5,1,1.2),'dark');box('Instrument panel',(-1.5,-2.0,2),(1.5,.1,.6),'screen')
 pts=[(-1.55+.53*math.cos(i*math.tau/32),-1.7,2.1+.53*math.sin(i*math.tau/32)) for i in range(33)];curve('Steering wheel',pts,.07,'dark');rod('Wheel spoke',(-2.05,-1.7,2.1),(-1.05,-1.7,2.1),.05,'steel')
 balm((0,-.6,1),.23);anchors['car']=(0,-.6,1.5);camera((7,1,18),(0,-.5,1.3),14.5)
def balm_close():
 box('Evidence tray',(0,0,-.1),(4.8,3.1,.2),'steel');balm((-.5,0,.05),1.1)
 rod('Swab handle',(-1.8,-.8,.1),(-1.8,1.1,.1),.035,'ivory');sphere('Swab cotton',(-1.8,1.2,.1),(.09,.2,.09),'paper');camera((6,-10,7),(0,0,1),10)
def hair():
 box('Sample tray',(0,0,-.1),(5,4,.18),'ivory')
 for x in [-.6,-.2,.2]:curve('Hair shaft',[(x,-1,.08),(x+.25,0,.1),(x,1,.09)],.018,'wood');sphere('Hair root',(x,-1.05,.1),(.045,.07,.035),'gold')
 vial('New independent sample',(1.7,.5,.0));anchors.update(hair=(0,-1.05,.1),sample=(1.7,.5,1.4));camera((5,-8,9),(0,0,.1),10.5)
def arm():
 import numpy as np
 hp=P/'human';verts=[];faces=[];group=''
 for l in (hp/'base.obj').read_text().splitlines():
  if l.startswith('v '):verts.append(list(map(float,l.split()[1:])))
  elif l.startswith('g '):group=l[2:]
  elif l.startswith('f ') and group=='body':faces.append([int(x.split('/')[0])-1 for x in l.split()[1:]])
 v=np.array(verts)
 for n in ['male.target','average.target']:
  for l in (hp/n).read_text().splitlines():
   if l and not l.startswith('#'):q=l.split();v[int(q[0])]+=np.array(list(map(float,q[1:])))
 v=np.stack([v[:,0],-v[:,2],v[:,1]-v[:,1].min()],1)*.1008
 rig=json.loads((hp/'default.mhskel').read_text());weights=json.loads((hp/'default_weights.mhw').read_text())['weights'];j={n:Vector(v[ii].mean(0)) for n,ii in rig['joints'].items()}
 shoulder=j['upperarm01.L____head'];elbow=j['lowerarm01.L____head'];wrist=j['wrist.L____head'];axis=(elbow-shoulder).normalized();ey=Vector((0,-1,0));ey=(ey-axis*ey.dot(axis)).normalized();ez=axis.cross(ey).normalized()
 rot=(wrist-elbow).normalized().rotation_difference(axis);lower=np.zeros(len(v));belongs=np.zeros(len(v))
 def descendant(name,ancestor):
  while name:
   if name==ancestor:return True
   name=rig['bones'].get(name,{}).get('parent')
  return False
 for name,pairs in weights.items():
  isarm=descendant(name,'upperarm01.L')
  islower=descendant(name,'lowerarm01.L')
  if isarm:
   for idx,w in pairs:belongs[idx]+=w
  if islower:
   for idx,w in pairs:lower[idx]+=w
 vv=[]
 for i,p in enumerate(v):
  point=Vector(p);q=elbow+rot@(point-elbow);point=point.lerp(q,min(1,lower[i]));rel=point-shoulder
  vv.append((rel.dot(axis)*12-3.5,rel.dot(ey)*12,rel.dot(ez)*12))
 vv=np.array(vv);keep=[]
 for f in faces:
  if min(belongs[f])<.48:continue
  c=vv[f].mean(0)
  if c[0]<-3.15:continue
  if K=='arm_open' and -2.95<c[0]<-1.2 and c[1]<-.02:continue
  keep.append(f)
 me=bpy.data.meshes.new('Anatomical arm mesh');me.from_pydata(vv.tolist(),[],keep);me.update();o=bpy.data.objects.new('Neutral anatomical explanatory model',me);S.collection.objects.link(o);finish(o,'skin')
 rod('Short fabric cuff',(-3.8,0,0),(-3.05,0,0),.70,'ivory')
 if K=='arm_open':
  rod('Concealed container',(-2.85,0,0),(-1.3,0,0),.19,'glass');rod('Foreign blood in container',(-2.78,-.13,0),(-1.37,-.13,0),.12,'red')
  for x in [-2.85,-1.3]:rod('Closed tube end',(x,0,0),(x+.05,0,0),.2,'ivory')
  anchors['tube']=(-2.1,-.16,.1)
 box('Display plinth',(.3,0,-.85),(10.5,3.5,.15),'dark');anchors['arm']=(-2.1,-.5,.3);camera((1,-14,10),(.3,0,0),20)

def court():
 box('Court floor',(0,0,-.12),(9,7,.2),'wood');box('Bench',(0,2,1.2),(7,1.5,2.4),'wood')
 for x in [-2.5,-1.25,0,1.25,2.5]:box('Bench raised panel',(x,1.20,1.2),(.95,.1,1.8),'gold')
 box('Witness desk',(-2,-1,.6),(2,1.5,1.2),'wood');box('Document',(0,1.9,2.44),(.9,1.3,.04),'paper');box('Judge chair',(0,2.9,2.3),(1.4,.35,1.7),'dark');anchors['court']=(0,1.3,2.4);camera((9,-12,10),(0,0,1),17)
if K in ['clinic','clinic_close']:clinic()
elif K in ['lab','lab_close']:
 lab()
 if K=='lab_close':camera((5,-8,6),(-1.3,-.4,.8),10)
elif K in ['folder','folder_motion']:folder()
elif K=='car':car()
elif K=='balm':balm_close()
elif K=='hair':hair()
elif K in ['arm_closed','arm_open']:arm()
elif K=='court':court()
else:raise ValueError(K)
# Continuous studio background; no artificial camera shake or zoom.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.6));finish(bpy.context.object,mat('Backdrop',(.018,.030,.042),0,.95))
for pos,power,size,col in [((-7,-10,12),2400,8,(.78,.88,1)),((6,-3,8),1700,7,(1,.78,.55)),((3,8,10),2800,6,(.4,.65,1))]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update();projected={}
for k,v in anchors.items():c=world_to_camera_view(S,S.camera,Vector(v));projected[k]=[c.x*1080,(1-c.y)*1920]
out=P/'frames'/K;out.mkdir(parents=True,exist_ok=True)
if K=='folder_motion':
 import subprocess,shutil
 cover=box('Closing folder cover',(0,0,.32),(4.9,3.3,.06),'gold')
 hinge=bpy.data.objects.new('Spine hinge',None);S.collection.objects.link(hinge);hinge.location=(0,1.65,.32);cover.parent=hinge;cover.location=(0,-1.65,0)
 def state(i):
  q=i/30;q=q*q*(3-2*q);hinge.rotation_euler.x=-math.radians(105)*(1-q)
 for f in out.glob('[0-9][0-9][0-9][0-9].jpg'):shutil.move(str(f),str(out/('probe_'+f.name)))
 probes=sorted(set([0,8,15,23,30]+[int(f.stem.split('_')[1]) for f in out.glob('probe_*.jpg')]))
 for i in probes:
  state(i);S.render.filepath=str(out/f'probe_{i:04d}.jpg')
  if not Path(S.render.filepath).exists():bpy.ops.render.render(write_still=True)
 result=subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'region_cache.py'),'bounds',str(out)],check=True,capture_output=True,text=True);region=json.loads(result.stdout)
 x0,y0,x1,y1=region['box_top_left_pixels'];w,h=region['source_size'];S.render.use_border=True;S.render.use_crop_to_border=True
 S.render.border_min_x=(x0+.1)/w;S.render.border_max_x=min(1,(x1+.1)/w);S.render.border_min_y=min(1,1-y1/h+.1/h);S.render.border_max_y=min(1,1-y0/h+.1/h)
 region['actual_box_top_left_pixels']=[int(S.render.border_min_x*w),h-int(S.render.border_max_y*h),int(S.render.border_max_x*w),h-int(S.render.border_min_y*h)]
 for i in range(31):
  state(i)
  if i not in probes:S.render.filepath=str(out/f'patch_{i:04d}.jpg');bpy.ops.render.render(write_still=True)
 S.render.use_border=False;S.render.use_crop_to_border=False
 (out/'index.json').write_text(json.dumps({'count':31,'anchors':projected,'native_fps':30,'source_resolution':[720,1280],'region':region}))
 subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'region_cache.py'),'stitch',str(out)],check=True)
else:
 S.render.filepath=str(out/'0000.jpg');bpy.ops.render.render(write_still=True)
if K!='folder_motion':(out/'index.json').write_text(json.dumps({'anchors':projected,'resolution':[720,1280],'count':1,'native_fps':30}))
(P/'models').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'{K}.blend'),compress=True)
