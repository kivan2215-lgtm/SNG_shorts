"""Authored 3-D explanatory models for Squalus V3. Blender 4.3 Eevee.
Geometry is educational, not a dimensionally exact historical engineering model.
Camera motion, component transforms and fill levels are driven by narration beats.
"""
import bpy, math, sys, json, random, time, os, shutil
from mathutils import Vector, Quaternion
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).parent
sys.path.insert(0,str(P))
from human_model import create as human_create, pose_person, operate_control, handle_line
from render_style import configure
for _d in ["tests","models","frames"]:(P/_d).mkdir(exist_ok=True)
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
K=ARGS[0] if ARGS else 'dock';MODE=ARGS[1] if len(ARGS)>1 else 'test'
random.seed(32)
S=bpy.context.scene
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S.render.engine='BLENDER_WORKBENCH';S.render.resolution_x=720;S.render.resolution_y=1280;S.render.resolution_percentage=100
S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=93
S.display.render_aa='FXAA';sh=S.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.6;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.35;sh.curvature_valley_factor=1.15;sh.show_specular_highlight=True;sh.background_type='WORLD';S.world.color=(.008,.023,.038)
S.view_settings.view_transform='Standard';S.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [x.identifier for x in S.view_settings.bl_rna.properties['look'].enum_items] else 'None'
M={}
def mat(n,col):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);M[n]=m;return m
for n,c in {'shell':(.10,.25,.31),'edge':(.41,.59,.62),'dark':(.025,.065,.09),'floor':(.23,.33,.32),'brass':(.85,.52,.17),'gold':(1,.72,.24),'water':(.015,.49,.68),'foam':(.2,.85,.94),'rubber':(.035,.12,.12),'safe':(.22,.86,.55),'danger':(.9,.24,.13),'cloth':(.18,.35,.44),'canvas':(.6,.5,.31),'skin':(.73,.56,.40),'boot':(.06,.08,.09),'light':(1,.87,.47),'sand':(.07,.16,.19),'rock':(.1,.23,.27),'red':(.65,.17,.13)}.items():mat(n,c)

for _n,_c in {'trousers':(.025,.045,.06),'hair':(.035,.025,.015),'eyewhite':(.6,.58,.52),'iris':(.04,.025,.015),'seam':(.08,.12,.13)}.items():mat(_n,_c)

for _n in ['skin','cloth','canvas','boot','sand']:
 M[_n].specular_intensity=.12

def material(o,m):o.data.materials.append(M[m]);return o

def empty(n,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.location=loc;o.parent=parent;return o

def cube(n,loc,dim,m='shell',bevel=0,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('machined edges','BEVEL');mod.width=bevel;mod.segments=2
  o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
 material(o,m);o.parent=parent;return o

def uv(n,loc,scale,m='shell',parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;material(o,m)
 for p in o.data.polygons:p.use_smooth=True
 o.parent=parent;return o

def cyl(n,loc,r,depth,m='edge',axis=(0,0,1),parent=None,vertices=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();material(o,m)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 bevel=o.modifiers.new('machined edge','BEVEL');bevel.width=min(.008,r*.07,depth*.12);bevel.segments=2
 o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
 o.parent=parent;return o

def bar(n,a,b,r=.04,m='edge',parent=None):
 a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m,b-a,parent,16);o['rest_length']=(b-a).length;return o

def curve(n,pts,r=.04,m='brass',parent=None):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for a,b in zip(sp.points,pts):a.co=(*b,1)
 c.bevel_depth=r;c.bevel_resolution=2;c.resolution_u=1;o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);material(o,m);o.parent=parent;return o

def torus(n,loc,major,minor=.045,m='edge',axis=(0,0,1),parent=None):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=loc,major_radius=major,minor_radius=minor);o=bpy.context.object;o.name=n;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();material(o,m)
 for p in o.data.polygons:p.use_smooth=True
 o.parent=parent;return o

def mesh(n,verts,faces,m,parent=None):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);material(o,m);o.parent=parent;return o

def annulus(n,z,ro,ri,m='floor',parent=None,depth=.09):
 verts=[];N=96
 for zz,rr in [(z,ro),(z,ri),(z-depth,ro),(z-depth,ri)]:
  verts += [(rr*math.cos(2*math.pi*i/N),rr*math.sin(2*math.pi*i/N),zz) for i in range(N)]
 faces=[]
 for i in range(N):
  j=(i+1)%N
  faces += [(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)]
 return mesh(n,verts,faces,m,parent)

