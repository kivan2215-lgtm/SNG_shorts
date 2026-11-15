"""Topic-specific explanatory models, not actual evidence or medical instructions."""
import bpy,math,sys,json,random
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).parent;K=sys.argv[sys.argv.index('--')+1]
sys.path.insert(0,str(P))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=10;S.cycles.use_denoising=True;S.cycles.max_bounces=4
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

M.update({
'cloth':mat('Teal flight suit',(.025,.20,.24),0,.75),
'trousers':mat('Teal trousers',(.025,.16,.19),0,.8),
'boot':mat('Rubber boots',(.025,.025,.026),0,.85),
'hair':mat('Hair',(.045,.025,.015)),
'eyewhite':mat('Eyes',(.8,.8,.75)),
'iris':mat('Iris',(.10,.17,.18)),
'grass':mat('Spring grass',(.15,.24,.08),0,1),
'earth':mat('Ploughed earth',(.23,.12,.055),0,1),
'cream':mat('House plaster',(.70,.66,.53),0,.9)})
def empty(n,l,parent=None):
 o=bpy.data.objects.new(n,None);S.collection.objects.link(o);o.location=l;o.parent=parent;return o
def uv(n,l,sc,m,parent=None):
 o=sphere(n,l,sc,M[m]);o.parent=parent;return o

def textured(n,lo,hi,scale,bump):
 m=M[n];nodes=m.node_tree.nodes;links=m.node_tree.links;b=nodes.get('Principled BSDF');noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=4
 ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*lo,1);ramp.color_ramp.elements[1].color=(*hi,1);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],b.inputs['Base Color'])
 bu=nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.6;bu.inputs['Distance'].default_value=bump;links.new(noise.outputs['Fac'],bu.inputs['Height']);links.new(bu.outputs['Normal'],b.inputs['Normal'])
textured('earth',(.055,.025,.012),(.24,.13,.065),18,.09)
textured('grass',(.025,.07,.012),(.23,.32,.08),22,.06)
textured('wood',(.055,.022,.01),(.20,.095,.035),6,.02)
M['canopy']=mat('Blue ripstop fabric',(.025,.16,.30),0,.92)
M['canopy2']=mat('Green ripstop fabric',(.035,.32,.16),0,.92)
def terrain():
 box('Earth section',(0,0,-.20),(10,8,.35),'earth')
 # Continuous uneven soil mesh: no wooden-looking repeated planks.
 rng=random.Random(35);v=[];f=[];nx=160;ny=100
 for j in range(ny+1):
  for i in range(nx+1):
   x=-5+10*i/nx;y=-4+8*j/ny
   z=.025+.10*(.5+.5*math.sin(x*19+.11*math.sin(y*2)))+rng.uniform(-.027,.027)
   v.append((x,y,z))
 for j in range(ny):
  for i in range(nx):a=j*(nx+1)+i;f.append((a,a+1,a+nx+2,a+nx+1))
 me=bpy.data.meshes.new('Organic furrowed soil');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('Ploughed field',me);S.collection.objects.link(o);finish(o,'earth')
 box('Grass verge',(0,3.6,.04),(10,.65,.15),'grass')
 for x in [-4.5,-3,-1.5,0,1.5,3,4.5]:rod('Fence post',(x,3.6,.1),(x,3.6,.7),.045,'wood')
 rod('Fence rail',(-5,3.6,.5),(5,3.6,.5),.025,'wood')
 for j in range(20):
  x=rng.uniform(-4.8,4.8);y=rng.uniform(3.35,3.8);sphere('Low hedgerow',(x,y,.16),(.22,.15,.15),'grass')

if K=='descent':
 import human_model
 terrain();root=human_model.create('Anonymous skydiver',(0,0,4.5),M,empty,uv,None,None,pose='stand')
 # Generic closed helmet and pack. No operational sabotage detail.
 st=human_model.PEOPLE[int(root['human_index'])]
 for side,sgn in [('L',1),('R',-1)]:st['targets']['arm'+side].location=(sgn*.19,.03,1.50)
 helmet=uv('Sports helmet',(0,-.005,1.74),(.15,.15,.19),'dark',root)
 pack=box('Parachute pack',(0,.15,1.20),(.39,.26,.55),'dark');pack.parent=root
 for x in [-.13,.13]:
  strap=box('Harness shoulder strap',(x,-.13,1.25),(.05,.04,.50),'dark');strap.parent=root
 # A slack collapsed canopy: explanatory scale, not a reconstruction of precise aerodynamics.
 mesh=bpy.data.meshes.new('Slack fabric mesh');verts=[];faces=[]
 for j in range(13):
  for i in range(17):
   u=i/16;v=j/12;verts.append(((u-.5)*1.8,.25*math.sin(u*math.pi*5)+.45*v,2.45+v*.65+.10*math.sin(u*math.pi*6)))
 for j in range(12):
  for i in range(16):a=j*17+i;faces.append((a,a+1,a+18,a+17))
 mesh.from_pydata(verts,[],faces);mesh.update();canopy=bpy.data.objects.new('Uninflated canopy diagram',mesh);S.collection.objects.link(canopy);canopy.parent=root;finish(canopy,'canopy');canopy.data.materials.append(M['canopy2'])
 for face in canopy.data.polygons:face.material_index=(face.index%16)//4%2
 sol=canopy.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.012
 for x in [-.8,-.4,0,.4,.8]:
  line=curve('Suspension line',[(x,.3,2.5),(.4*x,.20,1.9),(.15 if x>0 else -.15,.10,1.45)],.008,'ivory');line.parent=root
 camera((10,-17,13),(0,0,3),15)
 anchors.update(field=(0,-1,0),skydiver=(0,0,5.5))
 def state(i):
  q=i/60;q=q*q*(3-2*q);root.location.z=4.5-2.8*q
 count=61
