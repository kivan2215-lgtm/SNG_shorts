import bpy as b, math, os
import numpy as np
from mathutils import Vector
b.ops.wm.read_factory_settings(use_empty=True)
sc=b.context.scene
def material(n,c,metal=0):
 m=b.data.materials.new(n);m.use_nodes=True;s=m.node_tree.nodes['Principled BSDF'];s.inputs['Base Color'].default_value=(*c,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=.23;return m
red=material('Cherry-red enamel',(.78,.019,.018),.42);ground=material('Petrol cyclorama',(.016,.082,.091))
def sample(points,n):
 p=np.array(points);s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];return np.array([np.interp(np.linspace(0,s[-1],n),s,p[:,j]) for j in range(3)]).T
co=[(.33,0,.12),(.33,0,1.2)]
for a in np.linspace(0,math.pi,25):co.append((.33*math.cos(a),0,1.2+.33*math.sin(a)))
co.append((-.33,0,-1))
for a in np.linspace(math.pi,math.pi*2,25):co.append((.47*math.cos(a)+.14,0,-1+.47*math.sin(a)))
co.append((.61,0,1.28))
for a in np.linspace(0,math.pi,25):co.append((.64*math.cos(a)-.03,0,1.28+.64*math.sin(a)))
co.append((-.67,0,-.64))
home=[(-1,-.65,-1),(1,-.65,-1),(1,-.65,.5),(0,-.65,1.48),(-1,-.65,.5),(-1,-.65,-1),(-1,.73,-1),(-1,.73,.5),(0,.73,1.48),(0,-.65,1.48),(0,.73,1.48),(1,.73,.5),(1,-.65,.5),(1,.73,.5),(1,.73,-1),(-1,.73,-1)]
p=sample(co,96);h=sample(home,96);curve=b.data.curves.new('Single wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.065;curve.bevel_resolution=4
sp=curve.splines.new('POLY');sp.points.add(95)
for v,xyz in zip(sp.points,p):v.co=(*xyz,1)
obj=b.data.objects.new('Paperclip to house',curve);sc.collection.objects.link(obj);obj.data.materials.append(red);obj.shape_key_add(name='Paperclip');k=obj.shape_key_add(name='House')
for v,xyz in zip(k.data,h):v.co=xyz
for f,val in [(1,0),(12,0),(41,1),(54,1)]:k.value=val;k.keyframe_insert('value',frame=f)
for f,r in [(1,-.2),(54,.32)]:obj.rotation_euler.z=r;obj.keyframe_insert('rotation_euler',frame=f)
b.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.56));b.context.object.data.materials.append(ground)
def aim(o):o.rotation_euler=(Vector((0,0,.18))-o.location).to_track_quat('-Z','Y').to_euler()
for pos,en,size in [((-3,-4,6),1150,4),((3,1,3),850,3),((0,-4,1),250,3)]:
 b.ops.object.light_add(type='AREA',location=pos);o=b.context.object;o.data.energy=en;o.data.size=size;aim(o)
b.ops.object.camera_add(location=(2.15,-7.5,2.25));cam=b.context.object;aim(cam);cam.data.type='ORTHO';cam.data.ortho_scale=4.65;sc.camera=cam
sc.world=b.data.worlds.new('Studio');sc.world.color=(.3,.3,.3);sc.render.engine='CYCLES';sc.cycles.samples=6;sc.cycles.use_denoising=False;sc.cycles.max_bounces=2;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=520;sc.render.resolution_y=580;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;sc.render.fps=30;sc.frame_end=54;sc.render.filepath=os.path.abspath('model')+'/'
b.ops.wm.save_as_mainfile(filepath=os.path.abspath('wire.blend'));b.ops.render.render(animation=True)
