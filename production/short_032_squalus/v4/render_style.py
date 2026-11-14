"""V4 materials with restrained wear, indirect light and physically soft shadows."""
import bpy, math, os
from mathutils import Vector

def configure(S,M,K):
 if os.environ.get('SNG_DRAFT')=='1':return
 S.render.engine='CYCLES';S.render.use_persistent_data=True;S.cycles.device='CPU';S.cycles.samples=int(os.environ.get('SNG_SAMPLES','12'))
 S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.08
 S.cycles.use_denoising=True;S.cycles.denoiser='OPENIMAGEDENOISE'
 S.cycles.max_bounces=4;S.cycles.diffuse_bounces=2;S.cycles.glossy_bounces=2;S.cycles.transmission_bounces=3;S.cycles.transparent_max_bounces=6
 S.render.image_settings.quality=97
 S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.05
 S.world.use_nodes=True;bg=S.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.045,.065,.085,1);bg.inputs[1].default_value=.35
 colors={'shell':(.075,.13,.14),'edge':(.29,.33,.32),'floor':(.07,.085,.08),'brass':(.32,.20,.075),'gold':(.48,.30,.09),'water':(.018,.18,.23),'cloth':(.07,.12,.155),'trousers':(.035,.05,.06),'skin':(.43,.24,.14),'hair':(.03,.025,.019),'boot':(.024,.018,.012),'rubber':(.014,.018,.018),'sand':(.055,.07,.065),'rock':(.09,.105,.09),'canvas':(.27,.22,.145),'light':(.95,.79,.47),'ivory':(.55,.53,.42),'glass':(.10,.16,.17)}
 for name,m in M.items():
  m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
  col=colors.get(name,tuple(m.diffuse_color[:3]));bs.inputs['Base Color'].default_value=(*col,1)
  metal=name in ['edge','brass','gold'];fabric=name in ['cloth','trousers','canvas'];paint=name=='shell'
  rough=.87 if fabric else .57 if name in ['skin','sand','rock','rubber','boot','floor'] else .38
  bs.inputs['Metallic'].default_value=.83 if metal else .25 if paint else 0
  bs.inputs['Roughness'].default_value=rough;bs.inputs['Specular IOR Level'].default_value=.22 if fabric else .35
  if name=='skin':bs.inputs['Subsurface Weight'].default_value=.08;bs.inputs['Subsurface Radius'].default_value=(.5,.22,.12)
  if name in ['light','safe','foam']:
   bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=2.3 if name=='light' else .2
  if name not in ['water','light','safe','danger','foam','eyewhite','iris']:
   tc=nt.nodes.new('ShaderNodeTexCoord');tex=nt.nodes.new('ShaderNodeTexNoise');nt.links.new(tc.outputs['Object'],tex.inputs['Vector'])
   tex.inputs['Scale'].default_value=180 if fabric else 90 if name=='skin' else 18 if metal or paint else 25
   tex.inputs['Detail'].default_value=2.5;tex.inputs['Roughness'].default_value=.65
   ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[0].color=(*(v*.73 for v in col),1);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(*(min(1,v*1.12) for v in col),1)
   nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
   bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17 if fabric else .12;bump.inputs['Distance'].default_value=.0012 if fabric or name=='skin' else .003 if metal or paint else .018
   nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
   remap=nt.nodes.new('ShaderNodeMapRange');remap.inputs['To Min'].default_value=max(.1,rough-.08);remap.inputs['To Max'].default_value=min(1,rough+.13);nt.links.new(tex.outputs['Fac'],remap.inputs['Value']);nt.links.new(remap.outputs['Result'],bs.inputs['Roughness'])
  if name=='water':
   bs.inputs['Roughness'].default_value=.13;bs.inputs['IOR'].default_value=1.333;bs.inputs['Transmission Weight'].default_value=.5
   # Transparent cutaway water remains readable without an opaque plastic disk.
   tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.68;nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(bs.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
 wide=K in ['hero','dive','flood','loss','depth','rise','trips','saved','final'];scale=1.8 if wide else 1
 target=Vector((0,0,3 if K in ['depth','rise','trips','saved','final'] else 1.8))
 lights=[('Soft key',(-5,-6,9),1900,(.77,.87,1),5),('Warm fill',(5,-5,5),750,(1,.84,.66),5),('Ocean rim',(2,5,8),2300,(.35,.68,.83),4)]
 for name,pos,power,color,size in lights:
  bpy.ops.object.light_add(type='AREA',location=tuple(Vector(pos)*scale));o=bpy.context.object;o.name='SNG '+name;o.data.energy=power*scale*scale;o.data.color=color;o.data.shape='DISK';o.data.size=size*scale
  o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 # Warm practical illumination in the occupied chamber, parented to its motion.
 if K in ['dock','seal','drain','dry','open','transfer']:
  root=bpy.data.objects.get('McCann chamber')
  if root:
   bpy.ops.object.light_add(type='AREA',location=(-.5,.6,4.6));o=bpy.context.object;o.name='Cabin practical';o.parent=root;o.data.energy=60;o.data.color=(1,.78,.50);o.data.size=.65
   o.rotation_euler=(Vector((0,-.2,3))-o.location).to_track_quat('-Z','Y').to_euler()
 if K in ['question','cable','dock','seal','drain','dry','open','transfer']:
  for x in [-2.7,2.7]:
   bpy.ops.object.light_add(type='AREA',location=(x,-.5,-.20));o=bpy.context.object;o.name='Lower cabin practical';o.data.energy=18;o.data.color=(1,.80,.56);o.data.size=.7
   o.rotation_euler=(Vector((x,-.7,-1.4))-o.location).to_track_quat('-Z','Y').to_euler()
 S.render.film_transparent=False