elif K=='house':
 box('Foundation',(0,0,-.12),(7,6,.24),'dark');box('Floor',(0,0,.03),(6.8,5.8,.1),'wood')
 box('Rear wall',(0,3,1.6),(7,.16,3.3),'cream');box('Side wall',(-3.5,0,1.6),(.16,6,3.3),'cream')
 box('Window',(-1.5,2.88,1.9),(2.0,.08,1.4),'blue')
 for x in [-2.5,-1.5,-.5]:box('Window frame',(x,2.79,1.9),(.06,.1,1.4),'ivory')
 box('Counter',(1,2,1),(3.5,1.4,2),'ivory');box('Worktop',(1,2,2.05),(3.7,1.5,.12),'dark')
 for x in [0,1,2]:box('Drawer',(x,1.25,1.1),(.8,.05,1.6),'paper');rod('Handle',(x-.2,1.19,1.6),(x+.2,1.19,1.6),.03,'steel')
 box('Oven',(-1.6,2.05,.8),(1.2,1.5,1.6),'steel');box('Oven glass',(-1.6,1.26,.8),(.9,.06,.8),'dark')
 for x in [-1.9,-1.3]:
  for y in [1.7,2.3]:rod('Hob burner',(x,y,1.62),(x,y,1.65),.19,'dark')
 box('Table',(0,-1,1),(2.3,1.4,.12),'wood')
 for x in [-.9,.9]:
  for y in [-1.5,-.5]:rod('Table leg',(x,y,0),(x,y,.95),.045,'steel')

 box('Sink rim',(.35,2,2.12),(1.1,.85,.06),'steel');box('Sink basin',(.35,2,2.15),(.92,.66,.04),'dark')
 curve('Kitchen tap',[(.35,2.5,2.1),(.35,2.5,2.55),(.35,2.15,2.55),(.35,2.15,2.35)],.035,'steel')
 for x in [1.6,2.2]:
  rod('Kitchen storage jar',(x,2.45,2.12),(x,2.45,2.55),.16,'glass');rod('Jar lid',(x,2.45,2.54),(x,2.45,2.59),.18,'wood')
 for x in [-3+i*.4 for i in range(16)]:box('Backsplash grout',(x,2.87,2.3),(.008,.01,.7),'paper',.001)
 for z in [2.05,2.4,2.75]:box('Backsplash horizontal grout',(0,2.86,z),(6,.01,.008),'paper',.001)
 # Leak is indicated in post-production; no valve or sabotage instructions modeled.
 anchors.update(home=(0,0,1),risk=(-1.6,2,1.7));camera((10,-14,12),(0,0,1.2),14)
 count=1
 def state(i):pass
else:raise ValueError(K)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.45));finish(bpy.context.object,mat('Backdrop',(.026,.06,.08),0,.95))
for pos,power,size,col in [((-7,-10,15),2400,8,(.78,.88,1)),((6,-3,10),1900,7,(1,.78,.55)),((3,8,12),2600,6,(.4,.65,1))]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
out=P/'frames'/K;out.mkdir(parents=True,exist_ok=True)
bpy.context.view_layer.update();projected={}
for k,v in anchors.items():
 c=world_to_camera_view(S,S.camera,Vector(v));projected[k]=[c.x*1080,(1-c.y)*1920]
if count>1:
 import subprocess
 probes=[0,15,30,45,60]
 for i in probes:
  state(i);S.render.filepath=str(out/f'probe_{i:04d}.jpg');bpy.ops.render.render(write_still=True)
 result=subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'region_cache.py'),'bounds',str(out)],check=True,capture_output=True,text=True);region=json.loads(result.stdout)
 x0,y0,x1,y1=region['box_top_left_pixels'];w,h=region['source_size'];S.render.use_border=True;S.render.use_crop_to_border=True
 S.render.border_min_x=(x0+.1)/w;S.render.border_max_x=min(1,(x1+.1)/w);S.render.border_min_y=min(1,1-y1/h+.1/h);S.render.border_max_y=min(1,1-y0/h+.1/h)
 region['actual_box_top_left_pixels']=[int(S.render.border_min_x*w),h-int(S.render.border_max_y*h),int(S.render.border_max_x*w),h-int(S.render.border_min_y*h)]
 for i in range(count):
  state(i)
  if i not in probes:S.render.filepath=str(out/f'patch_{i:04d}.jpg');bpy.ops.render.render(write_still=True)
 S.render.use_border=False;S.render.use_crop_to_border=False
 (out/'index.json').write_text(json.dumps({'count':count,'anchors':projected,'fps':30,'region':region,'schematic_not_physics_simulation':True}))
 subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'region_cache.py'),'stitch',str(out)],check=True)
else:
 state(0);S.render.filepath=str(out/'0000.jpg');bpy.ops.render.render(write_still=True)
 (out/'index.json').write_text(json.dumps({'count':count,'anchors':projected,'fps':30}))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'{K}.blend'),compress=True)
