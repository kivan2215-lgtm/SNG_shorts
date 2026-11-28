"""Blender 4.3. Single-thread Cycles stage, with isolated turntable poses for the speaking deacon."""
import bpy, math, json, os, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from math import sin, cos, pi
root=Path(__file__).resolve().parent
work=root/'court_frames';work.mkdir(exist_ok=True)
b=bpy; b.ops.wm.read_factory_settings(use_empty=True)
sc=b.context.scene
sc.render.engine='CYCLES';sc.cycles.samples=9;sc.cycles.use_denoising=False;sc.cycles.use_adaptive_sampling=True
sc.render.threads_mode='FIXED';sc.render.threads=1
sc.render.resolution_x=720;sc.render.resolution_y=1280;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA'
sc.render.film_transparent=False;sc.world=b.data.worlds.new('Night around the model');sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.055,.083,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
sc.view_settings.view_transform='AgX'
def mat(name,rgb,metal=0,rough=.72,grit=0,light=0):
 m=b.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if light:p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=light
 if grit:
  t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=23;t.inputs['Detail'].default_value=2.8
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=grit;bump.inputs['Distance'].default_value=.045
  m.node_tree.links.new(t.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
stone=[mat('Travertine '+str(i),c,grit=.26) for i,c in enumerate([(.38,.298,.211),(.48,.365,.243),(.312,.239,.177),(.243,.203,.166)])]
teal=mat('Deep green marble',(.036,.095,.093),.12,.35,.19);marble=mat('Honey marble',(.63,.475,.302),.05,.48,.12)
gold=mat('Burnished bronze',(.532,.298,.082),.67,.34,.14);goldlight=mat('Gold embroidery',(.76,.46,.135),.44,.4)
bronze=mat('Blackened bronze',(.098,.074,.044),.58,.45,.1);wood=mat('Old waxed oak',(.092,.040,.022),0,.43,.2)
rose=mat('Oxblood wool',(.283,.033,.043),grit=.25);russet=mat('Sleeve vermilion',(.38,.054,.045),grit=.23)
ivory=mat('Old ivory linen',(.716,.585,.369),grit=.22);violet=mat('Faded violet',(.176,.085,.161),grit=.23);linen=mat('Dalmatic indigo',(.085,.148,.175),grit=.24)
dark=mat('Night wool',(.04,.071,.092),grit=.21);skin=mat('Fired ochre skin',(.518,.302,.158),rough=.65,grit=.13);nose=skin
shadow=mat('Shadow in the cowl',(.086,.065,.072),rough=.94);hair=mat('Tonsure',(.087,.054,.033),grit=.15)
page=mat('Parchment',(.805,.65,.4),rough=.77,grit=.18);wax=mat('Wax',(.79,.565,.258),rough=.55)
flame=mat('Flame',(.98,.535,.130),rough=.3,light=7);sky=mat('Apse recess',(.029,.086,.106),.12,.45,.1)
black=mat('Stage charcoal',(.018,.028,.038),rough=.77);floorA=mat('Polished porphyry',(.245,.127,.113),.1,.38,.12);floorB=mat('Green tesserae',(.072,.150,.142),.12,.41,.13)
tiles=[floorA,floorB,stone[0],stone[1]]
tmp=None
def obj_finish(o,n,m):
 o.name=n
 if m:o.data.materials.append(m)
 if tmp is not None and o.type=='MESH':o.parent=tmp
 return o
def box(n,loc,size,m,bevel=.025,rot=0):
 b.ops.mesh.primitive_cube_add(size=1,location=loc);o=b.context.object
 for v in o.data.vertices:
  for i in range(3):v.co[i]*=size[i]
 o.rotation_euler[2]=rot
 if bevel:
  mod=o.modifiers.new('Dressed edges','BEVEL');mod.width=bevel;mod.segments=2
  mod=o.modifiers.new('Face normals','WEIGHTED_NORMAL')
 return obj_finish(o,n,m)
def sph(n,p,scale,m):
 b.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=12,location=p);o=b.context.object;o.scale=scale
 for f in o.data.polygons:f.use_smooth=True
 return obj_finish(o,n,m)
