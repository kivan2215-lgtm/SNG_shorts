import bpy,math,sys,json,random
from pathlib import Path
from mathutils import Vector
P=Path(__file__).parent;K=sys.argv[sys.argv.index('--')+1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.max_bounces=3;s.render.resolution_x=720;s.render.resolution_y=1280;s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.045,.065,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
s.view_settings.view_transform='AgX'
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.42;return m
M={n:mat(n,c,met) for n,c,met in [('gold',(.63,.35,.07),.75),('blue',(.012,.06,.20),.45),('metal',(.4,.46,.50),.8),('cream',(.6,.56,.43),0),('black',(.018,.03,.04),.1),('screen',(.025,.16,.18),.2),('cyan',(.02,.65,.62),.3),('red',(.85,.13,.04),.2)]}
def mesh(o,n,m,parent=None):
 o.name=n;o.data.materials.append(M[m]);o.parent=parent
 for f in o.data.polygons:f.use_smooth=True
 return o
def box(n,loc,size,m,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mesh(o,n,m,parent);b=o.modifiers.new('Rounded','BEVEL');b.width=.025;b.segments=2;return o
def sphere(n,loc,r,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=r,location=loc);return mesh(bpy.context.object,n,m)
def rod(n,a,b,r,m,parent=None):
 v=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=v.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return mesh(o,n,m,parent)
def path(n,pts,m,r=.016):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for a,b in zip(sp.points,pts):a.co=(*b,1)
 o=bpy.data.objects.new(n,cu);s.collection.objects.link(o);o.data.materials.append(M[m]);return o
if K=='orbit':
 M['mars']=mat('Mars',(.4,.10,.035));nt=M['mars'].node_tree;pr=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=6;ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.08,.025,.012,1);ramp.color_ramp.elements[1].color=(.65,.26,.09,1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],pr.inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.35;bump.inputs['Distance'].default_value=.13;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],pr.inputs['Normal'])
 sphere('Mars',(0,0,0),2.2,'mars')
 # Offset arcs communicate low vs planned passage, not an exact flight reconstruction.
 for r,m in [(3.2,'cyan'),(2.38,'red')]:
  pts=[(r*math.cos(a),-.9,r*math.sin(a)) for a in [math.pi*(.12+i*.76/100) for i in range(101)]];path('Expected' if m=='cyan' else 'Low pass',pts,m)
 root=bpy.data.objects.new('Spacecraft',None);s.collection.objects.link(root);root.scale=(.72,.72,.72)
 box('Foil bus',(0,0,0),(.43,.38,.5),'gold',root)
 for x in [-.19,.19]:rod('Frame',(x,-.21,-.25),(x,-.21,.25),.013,'metal',root)
 rod('Solar spar',(.2,0,0),(1.25,0,0),.02,'metal',root)
 for j in range(3):
  x=.43+j*.31;box('Solar segment',(x,0,0),(.29,.025,.55),'blue',root)
  for z in [-.22,-.11,0,.11,.22]:rod('Cell row',(x-.14,-.02,z),(x+.14,-.02,z),.003,'metal',root)
 rod('Dish mast',(-.2,0,.1),(-.45,0,.32),.018,'metal',root)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(-.47,0,.34));o=bpy.context.object;o.scale=(.17,.045,.17);mesh(o,'High gain dish','cream',root)
 for x in [-.13,.13]:rod('Thruster',(x,0,-.25),(x,0,-.34),.045,'black',root)
 def state(i):
  u=i/60;e=u*u*(3-2*u);a=math.pi*(.88-.76*e);r=2.38;root.location=(r*math.cos(a),-1.22,r*math.sin(a));root.rotation_euler.y=.15*math.sin(a)
 cam=(0,-15,5);target=(0,0,.45);scale=11.6;count=61
else:
 box('Desk',(0,0,-.1),(7,3,.2),'black')
 for x in [-1.8,1.8]:
  box('CRT body',(x,.25,.9),(1.55,.85,1.3),'cream');box('Glass',(x,-.20,.9),(1.27,.03,.93),'screen');box('Base',(x,.3,.2),(.9,.7,.15),'cream');box('Keyboard',(x,-.9,.08),(1.6,.55,.1),'cream')
  for row in range(4):
   for col in range(12):box('Key',(x-.70+col*.125,-1.10+row*.115,.15),(.095,.08,.035),'black')
 path('Data link',[(-1,-.35,.4),(0,-.6,.4),(1,-.35,.4)],'cyan',.045)
 def state(i):pass
 cam=(7,-12,9);target=(0,0,.7);scale=10;count=1
for pos,power,size,col in [((-5,-7,9),1400,7,(1,.72,.43)),((6,-2,7),1700,6,(.45,.75,1))]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=col;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=cam);o=bpy.context.object;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;s.camera=o
out=P/'frames'/K;out.mkdir(parents=True,exist_ok=True)
for i in range(count):
 state(i);s.render.filepath=str(out/f'{i:04}.jpg');bpy.ops.render.render(write_still=True)
(out/'index.json').write_text(json.dumps({'frames':count,'fps':30,'source_size':[720,1280],'schematic':True,'not_to_scale':True,'camera':'fixed'}))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'{K}.blend'),compress=True)
