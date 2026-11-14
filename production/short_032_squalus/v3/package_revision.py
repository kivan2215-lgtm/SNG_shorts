"""Stage reviewed V3 deliverables and reproducible sources; no reference footage."""
from pathlib import Path
import shutil,json
P=Path(__file__).resolve().parents[1];R=Path('/workspace/sng-publish');D=R/'production/short_032_squalus'
(D/'v3/models').mkdir(parents=True,exist_ok=True);(D/'v3/human').mkdir(exist_ok=True)
for n in ['README.md','SOURCES.md','visuals_v3.py','build_v3.py','qc_v3.py','metadata.json','metadata.txt']:shutil.copy2(P/n,D/n)
for n in ['scene3d.py','human_model.py','render_style.py','render_all.py','PLAN.md','MECHANISM_CHECKS.md','render_manifest.json','QC.json','revision_manifest.json','package_revision.py','verify_delivery.py','check_preservation.py']:shutil.copy2(P/'v3'/n,D/'v3'/n)
for n in ['base.obj','default.mhskel','default_weights.mhw','male.target','average.target','LICENSE.md','LICENSE.ASSETS.md','ASSET_MANIFEST.json']:shutil.copy2(P/'v3/human'/n,D/'v3/human'/n)
for k in ['flood','open','transfer']:shutil.copy2(P/'v3/models'/f'{k}.blend',D/'v3/models'/f'{k}.blend')
for lang in ['ru','en']:
 dest=D/lang/'v3';dest.mkdir(parents=True,exist_ok=True);f=P/lang/f'SNG_032_Squalus_{lang.upper()}_PREVIEW_V3.mp4'
 qc=json.loads((P/lang/'v3/QC.json').read_text());assert not qc['failures'] and qc['encoded_frame_review']=='reviewed'
 shutil.copy2(f,R/f.name)
 for src in (P/lang/'v3').glob('*.jpg'):
  if not src.name.startswith('frame_'):shutil.copy2(src,dest/src.name)
 shutil.copy2(P/lang/'v3/QC.json',dest/'QC.json')
shutil.copy2(P.parents[1]/'production/SNG_SHORTS_PLAYBOOK/09_MODELED_GRAPHICS_STANDARD.md',R/'production/SNG_SHORTS_PLAYBOOK/09_MODELED_GRAPHICS_STANDARD.md')
print('Staged reviewed V3')
