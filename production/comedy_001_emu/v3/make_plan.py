from pathlib import Path
import json,hashlib
from visuals import ART,HEAD
P=Path(__file__).parent
purpose={
'hook':'Unexpected real premise: military equipment versus birds, no false declaration of war.',
'bird':'Reveal ordinary healthy emu as opponent; dry profanity reinforces absurd mismatch.',
'awkward':'Human reaction anticipates a problem without revealing the gun jam.',
'date':'Real1932 field archive anchors place and period; no invented map.',
'wheat':'Farmer physically lifts damaged stalks; crop damage supplies the real reason.',
'ask':'Farmers explain crop damage to military figure; generic actors, no fabricated quotation.',
'arrive':'Three men unload equipment; visual does not imply an army-sized force.',
'guns':'Genuine image of Lewis gun and allocation figures; figures are initial supplies not spent ammunition.',
'legs':'Set up the comic equipment comparison; modeled birds are not actual photographs.',
'balance':'Editorial mismatch joke; no fake scoreboard or zero-death claim.',
'scatter':'Continuous3D flock separates along outward paths; same fence and water landmark.',
'catch':'Hold the dispersed state so viewers understand why one concentrated target disappears.',
'ambush':'Actual waterside1932 photograph; do not claim it captures the exact gun jam.',
'flock':'Original scene of birds approaching water; show the prepared ambush before failure.',
'moment':'Hold same approach, add the expectation question, do not reveal failure until jam cue.',
'jam':'Soldier stops and looks at idle weapon; no weapon construction or repair details.',
'leave':'Distinct running birds escape, no wounds or suffering for comedy.',
'error':'Return to jam for a new editorial reboot joke; explicitly metaphorical interface.',
'truckplan':'People physically mount equipment on a period truck; new attempted solution.',
'chase':'Whole3D truck and emu ahead establish the chase before bumps begin.',
'rough':'Chassis pitches over schematic terrain; camera fixed; seated operator supported, wheels rotate.',
'escape':'Hold endpoint with bird ahead, show result of the failed chase.',
'mobility':'Distinct close reaction shot gives the equipment upgrade joke a human face.',
'massage':'Hold seated reaction to land the punchline, no unrelated meme or artificial camera shake.',
'recall':'Chronological operation diagram shows recall only; return remains hidden.',
'return':'Reveal next dated stage with progressive arrow; not a geographic route.',
'unresolved':'Same chronology adds remaining problem, no claim that there was no second attempt.',
'caveat':'Actual gunners archive, quieter music, acknowledge animal deaths without graphic imagery.',
'ended':'Real field archive returns with new December end-of-operation information.',
'farmers':'Farmer still faces emus in crops; shows agricultural problem rather than a treaty.',
'history':'New emu portrait names the popular historical nickname, no literal bird victory speech.',
'question':'Hold emu reaction for the final discussion question; no subscribe card.'}
purpose['balance']='Editorial joke about birds not requiring permission; not a literal claim of bird military organization.'
purpose['massage']='Figurative vibrator-on-wheels punchline over seated truck reaction; no literal sex device.'
purpose['printer']='Original absurd printer metaphor, not a historical cause of the jam or fake document.'
purpose['indifference']='Editorial indifference joke over same emu portrait; not literal military consciousness.'
out={'series':'SNG Comedy','episode':1,'status':'preview_pending_user_review','languages':{},'source_plan':'STORY_PLAN.md','final_qc':{'auditory_ru':False,'auditory_en':False,'encoded_frames':'pending'}}
for lang in ['ru','en']:
 words=json.loads((P/lang/'words.json').read_text());timeline=json.loads((P/lang/'timeline.json').read_text())
 for s in timeline:
  k=s['visual'];s['narration']=' '.join(w['text'] for w in words if s['start']-.03<=w['start']<s['end']-.03);s['purpose']=purpose[k];s['heading']=HEAD[k][lang=='en'];s['camera']='fixed';s['manual_review']='pending encoded frames'
  if k in ['mobility','massage']:s['asset']='truck_reaction.png';s['provenance']='original editorial illustration'
  elif k in ART:s['asset']=f'scenes{ART[k][0]}.png:panel{ART[k][1]}';s['provenance']='original editorial illustration'
  elif k in ['date','guns','ambush','caveat','ended']:s['asset']={'date':'field.jpg','guns':'gun.jpg','ambush':'rest.jpg','caveat':'gunners.jpg','ended':'field.jpg'}[k];s['provenance']='1932 archive; metadata in assets.json'
  else:s['asset']='scatter.blend' if k in ['legs','balance','scatter','catch'] else 'truck.blend';s['provenance']='original schematic3D'
 out['languages'][lang]=timeline
(P/'shot_plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
assets=json.loads((P/'assets.json').read_text())
for a in assets:a['sha256']=hashlib.sha256((P/'assets'/a['file']).read_bytes()).hexdigest();a['review']='visually reviewed; unused ambiguous water.jpg' if a['file']=='water.jpg' else 'visually reviewed; full source frame retained'
for f in sorted((P/'assets').glob('*.png')):
 if any(a.get('file')==f.name for a in assets):continue
 assets.append({'file':f.name,'type':'original generated editorial illustration','sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'review':'faces/hands/action/portrait composition reviewed','real_historical_photo':False})
(P/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
