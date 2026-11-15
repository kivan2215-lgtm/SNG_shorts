"""Authored educational 747/jet-core models. No claim of exact RB211 engineering geometry."""
import bpy,math,sys,json,random
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).parent;args=sys.argv[sys.argv.index('--')+1:];K=args[0];mode=args[1] if len(args)>1 else 'test'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True;S.cycles.max_bounces=4;S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.08;S.render.use_persistent_data=True
S.render.resolution_x=720;S.render.resolution_y=1280;S.render.resolution_percentage=100;S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=96
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.045,.065,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.4
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast'
def mat(name,col,metal=0,rough=.45,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 if emit:b.inputs['Emission Color'].default_value=(*col,1);b.inputs['Emission Strength'].default_value=emit
 return m
white=mat('Painted ivory',(.65,.68,.67),.15);blue=mat('Deep blue fuselage',(.025,.06,.115),.2);steel=mat('Machined titanium',(.25,.31,.34),.8,.3);dark=mat('Dark inner duct',(.025,.035,.04),.45);glass=mat('Cockpit glass',(.035,.09,.13),.55,.16);red=mat('Tail red',(.50,.025,.025));gold=mat('Hot metal',(.45,.20,.06),.65);ash=mat('Ash deposit',(.22,.16,.10),.1,.9);orange=mat('Combustion',(.9,.21,.025),0,.5,2);cyan=mat('Blue discharge',(.06,.35,.9),0,.5,2)
def finish(o,m):
 o.data.materials.append(m)
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def sphere(name,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;finish(o,m);return o
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);S.collection.objects.link(o);finish(o,m);be=o.modifiers.new('Soft edges','BEVEL');be.width=.035;be.segments=2;return o
def lathe(name,profile,m,loc=(0,0,0),cut=False):
 n=40 if cut else 64;a0=-math.pi/2 if cut else 0;span=math.pi if cut else math.tau
 vs=[(x,math.cos(a0+span*i/n)*r,math.sin(a0+span*i/n)*r) for x,r in profile for i in range(n+1)];fs=[]
 for j in range(len(profile)-1):
  for i in range(n):a=j*(n+1)+i;fs.append((a,a+1,a+n+2,a+n+1))
 o=mesh(name,vs,fs,m);o.location=loc;return o
def rod(name,a,b,r,m):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,m)
def camera(pos,target,scale):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;S.camera=o

def lights(scale=1):
 for pos,power,size,col in [((-7,-10,12),2600,8,(.78,.88,1)),((5,-3,7),1700,7,(1,.79,.57)),((3,8,10),3200,6,(.4,.68,1))]:
  bpy.ops.object.light_add(type='AREA',location=tuple(x*scale for x in pos));o=bpy.context.object;o.data.energy=power*scale**2;o.data.shape='DISK';o.data.size=size*scale;o.data.color=col;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
anchors={};root=None;deposits=[]
def aircraft():
 global root
 before=set(bpy.data.objects);lathe('747 fuselage',[(-7.7,.02),(-7.4,.3),(-6.6,.66),(-5.6,.82),(3.6,.82),(5,.64),(6.5,.33),(7.5,.02)],white)
 sphere('Blue lower fuselage',(-.1,0,-.22),(7.25,.80,.65),blue)
 sphere('747 upper deck',(-4.4,0,.56),(2.5,.67,.66),white)
 for side in [-1,1]:
  y=side
  mesh('Swept main wing',[(-1.8,0,0),(2.4,0,0),(5.3,y*8.3,.45),(4.3,y*8.4,.45),(-1.8,0,-.15),(2.4,0,-.15),(5.3,y*8.3,.31),(4.3,y*8.4,.31)],[(0,1,2,3),(4,7,6,5),(0,3,7,4),(1,5,6,2),(2,6,7,3)],white)
  mesh('Horizontal stabilizer',[(5,0,.3),(7,0,.35),(7.8,y*3,.6),(6.9,y*3,.6)],[(0,1,2,3)],steel)
  for j,x in enumerate([-.6,1.2]):
   yy=side*(3.0 if j==0 else 5.8);loc=(x,yy,-.9)
   lathe('Engine nacelle',[(-.95,.40),(-.8,.53),(.65,.47),(1.1,.30),(1.1,.25),(.6,.38),(-.75,.43),(-.95,.40)],white,loc)
   lathe('Intake rim',[(-.96,.4),(-.91,.43),(-.84,.45)],steel,loc)
   rod('Engine pylon',(x+.6,yy,-.5),(x+1.5,yy,.25),.14,steel)
   sphere('Spinner',(x-.69,yy,-.9),(.28,.16,.16),steel)
   for b in range(20):
    a=math.tau*b/20;rod('Fan blade',(x-.60,yy+math.cos(a)*.16,-.9+math.sin(a)*.16),(x-.48,yy+math.cos(a+.14)*.40,-.9+math.sin(a+.14)*.40),.028,dark)
   anchors['engine'+str((2-j) if side==-1 else (3+j))]=(x-.8,yy,-.9)
  for x in [i*.31-5.5 for i in range(35)]:sphere('Cabin window',(x,side*.807,.16),(.065,.014,.083),glass)
  for x in [-5.2,-4.9,-4.6,-4.3,-4.0,-3.7]:sphere('Upper deck window',(x,side*.57,.91),(.055,.018,.06),glass)
  mesh('Cockpit windshield',[(-6.5,side*.35,.68),(-5.9,side*.56,.76),(-5.6,side*.53,.98),(-6.15,side*.32,1.03)],[(0,1,2,3)],glass)
 mesh('Vertical stabilizer',[(4.8,0,.5),(6.6,0,3.1),(7.3,0,3.1),(7.2,0,.4)],[(0,1,2,3)],blue)
 mesh('Tail red flash',[(5.8,-.022,1.4),(6.65,-.022,2.9),(6.95,-.022,2.9),(6.45,-.022,1.4)],[(0,1,2,3)],red)
 root=bpy.data.objects.new('Aircraft assembly',None);S.collection.objects.link(root)
 for o in set(bpy.data.objects)-before:
  if o!=root:o.parent=root
 anchors['nose']=(-7.2,0,.2)

