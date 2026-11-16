"""Topic-specific explanatory models, not actual evidence or medical instructions."""
import bpy,math,sys,json,random,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).parent;K=sys.argv[sys.argv.index('--')+1]
sys.path.insert(0,str(P))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True;S.cycles.max_bounces=4
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

# Schematic adjacent rooms, not a measured historical floor plan.
M['cloth']=mat('Wool navy jumper',(.045,.09,.13),0,.9)
M['trousers']=mat('Grey trousers',(.11,.12,.12),0,.9)
M['wall']=mat('Warm plaster',(.68,.62,.49),0,.9)
M['linen']=mat('Linen',(.24,.40,.42),0,.95)
textured('wood',(.06,.025,.012),(.28,.14,.065),4,.013)
textured('wall',(.45,.41,.33),(.72,.67,.54),35,.006)
box('Base',(0,0,-.14),(6.3,7.2,.28),'dark')
box('Floor family',(0,-1.8,.035),(6.1,3.5,.07),'wood')
box('Floor bedsit',(0,1.8,.035),(6.1,3.5,.07),'paper')
# Three outer cutaway walls, softened corners, skirting and a full actual doorway.
box('Back wall',(0,3.6,1.45),(6.3,.16,2.9),'wall')
box('Left side',(-3.1,0,1.45),(.16,7.2,2.9),'wall')
for x in [-1.95,1.95]:box('Shared wall',(x,0,1.45),(2.3,.18,2.9),'wall')
box('Door lintel',(0,0,2.6),(1.6,.18,.6),'wall')
for x in [-.76,.76]:box('Door jamb',(x,-.08,1.17),(.08,.25,2.3),'wood')
box('Door frame top',(0,-.08,2.30),(1.6,.25,.09),'wood')
for x in [-2.2,2.2]:box('Wall baseboard',(x,-.12,.15),(1.7,.07,.16),'ivory')
# Open wardrobe located immediately in front of the concealed wall opening.
for x in [-.95,.95]:box('Wardrobe side',(x,-.40,1.2),(.15,.75,2.4),'wood')
box('Wardrobe roof',(0,-.40,2.4),(2.05,.75,.12),'wood')
box('Wardrobe plinth',(0,-.40,.10),(2.05,.75,.1),'wood')
# Open doors remain visibly connected to hinges, leaving a 1.4m clear passage.
for sgn in [-1,1]:
 hinge=empty('Wardrobe door hinge',(.98*sgn,-.80,0));door=box('Open paneled wardrobe door',(-sgn*.48,0,1.22),(.94,.07,2.25),'wood');door.parent=hinge
 for z in [.68,1.73]:
  panel=box('Recessed panel',(-sgn*.48,-.05,z),(.72,.04,.83),'paper',.025);panel.parent=hinge
 handle=rod('Brass door handle',(-sgn*.82,-.09,1.05),(-sgn*.82,-.09,1.25),.018,'gold');handle.parent=hinge
 hinge.rotation_euler.z=sgn*math.radians(110)
# Bedsit bed and tiny work area clearly distinguish the destination room.
box('Bed base',(1.8,2.15,.35),(1.45,2.4,.42),'wood')
box('Mattress',(1.8,2.15,.64),(1.42,2.34,.22),'ivory',.11)
box('Bed blanket',(1.8,1.9,.79),(1.43,1.8,.10),'linen',.08)
box('Pillow',(1.8,3,.83),(1.1,.45,.13),'paper',.12)
box('Headboard',(1.8,3.37,.72),(1.55,.12,1.35),'wood')
box('Desk',(-1.85,2.65,.84),(1.8,.85,.12),'wood')
for x in [-2.55,-1.15]:
 for y in [2.35,2.95]:rod('Desk leg',(x,y,.08),(x,y,.82),.035,'steel')
box('Closed book',(-1.65,2.7,.96),(.55,.36,.07),'blue')
rod('Desk lamp base',(-2.4,2.7,.9),(-2.4,2.7,.95),.15,'steel');rod('Desk lamp stem',(-2.4,2.7,.94),(-2.4,2.7,1.25),.02,'steel');sphere('Lamp shade',(-2.4,2.7,1.3),(.18,.18,.12),'ivory')
box('Window',(0,3.48,1.8),(1.4,.06,1.2),'blue')
for x in [-.7,0,.7]:box('Window mullion',(x,3.42,1.8),(.05,.07,1.2),'ivory')
box('Window crossbar',(0,3.41,1.8),(1.4,.07,.05),'ivory')
# Family living area: upholstered sofa, floor lamp, table and rug.
box('Woven rug',(0,-2.65,.085),(4.4,1.5,.025),'linen',.03)
box('Sofa seat',(-2.20,-2,.50),(1.1,2.5,.32),'blue',.14)
box('Sofa back',(-2.7,-2,.9),(.26,2.65,1.1),'blue',.12)
for y in [-3.2,-.8]:box('Sofa arm',(-2.2,y,.7),(1.05,.25,.65),'blue',.12)
for y in [-2.75,-1.85,-1.0]:box('Sofa cushion',(-2.1,y,.72),(.85,.70,.15),'linen',.11)
box('Coffee table',(1.25,-2.4,.54),(1.5,1,.10),'wood')
for x in [.65,1.85]:
 for y in [-2.75,-2.05]:rod('Table leg',(x,y,.08),(x,y,.52),.035,'steel')
