"""Original comedy explanatory dioramas. Schematic terrain and actors, not battle evidence."""
import bpy,math,random,sys,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).parent;K=sys.argv[sys.argv.index('--')+1];random.seed(38)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True;S.cycles.max_bounces=3
S.render.resolution_x=720;S.render.resolution_y=1280;S.render.resolution_percentage=100;S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=95
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.19,.23,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.5
S.view_settings.view_transform='AgX'
def mat(n,c,rough=.6,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
M={k:mat(k,c,r,me) for k,c,r,me in [('sand',(.37,.19,.07),.95,0),('earth',(.18,.08,.035),.95,0),('feather',(.12,.075,.04),.94,0),('tuft',(.25,.17,.09),.95,0),('neck',(.20,.22,.20),.8,0),('skin',(.48,.31,.19),.8,0),('black',(.012,.017,.018),.75,0),('beak',(.13,.12,.08),.6,0),('olive',(.21,.26,.12),.5,.15),('steel',(.19,.23,.22),.35,.7),('wood',(.28,.13,.05),.9,0),('gold',(.95,.49,.065),.4,.2),('cyan',(.06,.55,.62),.38,.2),('white',(.8,.75,.57),.8,0),('khaki',(.31,.27,.14),.9,0),('glass',(.25,.47,.5),.3,.2)]}
def empty(n,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(n,None);S.collection.objects.link(o);o.location=loc;o.parent=parent;return o
def finish(o,m,parent=None):
 o.data.materials.append(M[m]);o.parent=parent
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def box(n,l,sc,m,parent=None,b=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=l);o=bpy.context.object;o.name=n;o.scale=sc;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,m,parent)
 mo=o.modifiers.new('Soft edges','BEVEL');mo.width=b;mo.segments=2;return o
def uv(n,l,sc,m,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=l);o=bpy.context.object;o.name=n;o.scale=sc;return finish(o,m,parent)
def rod(n,a,b,r,m,parent=None):
 v=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=v.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return finish(o,m,parent)
def curve(n,pts,r,m,parent=None):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for a,p in zip(sp.bezier_points,pts):a.co=p;a.handle_left_type='AUTO';a.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,cu);S.collection.objects.link(o);finish(o,m,parent);return o
def emu(n,loc,scale=.7):
 root=empty(n,loc);root.scale=(scale,)*3
 uv('Shaggy emu body',(0,.08,1.1),(.38,.60,.45),'feather',root)
 curve('Long curved neck',[(0,-.26,1.2),(0,-.43,1.55),(0,-.42,1.94)],.09,'neck',root)
 uv('Head',(0,-.46,2.0),(.115,.19,.12),'neck',root);uv('Beak',(0,-.64,1.98),(.075,.11,.045),'beak',root)
 for x in [-.105,.105]:uv('Eye',(x,-.52,2.035),(.018,.018,.018),'black',root)
 for j in range(64):
  a=random.uniform(0,math.tau);z=random.uniform(-.6,.8);rr=math.sqrt(1-z*z);x=.38*rr*math.cos(a);y=.08+.60*rr*math.sin(a);zz=1.1+.45*z
  curve('Individual feather tuft',[(x,y,zz),(x*1.03,y+.08,zz-.06),(x*1.05,y+.16,zz-.16)],.008,'tuft',root)
 legs=[]
 for x in [-.15,.15]:
  thigh=rod('Upper leg',(x,0,.94),(x,.1,.52),.045,'neck',root);shin=rod('Lower leg',(x,.1,.52),(x,-.1,.10),.032,'neck',root)
  foot=empty('Three toed foot',(x,-.1,.09),root)
  for q in [-1,0,1]:rod('Toe',(0,0,0),(q*.075,-.18,.005),.018,'beak',foot)
  legs.append((thigh,shin,foot))
 return root,legs
def setrod(o,a,b):
 v=Vector(b)-Vector(a);o.location=(Vector(a)+Vector(b))/2;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.scale.z=v.length/o.dimensions.z if o.dimensions.z>0 else 1
 # Set depth using mesh base cylinder local Z, avoiding world bounding box.
 base=max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices);o.scale.z=v.length/base

def gait(bird,t,active):
 root,legs=bird
 for j,(a,b,foot) in enumerate(legs):
  x=[-.15,.15][j];phase=t*math.tau*2.4+j*math.pi;fy=-.05+math.sin(phase)*.25*active;fz=.09+max(0,math.cos(phase))*.12*active;knee=(x,.12+math.sin(phase)*.08*active,.53)
  setrod(a,(x,0,.94),knee);setrod(b,knee,(x,fy,fz));foot.location=(x,fy,fz)

def gun(loc,parent):
 ob=empty('Simplified Lewis gun exterior',loc,parent)
 rod('Barrel jacket',(0,.30,0),(0,-.85,0),.085,'steel',ob);box('Receiver',(0,.32,0),(.17,.38,.17),'steel',ob);box('Wood stock',(0,.68,-.01),(.14,.36,.14),'wood',ob)
 rod('Flat circular magazine',(0,.22,.1),(0,.22,.15),.24,'steel',ob)
 return ob