def engine():
 lathe('Cutaway outer nacelle',[(-4.7,1.36),(-4.3,1.57),(-2.8,1.5),(0,1.23),(2.8,1.1),(4.5,.72),(4.5,.62),(2.8,.96),(0,1.1),(-2.8,1.36),(-4.3,1.42),(-4.7,1.36)],white,cut=True)
 rod('Central shaft',(-4.1,0,0),(4.3,0,0),.17,steel)
 sphere('Intake cone',(-4.0,0,0),(.72,.45,.45),steel)
 for x,r,n in [(-3.3,1.25,24),(-2.3,.85,20),(-1.5,.7,20),(-.8,.6,20),(1.7,.65,22),(2.3,.74,22),(3.0,.68,22)]:
  lathe('Blade disk',[(x-.06,.2),(x-.06,r*.6),(x+.06,r*.6),(x+.06,.2)],steel)
  for i in range(n):
   a=math.tau*i/n
   # Exposed near-side blades and visible far-side structure.
   vs=[(x-.11,math.cos(a)*.22,math.sin(a)*.22),(x+.10,math.cos(a+.12)*.22,math.sin(a+.12)*.22),(x+.18,math.cos(a+.14)*r,math.sin(a+.14)*r),(x-.10,math.cos(a)*r,math.sin(a)*r)]
   mesh('Compressor / turbine blade',vs,[(0,1,2,3)],steel if x<0 else gold)
 lathe('Annular combustor cutaway',[(-.3,.79),(1.25,.75),(1.25,.43),(-.3,.43)],gold,cut=True)
 for i in range(5):sphere('Combustion glow',(-.1+i*.24,.05,.02),(.20,.34,.34),orange)
 for i in range(22):
  a=math.tau*i/22;o=sphere('Deposited ash',(1.62,math.cos(a)*.59,math.sin(a)*.59),(.13,.12,.12),ash);deposits.append(o)
 anchors.update(intake=(-4.2,0,1.2),compressor=(-1.7,0,.8),hot=(.45,0,.8),turbine=(1.7,0,.8),exhaust=(4,0,.6))

def box(name,loc,scale,m,bevel=.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,m)
 be=o.modifiers.new('Rounded edge','BEVEL');be.width=bevel;be.segments=3;return o

