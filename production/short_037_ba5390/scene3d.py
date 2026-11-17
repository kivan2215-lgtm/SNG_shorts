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

# Precision-style schematic. Dimensions/positions are illustrative, not a CAD repair drawing.
M['glass'].node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.28
M['glass'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.025,.17,.23,1)
M['gasket']=mat('Black rubber seal',(.018,.025,.025),0,.88)
M['lightsteel']=mat('Satin machined aluminium',(.48,.58,.62),.72,.3)
M['orange']=mat('Warm comparison accent',(.72,.22,.035),.45,.34)
M['blue']=mat('Blue comparison accent',(.035,.30,.40),.55,.32)
def empty(n):
 o=bpy.data.objects.new(n,None);S.collection.objects.link(o);return o
def mesh(n,vs,fs,m,bevel=.025):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);S.collection.objects.link(o);finish(o,m)
 if bevel:b=o.modifiers.new('Rounded edges','BEVEL');b.width=bevel;b.segments=3
 return o
def ring(n,outer,inner,z,thick,m):
 vs=[(x,y,zz) for zz in [z,z+thick] for pts in [outer,inner] for x,y in pts];fs=[];N=len(outer)
 for i in range(N):
  j=(i+1)%N;fs.extend([(i,j,j+N,i+N),(i+2*N,i+3*N,j+3*N,j+2*N),(i,i+2*N,j+2*N,j),(i+N,j+N,j+3*N,i+3*N)])
 return mesh(n,vs,fs,m)
def poly(n,pts,z,thick,m):
 N=len(pts);vs=[(x,y,zz) for zz in [z,z+thick] for x,y in pts];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];return mesh(n,vs,fs,m)
def bolt(n,l,r,length,material='steel',detailed=True):
 parent=empty(n);parent.location=l
 shaft=rod(n+' shank',(0,0,0),(0,0,length),r*.87,material);shaft.parent=parent
 # Round countersunk head with real cross recess, no flat capped cylinder placeholder.
 bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=r,radius2=r*1.8,depth=r*.65,location=(0,0,length+r*.325));o=bpy.context.object;finish(o,material);o.parent=parent
 for ang in [0,math.pi/2]:
  ob=box('Recess',(0,0,length+r*.65+.001),(r*2.5,r*.23,.016),'dark',.005);ob.rotation_euler.z=ang;ob.parent=parent
 if detailed:
  pts=[];turns=15
  for i in range(361):
   t=i/360;theta=t*turns*2*math.pi;pts.append((r*math.cos(theta),r*math.sin(theta),.06+t*(length-.10)))
  ob=curve('Continuous helical thread',pts,r*.09,material);ob.parent=parent
 return parent
count=37 if K=='window' else 61
if K=='window':
 outer=[(-2.65,-1.95),(2.65,-1.95),(2.22,2.0),(-1.9,2.0)]
 inner=[(-1.95,-1.24),(1.95,-1.24),(1.58,1.32),(-1.38,1.32)]
 middle=[(-2.30,-1.60),(2.30,-1.60),(1.90,1.66),(-1.64,1.66)]
 ring('Fuselage mounting surround',outer,inner,.5,.22,'ivory')
 ring('Inside structural flange',middle,inner,.36,.13,'lightsteel')
 panel=empty('Externally mounted windscreen assembly')
 ob=ring('Laminated panel edge',middle,inner,.74,.13,'steel');ob.parent=panel
 ob=ring('Rubber edge seal',[(x*.98,y*.98) for x,y in middle],[(x*1.01,y*1.01) for x,y in inner],.72,.035,'gasket');ob.parent=panel
 ob=poly('Blue laminated glazing',inner,.77,.10,'glass');ob.parent=panel
 # Ninety fasteners, simplified positions not the exact historical arrangement.
 boltloc=[]
 for a,b,n in zip(middle,middle[1:]+middle[:1],[25,20,25,20]):
  for i in range(n):
   q=(i+.5)/n;boltloc.append((a[0]*(1-q)+b[0]*q,a[1]*(1-q)+b[1]*q))
 for j,(x,y) in enumerate(boltloc):
  bo=bolt('Fastener %02d'%j,(x,y,.52),.047,.35,'steel',False);bo.parent=panel
  rod('Anchor nut',(x,y,.32),(x,y,.42),.082,'dark')
 # Aft metallic ribs and material contrast give readable depth.
 for x in [-2.5,2.5]:box('Mounting rib',(x,0,.22),(.13,3.4,.32),'lightsteel',.025)
 arrows=[]
 for x in [-.9,0,.9]:
  a=empty('Outward cabin pressure');ob=rod('Force shaft',(x,-.2,-.35),(x,-.2,.40),.038,'cyan');ob.parent=a
  bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.13,radius2=0,depth=.25,location=(x,-.2,.525));ob=bpy.context.object;finish(ob,'cyan');ob.parent=a;arrows.append(a)
 camera((7,-10,14),(0,0,1.05),12.6)
 anchors={'panel':(0,.1,1.0),'surround':(2.35,-1.5,.65),'inside':(-1.5,-2.2,.2),'outside':(0,1.8,2.0),'bolts':(-2.25,-1.55,.9)}
 def state(i):
  t=i/36;u=max(0,min(1,(t-.2)/.65));u=u*u*(3-2*u);panel.location.z=u*1.8
  for ob in arrows:ob.scale.z=.15+.85*min(1,t*3)
else:
 # Same head elevation permits a direct diameter/length comparison.
 specs=[(-1.55,.2413,2.032,'blue'),(0,.2083,2.032,'orange'),(1.55,.2413,1.778,'gold')]
 roots=[]
 for x,r,L,matname in specs:
  ob=bolt('Comparison bolt',(x,0,.5+2.032-L),r,L,matname,True);roots.append(ob)
  box('Comparison pedestal',(x,0,.15),(1.23,1.4,.3),'dark',.08)
 # Physical reference bar shows equal head level and the short bolt end gap.
 box('Baseline',(0,.38,.50),(4.55,.045,.035),'ivory',.005)
 box('Top alignment',(0,.38,2.69),(4.55,.045,.035),'ivory',.005)
 camera((0,-14,5),(0,0,1.55),8.9)
 anchors={'correct':(-1.55,0,1.4),'thin':(0,0,1.4),'short':(1.55,0,1.4),'shortend':(1.55,0,.754),'thinhead':(0,0,2.65)}
 def state(i):
  t=i/60;u=t*t*(3-2*t)
  # One gentle quarter-turn reveals actual helical threads and head recesses.
  for ob in roots:ob.rotation_euler.z=.7*u
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
 probes=sorted(set([0,(count-1)//4,(count-1)//2,3*(count-1)//4,count-1]))
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