def wheel(n,loc,r=.24,axis=(0,-1,0),parent=None):
 root=empty(n,loc,parent);q=Vector(axis).to_track_quat('Z','Y');root.rotation_mode='QUATERNION';root.rotation_quaternion=q;root['rest_rotation']=list(q);torus(n+' rim',(0,0,0),r,.035,'brass',parent=root)
 for a in [0,math.pi/3,2*math.pi/3]:bar(n+' spoke',(-r*math.cos(a),-r*math.sin(a),0),(r*math.cos(a),r*math.sin(a),0),.019,'brass',root)
 cyl(n+' hub',(0,0,0),.07,.08,'brass',parent=root);return root

def spin_wheel(root,angle):
 rest=Quaternion(root['rest_rotation']);root.rotation_quaternion=rest @ Quaternion((0,0,1),angle)
 assert (rest @ Vector((0,0,1))).dot(root.rotation_quaternion @ Vector((0,0,1)))>.99999, 'wheel axis changed'

def ladder(z1,z2,x=0,y=.25,parent=None,width=.7):
 for xx in [x-width/2,x+width/2]:bar('ladder rail',(xx,y,z1),(xx,y,z2),.035,'edge',parent)
 z=z1+.13
 while z<z2:bar('ladder rung',(x-width/2,y,z),(x+width/2,y,z),.025,'edge',parent);z+=.26

def person(n,loc=(0,0,0),diver=False,parent=None,pose='stand'):
 return human_create(n,loc,M,empty,uv,cyl,curve,parent,diver,pose)

def climb_motion(root,p):pose_person(root,p,climb=True)

def terrain(size=28,z=-2.2):
 size=max(size,120);n=70;vs=[]
 for iy in range(n):
  for ix in range(n):
   x=(ix/(n-1)-.5)*size;y=(iy/(n-1)-.5)*size
   height=.10*math.sin(x*.9)*math.cos(y*1.3)+.045*math.sin(x*3+y*2);vs.append((x,y,z+height))
 fs=[(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i) for j in range(n-1) for i in range(n-1)]
 o=mesh('seabed relief',vs,fs,'sand');o.modifiers.new('smooth seabed','WEIGHTED_NORMAL')
 for i in range(28):
  x=random.uniform(-size*.42,size*.42);y=random.uniform(-size*.4,size*.4);r=random.uniform(.10,.37);uv('seabed rock',(x,y,z+r*.3),(r,r*.75,r*.42),'rock')
 # Long contour strands create a readable depth field without oscillating the camera.
 for y in [-8,-5,5,8]:curve('seabed contour',[(x,y,z+.08+.08*math.sin(x)) for x in range(-12,13)],.012,'rock')

def hull_shell(parent=None,cut=False):
 profile=[(-9,.14),(-8.7,.65),(-8,1.15),(-6,1.5),(5.8,1.5),(7.1,1.25),(8.4,.6),(9,.12)]
 angles=[(math.pi*i/32 if cut else 2*math.pi*i/64) for i in range(33 if cut else 65)]
 # y=sin(angle) keeps positive-y back half; z=cos(angle).
 vs=[(x,r*math.sin(a),r*math.cos(a)) for x,r in profile for a in angles];N=len(angles);fs=[]
 for j in range(len(profile)-1):
  for i in range(N-1):fs.append((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i))
 o=mesh('pressure hull cutaway' if cut else 'pressure hull',vs,fs,'shell',parent)
 for p in o.data.polygons:p.use_smooth=True
 mod=o.modifiers.new('steel thickness','SOLIDIFY');mod.thickness=.12
 for x in [-6,-4,-2,0,2,4,6]:curve('hull rib',[(x,1.51*math.sin(a),1.51*math.cos(a)) for a in angles],.035,'edge',parent)
 return o

