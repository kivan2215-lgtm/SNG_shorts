"""Material/light treatment for the V3 explanatory model, authored for this film."""
import bpy,math,os
from mathutils import Vector

def configure(S,M,K):
 if os.environ.get('SNG_DRAFT')=='1':return
 S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=4
 S.eevee.use_raytracing=False
 S.render.image_settings.quality=95
 S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-.25
 S.world.use_nodes=True;bg=S.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.035,.065,.095,1);bg.inputs[1].default_value=.4
 colors={'shell':(.045,.095,.115),'edge':(.30,.40,.43),'floor':(.09,.12,.13),'brass':(.43,.25,.075),'gold':(.68,.40,.10),'water':(.015,.24,.31),'cloth':(.045,.085,.105),'trousers':(.022,.038,.052),'skin':(.48,.29,.18),'hair':(.026,.019,.013),'boot':(.018,.023,.022),'rubber':(.012,.025,.022),'sand':(.035,.065,.07),'rock':(.065,.105,.11),'canvas':(.26,.22,.13),'light':(.8,.62,.29)}
 for name,m in M.items():
  m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
  col=colors.get(name,tuple(m.diffuse_color[:3]));bs.inputs['Base Color'].default_value=(*col,1)
  metal=name in ['edge','brass','gold'];fabric=name in ['cloth','trousers','canvas'];rough=.82 if fabric else .65 if name in ['skin','sand','rock','rubber','boot','floor'] else .35
  bs.inputs['Metallic'].default_value=.80 if metal else .20 if name=='shell' else 0
  bs.inputs['Roughness'].default_value=rough;bs.inputs['Specular IOR Level'].default_value=.25 if fabric or name=='skin' else .45
  if name in ['light','safe','foam']:
   bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=2 if name=='light' else .35
  if fabric or name=='skin':
   tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=165 if fabric else 85 if name=='skin' else 20;tex.inputs['Detail'].default_value=2;tex.inputs['Roughness'].default_value=.65
   ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[0].color=(*(v*.90 for v in col),1);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(*(min(1,v*1.06) for v in col),1)
   nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
   bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.20 if fabric else .12;bump.inputs['Distance'].default_value=.006 if name in ['sand','rock'] else .0015
   nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
  if name=='water':
   bs.inputs['Roughness'].default_value=.18;bs.inputs['IOR'].default_value=1.333;bs.inputs['Alpha'].default_value=.70;m.surface_render_method='BLENDED';bs.inputs['Metallic'].default_value=.10
 # Physically separated key, cool rim and low warm fill: only the key casts
 # deterministic shadows, avoiding temporal noise from soft-shadow sampling.
 wide=K in ['hero','dive','flood','loss','depth','rise','trips','saved','final']
 target=Vector((0,0,3 if K in ['depth','rise','trips','saved','final'] else 1.8))
 scale=1.8 if wide else 1
 lights=[('Key',(-5,-7,8),1500,(.70,.83,1),.3,True),('Warm fill',(5,-5,4),430,(1,.78,.52),4.5,False),('Rim',(3,5,8),2100,(.29,.64,1),3.5,False)]
 for name,pos,power,color,size,shadow in lights:
  bpy.ops.object.light_add(type='AREA',location=tuple(Vector(pos)*scale));o=bpy.context.object;o.name='SNG '+name;o.data.energy=power*scale*scale;o.data.color=color;o.data.shape='DISK';o.data.size=size*scale;o.data.use_shadow=shadow;o.data.use_shadow_jitter=False;o.data.shadow_filter_radius=0
  o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 S.render.film_transparent=False