def cylinder(n,p,r,depth,m,top=None):
 b.ops.mesh.primitive_cone_add(vertices=24,radius1=r,radius2=r if top is None else top,depth=depth,location=p);o=b.context.object
 for f in o.data.polygons:
  if len(f.vertices)==4:f.use_smooth=True
 return obj_finish(o,n,m)
def line(n,a,z,r,m,r2=None):
 a,z=Vector(a),Vector(z);d=z-a;o=cylinder(n,(a+z)*.5,r,d.length,m,r2);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def local(ox,oy,ang,x,y,z):return (ox+x*cos(ang)-y*sin(ang),oy+x*sin(ang)+y*cos(ang),z)
def mesh(n,verts,faces,m):
 me=b.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=b.data.objects.new(n,me);sc.collection.objects.link(o);return obj_finish(o,n,m)
def cloth(n,x,y,z,levels,m,ang=0):
 verts=[];N=40
 for h,rx,ry,dx,dy in levels:
  for i in range(N):
   q=i*2*pi/N;r=1+.065*cos(q*9+.2)+.022*cos(q*5)
   verts.append(local(x,y,ang,dx+rx*r*cos(q),dy+ry*r*sin(q),z+h))
 faces=[tuple(reversed(range(N))),tuple((len(levels)-1)*N+i for i in range(N))]
 faces += [(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(len(levels)-1) for i in range(N)]
 o=mesh(n,verts,faces,m)
 for f in o.data.polygons:f.use_smooth=True
 return o
def arch(cx,cy,zc,r,t,mats):
 for j in range(13):
  a=j*pi/13+.007;e=(j+1)*pi/13-.007;out=r+t+(.08 if j==6 else 0)
  vs=[(cx+rr*cos(th),yy,zc+rr*sin(th)) for yy in [cy-.21,cy+.21] for rr,th in [(r,a),(out,a),(out,e),(r,e)]]
  mesh('Dressed limestone voussoir',vs,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],mats[(j+int(cx)+5)%len(mats)])
def col(x,y,h):
 for z,r,d,m in [(.12,.34,.24,stone[1]),(.31,.30,.15,marble),(.47,.265,.14,stone[0]),(h-.18,.29,.16,marble),(h-.05,.33,.14,stone[1])]:
  cylinder('Column molding',(x,y,z),r,d,m)
 cylinder('Marble shaft',(x,y,(h+.38)/2),.237,h-.68,stone[0],.215)
 for z in [.64,h-.36]:cylinder('Metal fillet',(x,y,z),.242,.037,gold)
def seat(x,y,z,ang):
 p=lambda a,b,c:local(x,y,ang,a,b,z+c)
 for xx in [-.43,.43]:
  for yy in [-.36,.36]:box('Throne foot',p(xx,yy,.39),(.13,.13,.8),wood,.025,ang)
 box('Throne seat',p(0,0,.78),(1.08,.95,.15),wood,.04,ang)
 box('Cushion',p(0,0,.89),(.99,.84,.13),violet,.08,ang)
 box('High throne back',p(0,.38,1.62),(1.16,.18,1.69),wood,.052,ang);box('Inlaid panel',p(0,.27,1.73),(.86,.05,1.25),teal,.03,ang)
 for xx in [-.50,.50]:
  box('Throne arm',p(xx,-.04,1.21),(.16,.85,.13),gold,.06,ang)
  box('Gilded rail',p(xx,.279,1.78),(.055,.045,1.43),gold,.012,ang)
  sph('Throne finial',p(xx,.38,2.49),(.088,.088,.088),gold)
 for c in (1.06,2.42):box('Gilt molding',p(0,.25,c),(.95,.06,.057),gold,.012,ang)