def submarine(cut=False,loc=(0,0,0),scale=1):
 root=empty('USS Squalus explanatory model',loc);root.scale=(scale,)*3
 shell=hull_shell(root,cut)
 cube('upper deck',(0,0,1.25),(13.7,1.45,.36),'shell',.12,root)
 if cut:
  # deck only back half exposes the interior but keeps position of hatch.
  shell_deck=bpy.data.objects['upper deck'];shell_deck.scale.y=.55;shell_deck.location.y=.32
 cube('conning tower',(-1.0,.25,2.12),(2,1.12,1.55),'shell',.3,root)
 for x in [-1.4,-.7]:bar('periscope',(x,.25,2.7),(x,.25,4.1),.07,'edge',root);bar('scope head',(x,.25,4.1),(x-.18,.25,4.1),.07,'edge',root)
 for y in [-.69,.69]:
  for x in [-6,-4,-2,0,2,4,6]:bar('deck stanchion',(x,y,1.42),(x,y,1.89),.025,'edge',root)
  bar('deck rail',(-6,y,1.89),(6,y,1.89),.025,'edge',root)
 cyl('deck gun pedestal',(-3.6,0,1.63),.19,.45,'shell',parent=root);bar('period deck gun barrel',(-3.2,0,1.95),(-4.8,0,2.03),.095,'edge',root)
 torus('forward hatch rim',(-5.2,0,1.56),.43,.07,'brass',parent=root);cyl('forward hatch',(-5.2,0,1.56),.38,.1,'brass',parent=root)
 for x in [i*.48-6.4 for i in range(28)]:cube('free flooding slot',(x,-1.35,.65),(.22,.04,.10),'dark',.02,root)
 bar('propeller shaft',(8.5,0,0),(9.5,0,0),.11,'edge',root)
 for a in [0,math.pi/2,math.pi,math.pi*1.5]:
  o=uv('propeller blade',(9.45,.40*math.cos(a),.40*math.sin(a)),(.08,.24,.58),'brass',root);o.rotation_euler[0]=a
 cube('stern rudder',(8.6,0,.5),(.7,.12,1.1),'shell',.06,root)
 if cut:
  cube('compartment deck',(0,0,-.65),(13,2.3,.12),'floor',.03,root)
  # Bulkhead divides fore survivors and aft flooded machinery spaces.
  cube('watertight bulkhead',(0,.57,.3),(.16,1.25,2.2),'edge',.04,root)
  for x in [.85,2.5,4.15]:
   cube('diesel engine',(x,.4,-.1),(1.2,.9,.9),'floor',.07,root)
   for xx in [x-.4,x-.15,x+.1,x+.35]:cyl('engine cylinder',(xx,.4,.51),.12,.35,'edge',parent=root)
   curve('engine pipe',[(x-.4,.7,.65),(x-.4,.7,1.05),(x+.45,.7,1.05)],.04,'brass',root)
  for x in [-5.8,-4.7,-3.6,-2.5]:person('survivor',(x,.28,-.58),parent=root)
  for x in [-6,-3]:cube('bunk',(x,1.0,.1),(1.7,.45,.13),'canvas',.04,root)
 return root

def water_volume(parent=None):
 # Profile rebuilt to keep the changing water level inside the cylindrical hull.
 n=24;verts=[(0,0,0)]*(2*(n+2));faces=[]
 faces.append(tuple(range(n+2)));faces.append(tuple(range(n+2,2*(n+2))))
 for i in range(n+2):j=(i+1)%(n+2);faces.append((i,j,n+2+j,n+2+i))
 o=mesh('rising seawater',verts,faces,'water',parent)
 def update(level):
  top=-1.28+2.56*max(.005,min(1,level));zlist=[-1.28+(.0+top+1.28)*i/n for i in range(n+1)]
  pts=[(-math.sqrt(max(.01,1.37**2-z*z)),z) for z in zlist]+[(math.sqrt(max(.01,1.37**2-top*top)),top)]
  # visible front cut plane + horizontal surface, entirely inside pressure radius
  ang=math.acos(max(-1,min(1,top/1.37)))
  pts=[(1.37*math.sin(ang+(2*math.pi-2*ang)*i/(n+1)),1.37*math.cos(ang+(2*math.pi-2*ang)*i/(n+1))) for i in range(n+2)]
  for j,x in enumerate([.2,6.3]):
   for i,(y,z) in enumerate(pts):o.data.vertices[j*len(pts)+i].co=(x,y,z)
  o.data.update()
 update(.01);return o,update