def terrain():
 vs=[];fs=[];N=35
 for j in range(N):
  for i in range(N):
   x=-5+i*10/(N-1);y=-4+j*8/(N-1);z=.025*math.sin(x*3)*math.cos(y*4);vs.append((x,y,z))
 for j in range(N-1):
  for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+1+N,a+N))
 me=bpy.data.meshes.new('Soil');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Continuous soil surface',me);S.collection.objects.link(o);finish(o,'sand')
 box('Earth cutaway',(0,0,-.22),(10,8,.4),'earth',b=.12)
 for x in [-4.7,-3.3,-1.9,-.5,.9,2.3,3.7,4.7]:
  rod('Fence post',(x,3.2,0),(x,3.2,.65),.04,'wood')
 for z in [.22,.45,.63]:rod('Fence wire',(-4.7,3.2,z),(4.7,3.2,z),.008,'steel')
 for j in range(100):
  x=random.uniform(-4.8,4.8);y=random.choice([random.uniform(-3.8,-3.0),random.uniform(2.7,3.8)]);rod('Wheat stalk',(x,y,.02),(x,y,.33),.008,'gold')
  uv('Wheat ear',(x,y,.37),(.027,.035,.09),'gold')
terrain();count=49 if K=='scatter' else 61
if K=='scatter':
 uv('Water landmark',(2.8,1.5,.03),(1.05,.75,.025),'glass')
 birds=[];starts=[];ends=[]
 for i in range(6):
  x=(i%3-1)*.62;y=(i//3)*.70-.6;b=emu('Emu '+str(i),(x,y,.03),.62);birds.append(b);starts.append((x,y));ends.append(([-3,-2.3,0,.5,2.5,3.2][i],[-1.6,-.5,1.8,2,-1.1,-.3][i]))
 marker=box('Human position',(-3.4,1.3,.08),(.9,.6,.14),'olive');gun((-3.4,1.3,.7),None)
 def state(i):
  u=i/(count-1);e=u*u*(3-2*u)
  for j,b in enumerate(birds):
   x,y=starts[j];xx,yy=ends[j];b[0].location=(x+(xx-x)*e,y+(yy-y)*e,.03);b[0].rotation_euler.z=math.atan2(xx-x,-(yy-y));gait(b,i/30,math.sin(math.pi*u)**.5 if 0<u<1 else 0)
 target=(0,0,.55);cam=(10,-15,16);scale=17.5
else:
 root=empty('Truck translation');body=empty('Sprung chassis',(0,0,0),root)
 box('Chassis',(0,0,.55),(3.5,1.4,.2),'steel',body)
 box('Engine hood',(-1.15,0,1.03),(1.05,1.24,.65),'olive',body);box('Radiator',(-1.70,0,1.04),(.08,1.08,.55),'steel',body)
 for y in [-.50,-.35,-.2,-.05,.1,.25,.4]:rod('Grille',(-1.76,y,.80),(-1.76,y,1.27),.018,'black',body)
 box('Cab floor',(-.2,0,.78),(.95,1.45,.16),'wood',body);box('Seat',(-.02,0,1.0),(.50,1.12,.23),'black',body);box('Seat back',(.22,0,1.28),(.13,1.12,.60),'black',body)
 for y in [-.65,.65]:rod('Windshield post',(-.62,y,1.1),(-.62,y,1.95),.035,'steel',body)
 rod('Windshield top',(-.62,-.65,1.95),(-.62,.65,1.95),.035,'steel',body);box('Windshield',(-.62,0,1.65),(.025,1.23,.53),'glass',body)
 box('Bed floor',(1.05,0,.77),(1.6,1.48,.15),'wood',body)
 for y in [-.74,.74]:
  for z in [1.0,1.22]:box('Wood sideboard',(1.05,y,z),(1.7,.07,.16),'wood',body)
 for y in [-.45,.45]:uv('Headlamp',(-1.77,y,1.27),(.09,.12,.12),'white',body)
 bpy.ops.mesh.primitive_torus_add(major_radius=.21,minor_radius=.018,major_segments=32,minor_segments=8,location=(-.45,-.18,1.34));steer=bpy.context.object;steer.rotation_euler.y=.55;finish(steer,'black',body)
 rod('Steering column',(-.65,-.18,.95),(-.45,-.18,1.34),.025,'steel',body)
 for yy in [-.2,.2]:rod('Steering spoke',(-.45,-.18,1.34),(-.45,-.18+yy,1.34),.012,'steel',body)
 wheels=[]
 for x in [-1.15,1.25]:
  rod('Axle',(x,-.85,.45),(x,.85,.45),.065,'steel',root)
  for y in [-.86,.86]:
   w=empty('Rolling wheel',(x,y,.45),root);rod('Tire',(0,-.15,0),(0,.15,0),.45,'black',w);rod('Wheel rim',(0,-.16,0),(0,.16,0),.27,'olive',w)
   for a in range(8):
    ang=a*math.tau/8;rod('Wheel spoke',(0,-.17,0),(.24*math.cos(ang),-.17,.24*math.sin(ang)),.015,'steel',w)
   wheels.append(w)
 # Deliberately modeled editorial miniatures, dressed and seated with visible support.
 def person(n,x,y,z,gunner=False):
  r=empty(n,(x,y,z),body);uv('Khaki torso',(0,0,.53),(.20,.25,.32),'khaki',r);uv('Head',(0,0,.96),(.14,.14,.18),'skin',r)
  uv('Hat crown',(0,0,1.1),(.17,.17,.11),'khaki',r);uv('Hat brim',(0,0,1.05),(.26,.25,.025),'khaki',r)
  for yy in [-.14,.14]:
   rod('Trouser upper',(0,yy,.35),(-.30,yy,.24),.095,'khaki',r);rod('Trouser lower',(-.30,yy,.24),(-.33,yy,.12 if gunner else .18),.07,'khaki',r);uv('Boot',(-.4,yy,.12 if gunner else .18),(.16,.08,.07),'black',r)
   rod('Upper arm',(-.03,yy*1.55,.72),(-.22,yy*1.8,.50),.065,'khaki',r);rod('Forearm',(-.22,yy*1.8,.50),(-.40,yy*1.5,.58),.055,'khaki',r);uv('Hand',(-.41,yy*1.5,.58),(.07,.045,.045),'skin',r)
  return r
 person('Driver',-.05,-.18,.76);box('Gunner seat',(1.45,0,1.05),(.42,.55,.20),'wood',body);person('Seated gunner',1.45,0,.8,True)
 weapon=gun((.91,0,1.38),body);weapon.rotation_euler.z=-math.pi/2
 rod('Gun mount',(.90,0,.80),(.90,0,1.37),.045,'steel',body)
 bird=emu('Emu ahead',(-3.1,-.2,0),.67);bird[0].rotation_euler.z=-math.pi/2
 def state(i):
  u=i/(count-1);e=u*u*(3-2*u);root.location.x=.8-1.6*e
  body.location.z=.045*math.sin(u*math.tau*4)*math.sin(math.pi*u);body.rotation_euler.y=.025*math.sin(u*math.tau*3)*math.sin(math.pi*u)
  for w in wheels:w.rotation_euler.y=1.6*e/.45
  bird[0].location.x=-2.7-1.1*e;gait(bird,i/30,math.sin(math.pi*u)**.5 if 0<u<1 else 0)
 target=(-.3,0,.75);cam=(-10,-15,10);scale=15.5
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.45));finish(bpy.context.object,'earth')
for pos,power,size,col in [((-8,-7,13),2300,8,(1,.84,.63)),((7,-2,10),1800,7,(.66,.82,1)),((1,9,12),2200,6,(1,.76,.47))]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=col;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=cam);o=bpy.context.object;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;S.camera=o
out=P/'frames'/K;out.mkdir(exist_ok=True,parents=True)
if K=='truck' and '--probes' not in sys.argv:
 import shutil,subprocess
 probes=[0,15,30,45,60]
 for i in probes:
  targetfile=out/f'probe_{i:04d}.jpg';existing=out/f'{i:04d}.jpg'
  if existing.exists():shutil.copy2(existing,targetfile)
  else:
   state(i);S.render.filepath=str(targetfile);bpy.ops.render.render(write_still=True)
 result=subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'region_cache.py'),'bounds',str(out)],check=True,capture_output=True,text=True);region=json.loads(result.stdout)
 x0,y0,x1,y1=region['box_top_left_pixels'];w,h=region['source_size'];S.render.use_border=True;S.render.use_crop_to_border=True
 S.render.border_min_x=(x0+.1)/w;S.render.border_max_x=min(1,(x1+.1)/w);S.render.border_min_y=min(1,1-y1/h+.1/h);S.render.border_max_y=min(1,1-y0/h+.1/h)
 region['actual_box_top_left_pixels']=[int(S.render.border_min_x*w),h-int(S.render.border_max_y*h),int(S.render.border_max_x*w),h-int(S.render.border_min_y*h)]
 for i in range(count):
  if i in probes:continue
  state(i);S.render.filepath=str(out/f'patch_{i:04d}.jpg');bpy.ops.render.render(write_still=True)
 S.render.use_border=False;S.render.use_crop_to_border=False
 (out/'index.json').write_text(json.dumps({'count':count,'frames':count,'fps':30,'source_size':[720,1280],'region':region,'schematic':True,'camera':'fixed','motion':'native30fps region rendering, unchanged background reused'},indent=2))
 subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'region_cache.py'),'stitch',str(out)],check=True)
else:
 indices=[0,count//2,count-1] if '--probes' in sys.argv else range(count)
 for i in indices:
  state(i);S.render.filepath=str(out/f'{i:04d}.jpg')
  if '--reuse' in sys.argv and Path(S.render.filepath).exists():continue
  bpy.ops.render.render(write_still=True)
 (out/'index.json').write_text(json.dumps({'frames':count,'fps':30,'source_size':[720,1280],'schematic':True,'camera':'fixed','motion':'native30fps, eased endpoint, no optical interpolation'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'{K}.blend'),compress=True)
