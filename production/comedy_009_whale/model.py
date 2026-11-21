import bpy,math,os
from mathutils import Vector
from math import pi
b=bpy;b.ops.wm.read_factory_settings(use_empty=True)
sc=b.context.scene
def mat(n,c,metal=0):
 m=b.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=.34;return m
green=mat('Avocado lacquer',(.22,.38,.095),.32);chrome=mat('Brushed aluminium',(.62,.71,.7),.75);tire=mat('Rubber',(.024,.031,.033));glass=mat('Smoked glass',(.052,.16,.18),.55);lamp=mat('Amber glass',(1,.66,.24));tail=mat('Red lens',(.62,.035,.022));road=mat('Tarmac',(.105,.15,.16));cream=mat('Paint',(.92,.8,.55));base=mat('Ocean studio',(.028,.17,.20))
def finish(o,m,bevel=0):
 o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def box(n,xyz,size,m,bevel=.025):
 b.ops.mesh.primitive_cube_add(size=1,location=xyz);o=b.context.object;o.name=n;o.dimensions=size;b.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,m,bevel)
def cyl(n,x,y,z,r,dep,m):
 b.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=dep,rotation=(pi/2,0,0),location=(x,y,z));o=b.context.object;o.name=n;return finish(o,m,.014)
def skin():
 # Cross sections of a long American hardtop, including the central depression in the roof.
 stations=[(-1.42,1.07,.88),(-.95,1.78,.72),(-.53,1.87,.72),(-.08,1.9,.73),(.40,1.85,.72),(.72,1.76,.71),(1.35,1.07,.86)]
 vs=[];faces=[]
 for x,z,r in stations:vs.extend([(x,-.92,1.035),(x,-r,z),(x,0,z+.035),(x,r,z),(x,.92,1.035)])
 for j in range(len(stations)-1):
  for k in range(4):q=5*j+k;faces.append((q,q+5,q+6,q+1))
 mesh=b.data.meshes.new('roof panels');mesh.from_pydata(vs,[],faces);mesh.update();o=b.data.objects.new('Hardtop and windshield',mesh);sc.collection.objects.link(o)
 for m in [green,glass,chrome]:o.data.materials.append(m)
 for j,p in enumerate(mesh.polygons):
  st,k=divmod(j,4);p.material_index=1 if st in (0,5) or k in (0,3) else 0
 o.shape_key_add(name='Intact');key=o.shape_key_add(name='Dented roof')
 for i,(x,y,z) in enumerate(vs):
  if z>1.2:key.data[i].co.z-=.72*math.exp(-((x+.04)/.70)**2)*(1-.23*abs(y))
 key.value=0;key.keyframe_insert('value',frame=38);key.value=1;key.keyframe_insert('value',frame=47)
skin()
box('parking plinth',(0,0,-.20),(6.8,3.6,.34),road,.15)
for y in [-1.48,1.48]:box('Parking stripe',(0,y,-.018),(6.27,.045,.012),cream,.003)
box('fuselage',(0,0,.73),(5.18,1.95,.66),green,.16)
for x in [-1.67,1.63]:
 for d in [-1,1]:
  cyl('Tyre',x,d*.963,.434,.448,.208,tire);cyl('Hub rim',x,d*1.07,.434,.296,.029,chrome);cyl('Colour hub',x,d*1.09,.434,.18,.018,green)
for y in [-.985,.985]:
 box('Side trim',(0,y,.88),(4.91,.035,.047),chrome)
 for x in [-.65,.52]:box('Door handle',(x,y,1.01),(.19,.04,.035),chrome)
for x in [-2.57,2.57]:box('Chrome bumper',(x,0,.52),(.14,1.99,.14),chrome,.045)
box('Nose grille',(2.58,0,.804),(.055,1.11,.24),tire)
for y in [-.49,-.36,-.23,-.1,.03,.16,.29,.42]:box('Grille slat',(2.615,y,.8),(.027,.038,.21),chrome,.005)
for y in [-.78,.78]:
 box('Headlights',(2.57,y,.83),(.09,.29,.19),lamp,.04);box('Tail lamp',(-2.59,y,.82),(.07,.29,.18),tail,.03)
box('Backdrop',(0,0,-.49),(200,200,.20),base)
def aim(obj,pos):obj.rotation_euler=(Vector(pos)-obj.location).to_track_quat('-Z','Y').to_euler()
for p,energy,size in [((3,-4,7),1000,6),((-5,2,5),800,5),((3,5,4),520,4)]:
 b.ops.object.light_add(type='AREA',location=p);o=b.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,0))
b.ops.object.camera_add();cam=b.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=8.65;sc.camera=cam
for frame,angle in [(1,-.87),(38,-1.15),(72,-1.38)]:
 cam.location=(8*math.cos(angle),8*math.sin(angle),4.55);aim(cam,(0,0,.74));cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=False;sc.cycles.max_bounces=2
sc.world=b.data.worlds.new('Softbox');sc.world.color=(.36,.36,.36)
sc.render.resolution_x=600;sc.render.resolution_y=650;sc.render.resolution_percentage=100
sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;sc.render.fps=30;sc.frame_end=72;sc.render.filepath=os.path.abspath('car/')+'/'
b.ops.wm.save_as_mainfile(filepath=os.path.abspath('car.blend'));b.ops.render.render(animation=True)