def hull_room():
 # Large lower hull cutaway beneath the escape hatch.
 cube('submarine back wall',(0,1.25,-1.15),(7.0,.25,2.4),'shell',.15)
 for x in [-3.45,3.45]:cube('cutaway side wall',(x,.1,-1.15),(.18,2.3,2.4),'shell',.08)
 cube('interior floor',(0,-.15,-2.05),(6.8,2,.14),'floor',.03)
 for x in [-3,-1.8,1.8,3]:curve('interior rib',[(x,-.9,-2.05),(x,.65,-2.05),(x,.8,-.1)],.075,'edge')
 # Ring-shaped roof section leaves a real hole at center.
 for x in [-2,2]:cube('deck side',(x,0,.04),(2.3,2.4,.22),'shell',.06)
 for y in [-.9,.9]:cube('hatch deck',(0,y,.04),(1.7,.6,.22),'shell',.04)
 annulus('flat mating plate',.20,1.28,.65,'edge',depth=.18)
 for a in range(0,360,30):cyl('mating plate bolt',(1.13*math.cos(math.radians(a)),1.13*math.sin(math.radians(a)),.24),.04,.065,'brass')
 for x in [-2.7,2.7]:person('waiting crew',(x,-.55,-2.05),pose='stand')
 curve('red cabin pipe',[(-3,.3,-.2),(-2,.3,-.2),(-2,.3,-1.4)],.045,'red')
 ladder(-2,.15,0,.28,width=.75)
 pivot=empty('sub hatch hinge',(-.64,0,.22));cyl('sub hatch lid',(.64,0,0),.65,.12,'brass',parent=pivot)
 wheel('sub hatch wheel',(.64,0,.10),.22,(0,0,1),pivot)
 return pivot

def chamber(loc=(0,0,.26),s=1):
 root=empty('McCann chamber',loc);root.scale=(s,)*3
 profile=[(0,1.27),(.18,1.30),(1.2,1.34),(2.5,1.73),(4.30,1.79),(4.80,1.62),(5.16,1.16),(5.35,.35)]
 # Smooth the lathed shell profile while preserving its authored dimensions.
 refined=[]
 for j in range(len(profile)-1):
  a=Vector(profile[max(0,j-1)]);b=Vector(profile[j]);c=Vector(profile[j+1]);d=Vector(profile[min(len(profile)-1,j+2)])
  for ii in range(6):
   t=ii/6;v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);refined.append(tuple(v))
 profile=refined+[profile[-1]]
 angles=[math.pi*i/64 for i in range(65)];N=len(angles);vs=[]
 for z,r in profile:vs.extend([(r*math.cos(a),r*math.sin(a),z) for a in angles])
 fs=[]
 for j in range(len(profile)-1):
  for i in range(N-1):fs.append((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i))
 shell=mesh('bell steel cutaway',vs,fs,'shell',root)
 for p in shell.data.polygons:p.use_smooth=True
 sol=shell.modifiers.new('visible steel shell thickness','SOLIDIFY');sol.thickness=.14
 # Front cut edges emphasize volumetric steel, not a line drawing.
 for side in [-1,1]:curve('exposed section edge',[(side*r,0,z) for z,r in profile],.07,'edge',root)
 for z,r in [(.18,1.32),(2.5,1.75),(4.3,1.81)]:
  curve('reinforcing ring',[(r*math.cos(a),r*math.sin(a),z) for a in angles],.05,'edge',root)
  for a in angles[::4]:uv('shell rivet',(r*math.cos(a),r*math.sin(a)-.015,z),(.048,.048,.048),'brass',root)
 annulus('upper chamber floor',2.5,1.72,.62,'floor',root,.15)
 torus('rubber mating seal',(0,0,.02),1.27,.095,'rubber',parent=root)
 torus('flange steel',(0,0,.15),1.30,.06,'edge',parent=root)
 # Practical interior: seat, communication, air cylinders, gauge, piping, valves.
 cube('operator bench',(-1.02,1.15,2.83),(.75,.58,.13),'canvas',.04,root)
 for z in [3.03,3.9]:curve('air pipe',[(-1.4,.6,z),(-1.4,1.1,z),(.5,1.1,z)],.04,'brass',root)
 for x in [.92,1.25]:cyl('air cylinder',(x,.65,3.1),.13,.9,'edge',parent=root)
 cyl('pressure gauge',(.85,.2,4.0),.19,.08,'brass',(0,-1,0),root)
 cyl('gauge face',(.85,.15,4.0),.16,.02,'light',(0,-1,0),root)
 bar('gauge needle',(.85,.12,4),(.96,.12,4.09),.012,'dark',root)
 wheel('air control',(1.27,.25,3.65),.21,(0,-1,0),root)
 cube('lamp',(-.5,.8,4.65),(.5,.2,.12),'light',.04,root)
 wheel('haul down reel',(-.97,.45,1.35),.33,(0,-1,0),root)
 cyl('reel drum',(-.97,.65,1.35),.26,.35,'edge',(0,1,0),root)
 ladder(.15,2.40,0,.33,root,.75)
 for x in [-.375,.375]:curve('upper ladder handhold',[(x,.70,2.5),(x,.70,3.60),(x,.90,3.68),(x,1.05,3.60),(x,1.05,2.5)],.027,'edge',root)
 person('bell operator',(-.85,.45,2.50),parent=root)
 # Second operator indicated with a distinct position, not cloned onto the same seat.
 person('second operator',(.80,.65,2.50),parent=root)
 pivot=empty('upper hatch hinge',(-.64,0,2.58),root);cyl('upper hatch lid',(.64,0,0),.65,.11,'brass',parent=pivot)
 wheel('upper hatch wheel',(.64,0,.10),.20,(0,0,1),pivot)
 torus('lifting eye',(0,0,5.50),.20,.06,'edge',(0,-1,0),root)
 # Lower water column; it is controlled independently of the upper passenger compartment.
 water=cyl('water lower chamber',(0,.08,1.25),1.13,2.25,'water',parent=root,vertices=40)
 return root,pivot,water