def hat(x,y,z,ang,m):
 verts=[local(x,y,ang,rx,ry,z+dz) for rx,ry,dz in [(-.22,-.095,0),(.22,-.095,0),(0,-.080,.33),(-.22,.095,0),(.22,.095,0),(0,.08,.30)]]
 mesh('White liturgical cap',verts,[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],m)
 line('Embroidered band',local(x,y,ang,-.196,-.10,z+.046),local(x,y,ang,.196,-.1,z+.046),.024,goldlight)
def person(x,y,z,ang,role):
 p=lambda a,b,c:local(x,y,ang,a,b,z+c)
 if role=='deacon':
  cloth('Deacon cassock',x,y,z,[(0,.42,.31,0,0),(.12,.42,.32,0,0),(.93,.24,.19,0,0),(1.53,.34,.21,0,0),(1.56,.14,.12,0,0)],dark,ang)
  cloth('Dark blue dalmatic',x,y,z,[(.81,.31,.25,0,0),(1.22,.28,.23,0,0),(1.53,.36,.20,0,0),(1.61,.14,.12,0,0)],linen,ang)
  line('Woven diagonal stole',p(-.22,-.142,1.50),p(.21,-.22,.88),.041,goldlight)
  arms=[((-.28,0,1.44),(-.34,-.17,1.16),(-.22,-.42,1.35)),((.28,0,1.44),(.36,-.10,1.18),(.32,-.36,1.22))]
  headh=1.80;body=linen
 elif role=='presider':
  cloth('Pope’s alb',x,y,z,[(0,.51,.34,0,0),(.12,.53,.36,0,0),(.79,.31,.26,0,0),(1.37,.31,.22,0,0)],ivory,ang)
  cloth('Red cope',x,y,z,[(.16,.49,.33,0,.04),(.62,.40,.30,0,.04),(1.09,.31,.24,0,0),(1.46,.37,.23,0,0),(1.56,.13,.11,0,0)],rose,ang)
  for a in [-1,1]:line('Cope orphrey',p(.19*a,-.17,1.49),p(.32*a,-.233,.25),.046,goldlight)
  arms=[((-.24,0,1.40),(-.32,-.13,1.18),(-.26,-.34,1.27)),((.26,0,1.42),(.39,-.18,1.31),(.40,-.62,1.38))]
  headh=1.75;body=russet
 else:
  seat(x,y,z,ang)
  cloth('Formosus robe',x,y,z,[(.16,.42,.35,0,-.21),(.52,.39,.34,0,-.22),(.96,.39,.44,0,-.12),(1.20,.32,.24,0,0),(1.60,.33,.22,0,.02),(1.69,.15,.13,0,.03)],violet,ang)
  cloth('Faded chasuble',x,y,z,[(.47,.37,.23,0,-.36),(.91,.36,.31,0,-.26),(1.06,.31,.26,0,-.12),(1.58,.34,.23,0,0),(1.68,.13,.13,0,0)],ivory,ang)
  line('Liturgical cross vertical',p(0,-.232,1.48),p(0,-.42,.92),.039,goldlight)
  line('Liturgical cross transverse',p(-.13,-.275,1.34),p(.13,-.275,1.34),.037,goldlight)
  arms=[((-.29,0,1.53),(-.37,-.08,1.25),(-.32,-.31,1.12)),((.29,0,1.53),(.37,-.08,1.25),(.31,-.29,1.12))]
  headh=1.87;body=violet
 for a,e,w in arms:
  line('Sleeve upper',p(*a),p(*e),.14,body,.121);line('Sleeve lower',p(*e),p(*w),.124,body,.091)
  sph('Sleeve cuff',p(*w),(.105,.104,.079),goldlight if role!='deacon' else ivory)
  hand=tuple(w[i]+(0,-.064,0)[i] for i in range(3));sph('Hand',p(*hand),(.082,.082,.094),shadow if role=='accused' else skin)
 if role=='presider':
  s=p(-.26,-.44,1.31);o=box('Rolled question parchment',s,(.30,.073,.26),page,.015,ang);line('Scroll roller',p(-.43,-.44,1.42),p(-.09,-.44,1.42),.033,marble)
 skinm=shadow if role=='accused' else skin
 sph('Head',p(0,-.04,headh),(.207,.18,.246),skinm)
 if role=='accused':
  cloth('Burial cowl',x,y,z,[(1.66,.24,.18,0,.025),(1.92,.225,.164,0,.04),(2.08,.12,.13,0,.04)],violet,ang)
  sph('Shadowed unlit face',p(0,-.155,1.87),(.153,.055,.184),shadow);hat(*p(0,.017,2.02),ang,ivory)
 else:
  sph('Nose',p(0,-.211,headh-.018),(.058,.056,.069),skinm)
  for a in [-1,1]:sph('Eye',p(.082*a,-.187,headh+.028),(.026,.018,.015),hair)
  sph('Hair',p(0,-.018,headh+.135),(.208,.178,.115),hair)
  if role=='presider':hat(*p(0,0,headh+.13),ang,ivory)
  else:sph('Tonsure',p(0,-.018,headh+.234),(.102,.088,.028),skin)