def cabin():
 cloth=mat('Blue seat cloth',(.045,.095,.15),0,.87);cream=mat('Cabin ivory',(.5,.47,.38),0,.75)
 box('Cabin floor',(0,0,-.15),(7,10,.25),dark)
 for side in [-1,1]:
  box('Cabin wall',(side*3.5,0,1.5),(.15,10,3.3),cream)
  for y in [-3.5,-1.6,.3,2.2,4.1]:
   box('Window rim',(side*3.4,y,2.1),(.12,.8,.85),steel)
   box('Night window',(side*3.32,y,2.1),(.08,.67,.69),glass)
   box('Vent',(side*3.3,y,.35),(.10,.65,.16),steel)
  for y in [-3,-1,1,3]:
   for x in [side*1.65,side*2.65]:
    box('Seat cushion',(x,y,.55),(.78,.8,.19),cloth)
    b=box('Seat back',(x,y+.35,1.1),(.78,.18,1.05),cloth);b.rotation_euler.x=-.08
    for dx in [-.41,.41]:box('Arm rest',(x+dx,y,.82),(.09,.72,.09),steel)
    rod('Seat support',(x,y,0),(x,y,.55),.06,steel)
 sys.path.insert(0,str(P))
 from human_model import create as person
 M={'skin':mat('Skin',(.43,.26,.17),0,.68),'cloth':mat('Civilian shirt',(.27,.22,.17),0,.9),'trousers':mat('Trousers',(.055,.065,.08),0,.9),'boot':mat('Shoes',(.025,.023,.02),0,.7),'hair':mat('Hair',(.045,.025,.014),0,.9),'eyewhite':white,'iris':dark}
 def empty(n,l,parent=None):
  o=bpy.data.objects.new(n,None);S.collection.objects.link(o);o.location=l;o.parent=parent;return o
 def uv(n,l,sc,m,parent=None):
  o=sphere(n,l,sc,M[m]);o.parent=parent;return o
 for i,(x,y) in enumerate([(-1.65,-3),(-2.65,-1),(-1.65,1),(1.65,1)]):
  root=person('Generic passenger '+str(i),(x,y+.10,-.4),M,empty,uv,None,None,pose='seated')
 anchors['vent']=(-3.25,-1.6,.35)
 camera((8,-13,9),(0,0,1),24);lights(.8)

def cockpit():
 panel=mat('Instrument panel',(.035,.045,.05),.2,.65)
 box('Instrument deck',(0,0,0),(7,2,.7),panel)
 for x in [-2.5,-1.7,-.9,0,.9,1.7,2.5]:
  sphere('Analog instrument',(x,-1.03,.18),(.30,.04,.30),dark)
  for a in [i*math.tau/12 for i in range(12)]:rod('Gauge tick',(x+math.cos(a)*.22,-1.08,.18+math.sin(a)*.22),(x+math.cos(a)*.26,-1.08,.18+math.sin(a)*.26),.012,white)
  rod('Needle',(x,-1.09,.18),(x+.16,-1.09,.3),.014,white)
 scratched=mat('Abraded windshield',(.31,.37,.38),.05,.97)
 for x in [-2.4,0,2.4]:
  box('Windshield frame',(x,.75,2),(2.45,.18,2.5),panel)
  box('Opaque abraded glass',(x,.62,2),(2.18,.06,2.2),scratched,.02)
  random.seed(33+int(x*10))
  for j in range(45):
   xx=x+random.uniform(-1,1);zz=random.uniform(1,3);rod('Abrasion scratch',(xx,.57,zz),(xx+random.uniform(.05,.3),.57,zz+.08),.006,steel)
 # A small lower clear strip represents the captain's restricted view, not an exact windshield map.
 box('Small clear strip',(-2.4,.53,.95),(1.8,.04,.17),glass,.01)
 for x in [-3,-2,2,3]:rod('Window pillar',(x,.45,.6),(x,.45,3.4),.075,steel)
 camera((5,-11,5),(0,0,1.4),14);lights(.65);anchors['glass']=(0,.5,2)

def radar():
 panel=mat('Radar panel',(.045,.055,.06),.35,.5);screen=mat('Phosphor screen',(.005,.035,.018),.1,.25,.15);green=mat('Phosphor grid',(.08,.4,.19),0,.6,.6)
 box('Radar housing',(0,.2,0),(6,1.3,6),panel,.3)
 sphere('CRT glass',(0,-.5,0),(2.5,.13,2.5),screen)
 for radius in [.65,1.3,1.95,2.4]:
  for i in range(72):
   a=i*math.tau/72;b=(i+1)*math.tau/72;rod('Range ring',(math.cos(a)*radius,-.67,math.sin(a)*radius),(math.cos(b)*radius,-.67,math.sin(b)*radius),.009,green)
 for a in [0,math.pi/4,math.pi/2,math.pi*3/4]:rod('Radial grid',(-math.cos(a)*2.4,-.67,-math.sin(a)*2.4),(math.cos(a)*2.4,-.67,math.sin(a)*2.4),.009,green)
 for x in [-2,0,2]:sphere('Control knob',(x,-.56,-2.7),(.12,.1,.12),steel)
 anchors['center']=(0,-.70,0)
 for i in range(72):anchors['ring'+str(i)]=(math.cos(i*math.tau/72)*2.35,-.70,math.sin(i*math.tau/72)*2.35)
 camera((3,-12,5),(0,0,0),13.5);lights(.7)