def ship(loc=(0,0,0),s=1):
 root=empty('surface rescue vessel',loc);root.scale=(s,)*3
 uv('rescue ship hull',(0,0,0),(3,.8,.48),'shell',root);cube('ship deck',(0,0,.3),(5.1,1.3,.2),'floor',.1,root)
 cube('ship bridge',(.0,.1,.85),(1.6,.9,.85),'edge',.08,root);cyl('funnel',(1.2,.1,1.2),.24,1.0,'shell',parent=root)
 for x in [-.5,0,.5]:cube('bridge window',(x,-.38,1.0),(.28,.035,.23),'dark',.025,root)
 for x in [-2,2]:bar('mast',(x,0,.4),(x,0,2.6),.045,'edge',root)
 bar('working crane',(-2,0,2.2),(-3.8,-.1,1.2),.07,'brass',root)
 return root

bpy.ops.object.camera_add(location=(8,-18,10));CAM=bpy.context.object;S.camera=CAM;CAM.data.type='ORTHO';CAM.data.lens=50

def camera(loc,target,scale):
 CAM.location=loc;CAM.rotation_euler=(Vector(target)-CAM.location).to_track_quat('-Z','Y').to_euler();CAM.data.ortho_scale=scale

def e(p):p=min(1,max(0,p));return p*p*p*(p*(p*6-15)+10)
def sm(p,a=0,b=1):return e((p-a)/(b-a))
def lerp(a,b,p):return a+(b-a)*p

state={};anchors={};objects=[]
BELL_KINDS=['cable','dock','seal','drain','dry','open','transfer','question']
SUB_KINDS=['hero','dive','flood','loss','depth','rise','trips','saved','final']
if K in BELL_KINDS:
 sublid=hull_room();terrain(25,-2.25)
 if K not in ['question','cable']:
  bell,upper,wet=chamber();rope=curve('lifting wire',[(0,0,5.8),(0,0,12)],.025,'edge');hose=curve('air and telephone umbilical',[(1.0,.9,4.6),(1.9,1.0,6.4),(2.0,1.3,12)],.045,'brass')
  marker=torus('seal highlight',(0,0,.29),1.32,.045,'safe');marker.hide_render=K=='dock'
 else:bell=upper=wet=None
 if K=='question':
  for x in [-1.5,0,1.5]:
   bar('water pressure arrow',(x,-.15,3.6),(x,-.15,1.1),.028,'water')
   bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=.13,radius2=0,depth=.35,location=(x,-.15,.93));o=bpy.context.object;o.rotation_euler[0]=math.pi;material(o,'foam')
 if K=='cable':
  diver=person('hard hat diver',(.60,0,.28),True,pose='attach');diver.rotation_euler[2]=-math.pi/2
  cable=curve('guide cable',[(0,0,.3),(0,0,7)],.025,'gold');hose=curve('diver hose',[(.60,0,1.95),(1.8,.8,3),(2.2,1.1,7)],.05,'brass')
 if K=='transfer':
  passenger=person('climbing survivor',(.05,.04,-1.8),pose='climb');passenger.rotation_euler[2]=math.pi
 anchors={'hatch':(0,-.5,.2),'seal':(-1.1,-.35,.3),'lower':(.95,-.4,1.2),'upper':(0,0,3.5),'path':(-.1,-.3,1.5),'cable':(0,0,4)}
 camera((8,-20,9),(0,0,1.8),11.4)
 if K=='question':camera((8,-18,9),(0,0,.1),9.2)
 if K=='cable':camera((8,-19,10),(0,0,1.2),10.8)