def light(n,pos,power,color,size,look,typ='AREA'):
 ld=b.data.lights.new(n,typ);ld.energy=power;ld.color=color
 if typ=='AREA':ld.shape='DISK';ld.size=size
 else:ld.shadow_soft_size=size
 o=b.data.objects.new(n,ld);sc.collection.objects.link(o);o.location=pos
 if typ=='AREA':o.rotation_euler=(Vector(look)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
def candle(x,y,z,count=3):
 cylinder('Lamp base',(x,y,z+.03),.25,.065,bronze);cylinder('Lamp foot',(x,y,z+.13),.13,.22,gold,.068)
 cylinder('Lamp standard',(x,y,z+.54),.052,.81,gold)
 for j in range(count):
  xx=x+(j-(count-1)/2)*.155;zz=z+.90+(.09 if j==count//2 else 0)
  line('Curving holder',(x,y,z+.69),(xx,y,zz-.018),.021,bronze)
  cylinder('Wax lamp',(xx,y,zz+.09),.042,.23,wax)
  sph('Glowing wick',(xx,y,zz+.243),(.028,.027,.074),flame)
 light('Amber practical',(x,y,z+1.20),11,(1,.43,.13),.32,(0,0,0),'POINT')
box('Night ground',(0,0,-1.12),(200,200,.16),black)
box('Reliquary foot',(0,-.10,-.63),(7.44,5.25,.75),wood,.125)
box('Deep offset bevel',(0,-.10,-.66),(7.61,5.34,.22),bronze,.07)
box('Gold base inlay',(0,-.10,-.36),(7.52,5.30,.062),gold,.018)
box('Marble upper base',(0,-.10,-.20),(7.70,5.42,.25),teal,.056)
box('Floor face',(0,-.10,-.065),(7.74,5.44,.12),stone[2],.035)
for iy in range(7):
 for ix in range(10):
  x=(ix-4.5)*.735;y=(iy-3)*.723
  box('Mosaic pavement',(x,y-.11,.008),(.718,.707,.035),tiles[(ix%2+(iy%2)*3)%4],.008)
for xx in [-3.68,3.68]:box('Inlaid floor band',(xx,-.11,.025),(.07,5.06,.04),gold,.008)
for yy in [-2.66,2.44]:box('Inlaid floor band',(0,yy,.025),(7.44,.07,.04),gold,.008)
box('Rear apse screen',(0,2.43,2.47),(7.48,.30,4.97),teal,.07)
for j in range(3):
 x=(j-1)*2.30
 box('Recess behind arch',(x,2.24,2.25),(1.96,.16,4.15),sky,.065)
 for i in range(7):
  xx=x+(i-3)*.238
  box('Apse panel border',(xx,2.125,1.07),(.06,.05,1.25),bronze,.008)
 arch(x,2.02,3.11,.94,.25,stone)
 for xx in [x-1.025,x+1.025]:col(xx,2.01,3.13)
 for h in [.26,.45]:box('Marble wainscot',(x,1.98,h),(1.90,.14,.065),marble,.009)
box('Upper entablature',(0,2.32,4.63),(7.61,.58,.18),stone[1],.03)
box('Frieze',(0,2.22,4.82),(7.67,.61,.20),teal,.035);box('Crown molding',(0,2.20,4.975),(7.75,.68,.115),gold,.025)
for jj in range(39):sph('Filigree roundel',((jj-19)*.185,1.906,4.82),(.037,.016,.037),gold)
for x,z in [(-2.10,.75),(2.04,.46)]:
 for idx,(y,wx,dep,h) in enumerate([(.41,2.24,2.19,.15),(.49,2.13,1.90,.13),(.58,2.04,1.65,z-.28)]):
  zz=[.065,.20,.28+(z-.28)*.5][idx];box('Raised tribunal dais',(x,y,zz),(wx,dep,h),stone[idx],.024)
 for k in [-.87,.87]:box('Dais gold border',(x+k,.65,z+.005),(.038,1.38,.02),gold,.005)
person(-2.12,.47,.74,.85,'presider');person(2.08,.60,.45,-.62,'accused')
# The figures occupy complementary profile angles, with the advocate in front.
for x,y,z in [(-2.98,1.10,.75),(2.99,1.38,.46),(-2.82,-1.32,.015),(2.87,-1.25,.015)]:candle(x,y,z)
light('West window softbox',(-3.6,-4.5,7),560,(1,.78,.57),4.0,(0,0,1.3))
light('Cool clerestory',(3,1,6.9),655,(.50,.73,.95),4.0,(0,.5,1.5))
light('Viewer side fill',(1.6,-5,4),170,(.77,.81,1),4.0,(0,0,1.2))
light('Crown glint',(-.2,2.6,6.6),310,(1,.65,.34),2.4,(0,0,1.2))
cd=b.data.cameras.new('Court camera');cam=b.data.objects.new('Court camera',cd);sc.collection.objects.link(cam)
cam.location=(.8,-13.4,7.2);target=Vector((0,-.04,2.10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=14.25;sc.camera=cam
b.context.view_layer.update()
xy=lambda p: (lambda v:[round(v.x*720,2),round((1-v.y)*1280,2)])(world_to_camera_view(sc,cam,Vector(p)))
coords={'presider':xy((-1.67,.07,2.01)),'deacon':xy((.04,-.94,1.52)),'sit':xy((2.13,.20,2.0))};(work/'anchors.json').write_text(json.dumps(coords))
sc.render.filepath=str(work/'stage.png');b.ops.render.render(write_still=True)
# Cache the static palace. Render only the deacon for smoothly varying rotations.
static=[o for o in sc.objects if o.type=='MESH']
for o in static:o.hide_render=True
tmp=b.data.objects.new('Deacon pivot',None);sc.collection.objects.link(tmp);tmp.location=(.06,-.85,.055)
person(0,0,0,0,'deacon')
sc.render.film_transparent=True
sc.render.use_border=True;sc.render.use_crop_to_border=True
# Blender's border in bottom-up unit coordinates. Center deacon fits within these coordinates.
sc.render.border_min_x=.395;sc.render.border_max_x=.65;sc.render.border_min_y=.265;sc.render.border_max_y=.56
sc.cycles.samples=5
for j in range(13):
 ang=(-.94+1.63*j/12);tmp.rotation_euler[2]=ang
 sc.render.filepath=str(work/('turn%02d.png'%j));b.ops.render.render(write_still=True)
