from pathlib import Path
import shutil,json
P=Path(__file__).resolve().parents[1];R=Path('/workspace/sng-publish');D=R/'production/short_032_squalus'
for sub in ['v4/models','v4/human']:(D/sub).mkdir(parents=True,exist_ok=True)
for n in ['README.md','SOURCES.md','visuals_v4.py','build_v4.py','qc_v4.py','metadata.json','metadata.txt']:shutil.copy2(P/n,D/n)
for n in ['scene3d.py','human_model.py','render_style.py','render_all.py','region_cache.py','check_motion.py','motion_QC.json','PLAN.md','MECHANISM_CHECKS.md','render_manifest.json','QC.json','revision_manifest.json','package_revision.py','verify_delivery.py','check_preservation.py']:shutil.copy2(P/'v4'/n,D/'v4'/n)
for n in ['base.obj','default.mhskel','default_weights.mhw','male.target','average.target','LICENSE.md','LICENSE.ASSETS.md','ASSET_MANIFEST.json']:shutil.copy2(P/'v4/human'/n,D/'v4/human'/n)
for k in ['flood','seal','transfer']:shutil.copy2(P/'v4/models'/f'{k}.blend',D/'v4/models'/f'{k}.blend')
for lang in ['ru','en']:
 dest=D/lang/'v4';dest.mkdir(parents=True,exist_ok=True);f=P/lang/f'SNG_032_Squalus_{lang.upper()}_PREVIEW_V4.mp4'
 qc=json.loads((P/lang/'v4/QC.json').read_text());assert not qc['failures'] and qc['encoded_frame_review']=='reviewed'
 shutil.copy2(f,R/f.name)
 for src in (P/lang/'v4').glob('*.jpg'):
  if not src.name.startswith('frame_'):shutil.copy2(src,dest/src.name)
 shutil.copy2(P/lang/'v4/QC.json',dest/'QC.json')
for name in ['00_MASTER_SETTINGS.md','04_DIAGRAMS_AND_VISUALS.md','09_MODELED_GRAPHICS_STANDARD.md']:
 shutil.copy2(P.parents[1]/'production/SNG_SHORTS_PLAYBOOK'/name,R/'production/SNG_SHORTS_PLAYBOOK'/name)
print('Packaged reviewed V4')