elif K in SUB_KINDS:
 overview=K in ['depth','rise','trips','saved','final']
 cut=K in ['flood','loss'];sub=submarine(cut,scale=.48 if overview else 1)
 terrain(30,-1.2 if overview else -1.7)
 if cut:water,update_water=water_volume(sub)
 if overview:
  surf=ship((.2,0,10.8),.72);bell,upper,wet=chamber((-2.5,0,2),.28)
  rope=curve('rescue cable',[(-2.5,0,1),(-2.5,0,12)],.025,'gold')
  if K!='depth':person('rescued passenger',(0,-.12,2.55),parent=bell)
  # The surface is a shaped water slab, not a plain line.
  cube('surface slice',(0,2,10.65),(16,6,.12),'water',.05)
  anchors={'surface':(4,0,10.7),'bottom':(4,0,-.2),'sub':(-2.5,0,.8),'bell':(-2.5,0,5),'count':(2.2,0,5)}
  camera((7,-24,14),(0,0,4.2),20)
 else:
  anchors={'hatch':(-5.2,0,1.6),'aft':(3,-1,.2),'fore':(-4,-1,.2),'valve':(2,.4,1.7)}
  camera((15,-28,16),(0,0,.5),27)
  if K in ['hero','dive']:camera((17,-25,15),(0,0,0),28)
  if K in ['flood','loss']:camera((17,-27,18),(0,0,0),32)

elif K=='valve':
 terrain(20,-3)
 # A thick section of induction pipe with an open butterfly plate and visible bolts.
 for z in [0,3.2]:annulus('pipe flange',z,1.55,1.07,'edge',depth=.18)
 # cylindrical back half section
 vs=[(1.25*math.cos(a),1.25*math.sin(a),z) for z in [0,3.2] for a in [math.pi*i/40 for i in range(41)]];fs=[(i,i+1,42+i,41+i) for i in range(40)];o=mesh('open air intake section',vs,fs,'shell');o.modifiers.new('pipe wall thickness','SOLIDIFY').thickness=.16
 plate=cyl('failed butterfly valve',(0,0,2),1.08,.13,'brass');plate.rotation_euler[1]=1.02
 bar('valve spindle',(-1.6,0,2),(1.6,0,2),.09,'edge');wheel('actuator wheel',(1.6,0,2),.45,(1,0,0))
 for z in [.04,3.25]:
  for a in range(0,360,30):cyl('flange bolts',(1.36*math.cos(math.radians(a)),1.36*math.sin(math.radians(a)),z),.08,.20,'brass')
 # Continuous water stream curves around the open plate, never through it.
 path=[(-.35,-.28,3.8),(-.5,-.28,3.25),(-.91,-.28,2.8),(-.97,-.28,2.2),(-.85,-.28,1.6),(-.45,-.28,1.0),(-.35,-.28,.2)]
 centers=[]
 for i in range(81):
  u=i/80*(len(path)-1);j=min(len(path)-2,int(u));t=u-j
  a=Vector(path[max(0,j-1)]);b=Vector(path[j]);c=Vector(path[j+1]);dd=Vector(path[min(len(path)-1,j+2)])
  centers.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-dd)*t*t+(-a+3*b-3*c+dd)*t*t*t))
 vv=[tuple(c) for c in centers for a in range(20)];ff=[]
 for i in range(80):
  for j in range(20):ff.append((i*20+j,i*20+(j+1)%20,(i+1)*20+(j+1)%20,(i+1)*20+j))
 stream=mesh('continuous seawater past open valve',vv,ff,'water')
 for face in stream.data.polygons:face.use_smooth=True
 def stream_update(p):
  for i,c in enumerate(centers):
   radius=.12+.013*math.sin(i*.65-p*math.pi*8)+.007*math.sin(i*1.1+p*math.pi*4)
   for j in range(20):
    a=j*2*math.pi/20;stream.data.vertices[i*20+j].co=c+Vector((radius*math.cos(a),radius*math.sin(a),0))
  stream.data.update()
 stream_update(0)
 anchors={'valve':(.15,-.15,1.65),'flow':(-.35,-.3,.8)};camera((8,-18,9),(0,0,1.4),9.8)

