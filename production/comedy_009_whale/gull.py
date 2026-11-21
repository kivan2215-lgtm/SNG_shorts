import bpy as b, math, os
from mathutils import Vector
b.ops.wm.read_factory_settings(use_empty=True);sc=b.context.scene
def mat(n,c):
 m=b.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);return m
white=mat('Warm white',(.94,.92,.82));grey=mat('Gull grey',(.30,.40,.46));black=mat('Wingtip black',(.032,.046,.052));gold=mat('Yellow ochre',(.92,.46,.036));blue=mat('Backdrop',(.055,.24,.30))
def empty(n,pos,parent=None):
 o=b.data.objects.new(n,None);sc.collection.objects.link(o);o.parent=parent;o.location=pos;return o
rig=empty('Gull flight',(0,0,0))
def egg(n,pos,scale,m,parent):
 b.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12);o=b.context.object;o.name=n;o.parent=parent;o.location=pos;o.scale=scale;o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
egg('Body',(0,0,0),(.85,.39,.43),white,rig);egg('Mantle',(-.13,0,.23),(.71,.38,.24),grey,rig)
head=empty('Head joint',(.53,0,.34),rig)
egg('Head',(.13,0,.11),(.34,.29,.33),white,head);egg('Bill',(.48,0,.06),(.265,.095,.083),gold,head)
for d in [-1,1]:
 egg('Iris',(.29,d*.20,.16),(.082,.071,.082),gold,head);egg('Pupil',(.32,d*.241,.17),(.05,.042,.05),black,head)
 egg('Foot',(.02,d*.15,-.43),(.17,.078,.028),gold,rig)
 wing=empty('Wing joint',(0,d*.25,.17),rig)
 def feathers(n,pts,m):
  mesh=b.data.meshes.new(n);mesh.from_pydata([(x,d*y,z) for x,y,z in pts],[],[tuple(range(len(pts)))]);mesh.materials.append(m);o=b.data.objects.new(n,mesh);sc.collection.objects.link(o);o.parent=wing
  sol=o.modifiers.new('Thickness','SOLIDIFY');sol.thickness=.036
 feathers('Inner wing',[(.33,0,0),(.24,.83,.17),(.02,1.16,.11),(-.43,1.18,.10),(-.53,.38,.01),(-.43,.02,-.03)],grey)
 feathers('Outer wing',[(.02,1.16,.11),(-.33,1.88,.10),(-.59,2.16,.05),(-.62,1.98,.05),(-.69,2.02,.05),(-.64,1.74,.08),(-.70,1.72,.08),(-.43,1.18,.10)],black)
 for f,a in [(1,.34),(11,.12),(21,.85),(32,-.45),(43,.70),(52,.16)]:
  wing.rotation_euler.x=d*a;wing.keyframe_insert('rotation_euler',frame=f)
for f,z,angle in [(1,-.08,0),(15,-.04,.07),(27,.12,.04),(39,.17,.01),(52,.26,-.07)]:
 rig.location.z=z;rig.rotation_euler.z=angle;rig.keyframe_insert('location',frame=f);rig.keyframe_insert('rotation_euler',frame=f)
for f,a in [(1,-.06),(13,-.45),(26,-.37),(49,.12)]:
 head.rotation_euler.z=a;head.keyframe_insert('rotation_euler',frame=f)
b.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.20));b.context.object.data.materials.append(blue)
def aim(o):o.rotation_euler=(Vector((0,0,.03))-o.location).to_track_quat('-Z','Y').to_euler()
for loc,energy in [((2,-5,6),750),((-3,3,5),950)]:
 b.ops.object.light_add(type='AREA',location=loc);o=b.context.object;o.data.energy=energy;o.data.size=5;aim(o)
b.ops.object.camera_add(location=(3.8,-4.8,2.4));cam=b.context.object;aim(cam);cam.data.type='ORTHO';cam.data.ortho_scale=4.5;sc.camera=cam
sc.world=b.data.worlds.new('Ambient');sc.world.color=(.4,.4,.4);sc.render.engine='CYCLES';sc.cycles.samples=6;sc.cycles.use_denoising=False;sc.cycles.max_bounces=2
sc.render.resolution_x=540;sc.render.resolution_y=470;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=1
sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;sc.render.fps=30;sc.frame_end=52;sc.render.filepath=os.path.abspath('bird')+'/'
b.ops.wm.save_as_mainfile(filepath=os.path.abspath('gull.blend'));b.ops.render.render(animation=True)
