import bpy as b,math,os
from mathutils import Vector
b.ops.wm.read_factory_settings(use_empty=True);sc=b.context.scene
def material(n,c,metal=0):
 m=b.data.materials.new(n);m.use_nodes=True;s=m.node_tree.nodes['Principled BSDF'];s.inputs['Base Color'].default_value=(*c,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=.24;return m
plum=material('Aubergine leather',(.16,.027,.057));gold=material('Brass',(.8,.48,.14),.74);velvet=material('Velvet',(.013,.09,.089));blue=material('Lapis',(.035,.13,.65),.33);black=material('Black lacquer',(.018,.018,.025),.40);ground=material('Jade surface',(.025,.165,.15))
def box(name,p,dims,m,parent=None,bev=.035):
 b.ops.mesh.primitive_cube_add(size=1);o=b.context.object;o.name=name;o.dimensions=dims;b.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=parent;o.location=p;o.data.materials.append(m);mod=o.modifiers.new('Rolled edges','BEVEL');mod.width=bev;mod.segments=4;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o
def empty(n,p):
 o=b.data.objects.new(n,None);sc.collection.objects.link(o);o.location=p;return o
box('Case',(0,0,0),(3.9,1.4,.36),plum,bev=.1);box('Binding',(0,0,.178),(3.84,1.34,.043),gold);box('Tray',(0,0,.21),(3.72,1.23,.08),velvet)
lid=empty('Hinge',(0,.66,.22));box('Cover',(0,-.66,.14),(3.91,1.40,.27),plum,lid,.09);box('Lining',(0,-.66,.004),(3.71,1.23,.05),velvet,lid)
for f,deg in [(1,0),(20,-102),(49,-102),(65,0)]:
 lid.rotation_euler.x=math.radians(deg);lid.keyframe_insert('rotation_euler',frame=f)
pen=empty('Fountain pen',(0,0,.36))
def barrel(n,x,rad,depth,m):
 b.ops.mesh.primitive_cylinder_add(vertices=48,radius=rad,depth=depth);o=b.context.object;o.name=n;o.parent=pen;o.location=(x,0,0);o.rotation_euler.y=math.pi/2;o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
barrel('Barrel',-.30,.101,1.98,black);barrel('Cap',.9,.127,1.03,blue)
for x in [.37,.44,1.4,-1.3]:barrel('Gilt ring',x,.131 if x>0 else .105,.047,gold)
box('Clip',(.93,-.052,.12),(.81,.049,.04),gold,pen,.018)
for f,pos in [(1,(0,0,.36)),(26,(0,0,.36)),(36,(0,0,1.0)),(45,(5,0,1.5))]:
 pen.location=pos;pen.keyframe_insert('location',frame=f)
box('Table',(0,0,-.30),(200,200,.22),ground)
def aim(o):o.rotation_euler=(Vector((0,0,.52))-o.location).to_track_quat('-Z','Y').to_euler()
for pos,en,size in [((-3,-4,6),950,4),((3,1,3),650,3),((0,-4,1),200,3)]:
 b.ops.object.light_add(type='AREA',location=pos);o=b.context.object;o.data.energy=en;o.data.size=size;aim(o)
b.ops.object.camera_add(location=(2.5,-7.4,5.0));cam=b.context.object;aim(cam);cam.data.type='ORTHO';cam.data.ortho_scale=5.4;sc.camera=cam
sc.world=b.data.worlds.new('Studio');sc.world.color=(.35,.35,.35);sc.render.engine='CYCLES';sc.cycles.samples=5;sc.cycles.use_denoising=False;sc.cycles.max_bounces=2;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=540;sc.render.resolution_y=500;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;sc.render.fps=30;sc.frame_end=65;sc.render.filepath=os.path.abspath('model')+'/'
b.ops.wm.save_as_mainfile(filepath=os.path.abspath('case.blend'));b.ops.render.render(animation=True)