elif K=='sealed':
 terrain(20,-.35)
 cube('compartment floor',(0,.3,0),(8,4,.2),'floor',.1)
 cube('rear pressure wall',(0,2,1.8),(8,.18,3.6),'shell',.2)
 for x in [-3.6,-2.4,-1.2,1.2,2.4,3.6]:curve('hull frame',[(x,-1.8,0),(x,1.8,0),(x,1.9,3.4),(x,-.3,3.4)],.075,'edge')
 # Door in a bulkhead aligned transverse to the hull.
 cube('bulkhead back',(0,1.5,1.75),(.17,1.0,3.5),'edge',.03)
 cube('bulkhead top',(0,-.3,3.0),(.17,2.7,.65),'edge',.03)
 cube('bulkhead foot',(0,-.3,.25),(.17,2.7,.5),'edge',.03)
 door=empty('watertight door hinge',(0,.9,.5));cube('watertight door',(0,-.85,1.05),(.15,1.7,2.15),'shell',.12,door)
 handwheel=wheel('door handwheel',(-.15,-.9,1.2),.43,(-1,0,0),door)
 for y in [-.9,0]:cube('door clamp',(-.1,y,.7),(.23,.16,.18),'brass',.02,door)
 person('fore crew',(-2.4,-.3,.15));person('second fore crew',(-3.4,.8,.15))
 cube('aft flood',(2.1,.35,1.4),(3.6,2.8,2.6),'water',.12)
 curve('overhead pipe',[(-3.6,1.6,3),(-1.3,1.6,3),(-1.3,1.6,1.7)],.08,'brass')
 for x in [-2.8,2.8]:cube('cabin lamp',(x,1.75,2.9),(.65,.16,.17),'light',.05)
 anchors={'door':(0,-.9,1.6),'dry':(-2.5,-1.2,.3),'wet':(2.4,-1.2,1.3)};camera((-9,-19,10),(0,0,1.3),16)
else:raise ValueError(K)

configure(S,M,K)
S.render.film_transparent=False
S.camera.data.clip_end=300
# Save an inspectable, reusable Blender project for every shot.
(P/'models').mkdir(exist_ok=True)