rod('Mug',(1.4,-2.5,.60),(1.4,-2.5,.77),.07,'ivory')
box('Magazine without text',(.95,-2.4,.62),(.43,.55,.025),'paper',.01)
rod('Floor lamp',(2.7,-.8,.08),(2.7,-.8,1.9),.025,'steel');sphere('Lampshade',(2.7,-.8,1.95),(.3,.3,.22),'ivory')
import human_model
root=human_model.create('Anonymous man',(0,-1.2,.08),M,empty,uv,None,None,pose='stand');root.rotation_euler.z=math.pi
st=human_model.PEOPLE[int(root['human_index'])]
camera((7,-17,24),(0,0,1),16.2) if K=='overview' else camera((5,-17,23),(0,.4,1.0),10.8)
anchors.update(wardrobe=(0,-.7,2.4),passage=(0,0,1.3),family=(1.5,-2.8,.1),bedsit=(1.5,2,.8))
count=1 if K=='overview' else 91
# World-contact foot targets: one foot moves, the supporting foot stays planted.
def state(i):
 p=i/90
 def smooth(u):u=max(0,min(1,u));return u*u*u*(u*(u*6-15)+10)
 feet={'L':[-1.2,.18],'R':[-1.2,.18]}
 for j,side in enumerate(['L','R','L','R','L','R']):
  a=j/6;b=(j+1)/6
  if p<a:continue
  u=min(1,(p-a)/(b-a));old=feet[side][0];target=-1.2+.60*(j+1)
  feet[side]=[old+(target-old)*smooth(u),.18+.11*math.sin(math.pi*u)**2]
 def ground(y):return .08+.07*smooth((y+.9)/.12)*(1-smooth((y-.0)/.12))
 root.location.y=(feet['L'][0]+feet['R'][0])/2
 root.location.z=(ground(feet['L'][0])+ground(feet['R'][0]))/2+.012*math.sin(p*6*math.pi)**2
 for side,sgn in [('L',1),('R',-1)]:
  y,z=feet[side];z+=ground(y)-.08;st['targets']['leg'+side].location=(sgn*.13,root.location.y-y,z-root.location.z)
  st['targets']['arm'+side].location=(sgn*.24,-.03+sgn*.10*math.sin(p*6*math.pi),.88)
  q=st['targets']['leg'+side].location;st['boots'][side].location=(q.x,q.y-.055,q.z-.035)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.45));finish(bpy.context.object,mat('Backdrop',(.026,.06,.08),0,.95))
for pos,power,size,col in [((-7,-10,15),2400,8,(.78,.88,1)),((6,-3,10),1900,7,(1,.78,.55)),((3,8,12),2600,6,(.4,.65,1))]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
out=P/'frames'/K;out.mkdir(parents=True,exist_ok=True)
probe_key=hashlib.sha256(Path(__file__).read_bytes()+(P/'human_model.py').read_bytes()).hexdigest()
probe_key_file=out/'probe_source.sha256'
if '--reuse-probes' in sys.argv and (not probe_key_file.exists() or probe_key_file.read_text()!=probe_key):raise RuntimeError('Probe cache differs from scene source. Render --probes again.')
bpy.context.view_layer.update();projected={}
for k,v in anchors.items():
 c=world_to_camera_view(S,S.camera,Vector(v));projected[k]=[c.x*1080,(1-c.y)*1920]
if count>1:
 import subprocess
 probes=[0,22,45,68,90]
 for i in probes:
  if '--reuse-probes' in sys.argv and (out/f'probe_{i:04d}.jpg').exists():continue
  state(i);S.render.filepath=str(out/f'probe_{i:04d}.jpg');bpy.ops.render.render(write_still=True)
 probe_key_file.write_text(probe_key)
 if '--probes' in sys.argv:
  (out/'anchors.json').write_text(json.dumps(projected));bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'{K}.blend'),compress=True);sys.exit(0)
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
