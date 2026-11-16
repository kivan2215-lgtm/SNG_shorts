from pathlib import Path
import json,hashlib
P=Path(__file__).parent
ART={'dead':'opening.png','arrival':'scenes1:0','memory':'scenes1:1','clue':'scenes3:0','date':'scenes1:3','kayak':'scenes1:2','wreck':'scenes2:1','declared':'scenes2:1','payout':'scenes3:1','grief':'scenes2:2','return':'scenes2:0','search':'scenes2:3','hiding':'scenes3:2','newlife':'scenes3:3'}
PHOTOS={'missing':'john','staged':'john','photo':'panama','couple':'panama','dated':'panama','contradiction':'panama','website':'panama','knew':'anne','verdict':'anne','sentence':'anne','sons':'sons','believed':'sons','end':'sons','panama':'farm'}
PURPOSE={
'dead':'A presumed-dead man is physically alive; mystery without disclosing the fraud mechanism',
'arrival':'Actually entering police station, not a generic facade',
'memory':'Claimed memory loss, not medical diagnosis',
'clue':'A still-unrevealed photograph; reverse is illustration not documentary scan',
'date':'Geographic/time setup at sea; coastguards are illustrative',
'kayak':'Man paddling red kayak, not merely empty coastline',
'wreck':'Inspecting damaged boat; generic illustration, no false original-evidence caption',
'missing':'Actual John identified as missing, archive capture date unknown',
'declared':'Official death declaration shown separately from disappearance',
'payout':'Receiving correspondence; no fake bank statement or invented amount',
'grief':'Two adult sons grieve, no claim this illustration is actual family photo',
'return':'Reunion contrasts with grief; no photo revelation yet',
'search':'Woman types reported query John Anne Panama into illustrative interface; no fake results or claim of original screenshot',
'photo':'Actual agency photograph first appears precisely when named',
'couple':'Identify only John and Anne; adviser is not accused',
'dated':'Capture date 2006 contrasted with return 2007',
'contradiction':'Still presumed dead during documented 2006 visit',
'staged':'Fraud revealed after viewer sees contradiction',
'hiding':'Distinct approach-to-wardrobe illustration introduces physical hiding',
'visitors':'Whole adjacent-room model, stable spatial anchors',
'passage':'Close view, articulated walk through actual opening into adjoining room',
'knew':'Real Anne photograph after her complicity is stated',
'panama':'Actual John in Panama summer2007; distinct source photograph',
'website':'Return to actual photo for a new fact: agency publication, not fabricated web screenshot',
'verdict':'2008 sentence context, not claim of current incarceration',
'sentence':'Exact term per person, not time actually served',
'sons':'Actual sons are not accomplices; no claim source photo is the earlier reunion',
'newlife':'Anonymous packing scene illustrates a new life, not original evidence',
'believed':'Sons believed father dead; archival faces held for emotional consequence',
'end':'Discussion question about financial and emotional harm, no call to subscribe'}
plan={'episode':36,'case':'John Darwin','status':'preview_pending_user_review','languages':{},'final_qc':{'auditory_review_ru':False,'auditory_review_en':False,'technical':'pending','encoded_frames':'pending'}}
for l in ['ru','en']:
 timeline=json.loads((P/l/'timeline.json').read_text());words=json.loads((P/l/'words.json').read_text());out=[]
 for shot in timeline:
  k=shot['visual'];d=dict(shot);d['narration']=' '.join(w['text'] for w in words if shot['start']-.015<=w['start']<shot['end']-.015)
  d['purpose']=PURPOSE[k];d['asset']=ART.get(k,PHOTOS.get(k,'models/'+('overview' if k=='visitors' else 'passage')))
  d['provenance']='original illustration' if k in ART else 'authentic photograph, source metadata in assets.json' if k in PHOTOS else 'original schematic 3D, based on reported connection, dimensions not measured'
  d['camera']='fixed; no routine zoom/pan';d['movement']='native 30fps articulated walking with foot contact' if k=='passage' else 'sequential explanatory timeline/labels or typing' if k in ['dated','contradiction','couple','sentence','search'] else 'static meaningful shot'
  d['early_reveal_guard']='Do not show Panama photo until photo cue, nor wardrobe before hiding cue';d['manual_frame_review']='pending';out.append(d)
 plan['languages'][l]=out
(P/'shot_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
manifest={'episode':36,'status':'preview_pending_user_review','files':{}}
for f in list(P.glob('*.py'))+list((P/'assets').glob('*'))+[P/l/'narration.txt' for l in ['ru','en']]:
 if f.is_file():manifest['files'][str(f.relative_to(P))]=hashlib.sha256(f.read_bytes()).hexdigest()
(P/'render_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Saved phrase-level plan and source hashes')