def animate(p):
 if K in BELL_KINDS:
  if bell:
   bell.location.z=.26+(1-sm(p,0,.8))*1.8 if K=='dock' else .26
   rope.data.splines[0].points[0].co=(0,0,bell.location.z+5.7,1)
   hose.data.splines[0].points[0].co=(1.0,.9,bell.location.z+4.6,1)
   # Water stays below the closed upper floor until removal is complete.
   lev=1-sm(p,.06,.83) if K=='drain' else (1 if K in ['dock','seal'] else .002)
   wet.scale.z=max(.002,lev);wet.location.z=.15+2.25*lev/2;wet.hide_render=lev<.005
   if K=='drain':
    spin_wheel(bpy.data.objects['air control'],1.7*sm(p,.18,.65))
    operate_control(bpy.data.objects['second operator'],p)
   if K=='open':
    spin_wheel(bpy.data.objects['upper hatch wheel'],1.7*sm(p,0,.20))
    spin_wheel(bpy.data.objects['sub hatch wheel'],1.7*sm(p,0,.20))
   if K=='transfer':
    spin_wheel(bpy.data.objects['upper hatch wheel'],1.7)
    spin_wheel(bpy.data.objects['sub hatch wheel'],1.7)
   upper.rotation_euler[1]=-math.pi/2*(sm(p,.22,.85) if K=='open' else (1 if K=='transfer' else 0))
   sublid.rotation_euler[1]=math.pi/2*(sm(p,.22,.85) if K=='open' else (1 if K=='transfer' else 0))
  if K=='cable':handle_line(diver,p)
  if K=='transfer':
   passenger.location.z=lerp(1.65,2.76,sm(p,0,.84));passenger.location.y=lerp(.04,-.85,sm(p,.74,1));climb_motion(passenger,p)
  if K=='seal':marker.scale=(1,1,1)
  # No constant orbit. Small purpose-driven move shows the seal from a lower angle.
  if K=='seal':camera((7.0,-20,8.2),(0,0,1.8),10.8)
  if K=='dock':
   progress=sm(p,0,.8);camera((8,-20,9),(0,0,lerp(2.8,1.8,progress)),lerp(13.4,11.4,progress))
 elif K in SUB_KINDS:
  overview=K in ['depth','rise','trips','saved','final']
  if K=='dive':sub.location.z=lerp(2.0,0,sm(p,0,.9))
  if K=='hero':camera((17,-25,15),(0,0,0),28)
  if K=='flood':update_water(sm(p,.05,.88))
  if K=='loss':update_water(1)
  if overview:
   by=lerp(.55,8.8,sm(p,.05,.87)) if K=='rise' else (8.8 if K in ['trips','saved'] else 4.1 if K=='final' else .55)
   bell.location.z=by
   wet.scale.z=1;wet.location.z=1.275
   for idx,co in enumerate([(-2.5,0,by+1.6),(-2.5,0,12)]):rope.data.splines[0].points[idx].co=(*co,1)
   if K=='depth':
    bell.hide_render=True
    for child in surf.children_recursive:child.hide_render=True
    rope.hide_render=True
   # hide the bell descendants as well when locating the wreck before solution is introduced
   if K=='depth':
    for child in bell.children_recursive:child.hide_render=True
 elif K=='valve':
  stream_update(p)
 elif K=='sealed':door.rotation_euler[2]=lerp(-.55,0,sm(p,0,.65));spin_wheel(handwheel,1.5*sm(p,.65,1))
 bpy.context.view_layer.update()

def projection():
 r={}
 for k,xyz in anchors.items():
  q=world_to_camera_view(S,CAM,Vector(xyz));r[k]=[round(q.x*1080,2),round((1-q.y)*1920,2)]
 return r

if MODE=='test':
 animate(float(os.environ.get('SNG_TEST_PROGRESS','.65')));S.render.filepath=str(P/'tests'/f'{K}.jpg');bpy.ops.render.render(write_still=True)
 (P/'tests'/f'{K}_anchors.json').write_text(json.dumps(projection(),indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'{K}.blend'),compress=True)
else:
 timings=[]
 for lang in ['ru','en']:
  timings+=json.loads((P.parent/lang/'timeline.json').read_text())
 duration=max(x['end']-x['start'] for x in timings if x['visual']==K)
 # Maximum-language duration at 30 fps; both language cuts reuse this normalized motion sequence.
 fps=30 if K=='transfer' else 15
 count=2 if K in ['hero','question','loss','depth','seal','dry','trips','saved','final'] else max(2,math.ceil(duration*fps))
 if K=='valve':count=2*math.ceil(duration*15/2)+1  # two identical cycles of the continuous surface ripple
 out=P/'frames'/K;out.mkdir(parents=True,exist_ok=True)
 metadata={'scene':K,'count':count,'native_resolution':[720,1280],'render_fps':fps,'presentation_fps':30,'normalized_duration':duration,'anchors':[]}
 for i in range(count):
  p=i/(count-1);animate(p);file=out/f'{i:04}.jpg'
  if not file.exists():
   if count==2 and i==1:shutil.copy2(out/'0000.jpg',file)
   elif K=='valve' and i>=(count-1)//2:shutil.copy2(out/f'{i%((count-1)//2):04}.jpg',file)
   else:S.render.filepath=str(file);bpy.ops.render.render(write_still=True)
  metadata['anchors'].append(projection())
 (out/'index.json').write_text(json.dumps(metadata));bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'{K}.blend'),compress=True)
 print('COMPLETE',K,count,flush=True)