if K in ['flight','glide','landing','glow']:
 aircraft();camera((-13,-22,14),(0,0,0),36);lights(1.4)
 if K=='glide':camera((-6,-25,10),(0,0,0),36)
 if K=='landing':
  camera((-19,-20,9),(0,0,0),36)
  for x,y in [(-5,0),(1,-1),(1,1)]:
   rod('Landing strut',(x,y,-.6),(x,y,-2.15),.09,steel)
   sphere('Landing wheel',(x,y,-2.2),(.3,.16,.3),dark)
  box('Runway',(0,0,-2.55),(60,9,.15),dark)
  for x in range(-25,26,4):box('Centerline',(x,0,-2.46),(1.5,.13,.02),white,.01)
  for x in range(-25,26,3):
   for y in [-4.3,4.3]:sphere('Runway edge light',(x,y,-2.4),(.07,.07,.04),cyan)
 if K=='glow':
  camera((-13,-18,8),(-4.5,0,.2),15)
  for a,b in [((-6.7,-.4,.7),(-6.0,-.65,1.1)),((-5.9,-.65,1),(-5.4,-.6,.6))]:rod('Static discharge stylization',a,b,.018,cyan)
elif K=='radar':radar()
elif K=='cabin':cabin()
elif K=='cockpit':cockpit()
else:
 engine();camera((-8,-18,10),(0,0,0),21);lights(.9)

# Recessed neutral background, not a geographic surface.
bg=mat('Backdrop',(.018,.035,.048),0,.95);bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-4));finish(bpy.context.object,bg)
def state(p):
 if root:
  root.location.z=(-1.5*p*p*(3-2*p) if K=='glide' else 0)
 q=max(0,min(1,p));q=q*q*(3-2*q)
 amount=1 if K=='blocked' else q if K=='deposit' else 1-q if K=='clear' else 0
 for o in deposits:o.scale=tuple(max(.001,v*amount) for v in (.17,.18,.18))
 for o in bpy.data.objects:
  if o.name.startswith('Combustion glow'):o.hide_render=K=='blocked' or (K=='deposit' and p>.8) or K=='clear'
def proj():
 out={}
 for k,v in anchors.items():
  point=Vector(v)+(root.location if root else Vector((0,0,0)));c=world_to_camera_view(S,S.camera,point);out[k]=[c.x*1080,(1-c.y)*1920]
 return out
out=P/'frames'/K;out.mkdir(exist_ok=True)
count=61 if K in ['glide','deposit','clear'] and mode=='render' else 1
import subprocess,shutil
records=[]
if count==1:
 state(0);S.render.filepath=str(out/'0000.jpg');bpy.ops.render.render(write_still=True);records=[proj()]
 meta={'count':1,'anchors':records,'native_fps':30,'source_resolution':[720,1280],'processed':True}
else:
 for f in out.glob('[0-9][0-9][0-9][0-9].jpg'):
  # Reuse full frames from this same model branch before region caching was enabled.
  shutil.move(str(f),str(out/('probe_'+f.name)))
 probes=sorted(set([0,22,44,60]+[int(f.stem.split('_')[1]) for f in out.glob('probe_*.jpg')]))
 for i in probes:
  state(i/(count-1));S.render.filepath=str(out/f'probe_{i:04d}.jpg')
  if not Path(S.render.filepath).exists():bpy.ops.render.render(write_still=True)
 r=subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'region_cache.py'),'bounds',str(out)],check=True,capture_output=True,text=True);region=json.loads(r.stdout);print('REGION',region,flush=True)
 x0,y0,x1,y1=region['box_top_left_pixels'];w,h=region['source_size'];S.render.use_border=True;S.render.use_crop_to_border=True
 S.render.border_min_x=(x0+.1)/w;S.render.border_max_x=min(1,(x1+.1)/w);S.render.border_min_y=min(1,1-y1/h+.1/h);S.render.border_max_y=min(1,1-y0/h+.1/h)
 region['actual_box_top_left_pixels']=[int(S.render.border_min_x*w),h-int(S.render.border_max_y*h),int(S.render.border_max_x*w),h-int(S.render.border_min_y*h)]
 for i in range(count):
  state(i/(count-1));records.append(proj())
  if i not in probes:
   S.render.filepath=str(out/f'patch_{i:04d}.jpg');bpy.ops.render.render(write_still=True)
 meta={'count':count,'anchors':records,'native_fps':30,'source_resolution':[720,1280],'region':region}
 S.render.use_border=False;S.render.use_crop_to_border=False
(out/'index.json').write_text(json.dumps(meta))
if count>1:subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'region_cache.py'),'stitch',str(out)],check=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'{K}.blend'),compress=True)
