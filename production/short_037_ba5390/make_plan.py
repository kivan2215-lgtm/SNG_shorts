from pathlib import Path
import json
P=Path(__file__).parent
assets={
'hold':'opening.png','outside':'scenes1.png:0','height':'scenes2.png:0','grip':'scenes1.png:3','braced':'scenes3.png:3','date':'aircraft.jpg','normal':'scenes3.png:1','blow':'3D window','ejected':'scenes1.png:0','grab':'opening.png','help':'scenes1.png:1','copilot':'scenes1.png:2','airport':'scenes3.png:2','radio':'scenes3.png:0','numb':'numb.png','believed':'scenes3.png:3','holding':'scenes1.png:1','kick':'kick.png','alive':'kick.png','duration':'scenes1.png:0','landing':'scenes2.png:2','survived':'crew.jpg','why':'3D window','evidence':'appendix-19.jpg','repair':'scenes2.png:3','ninety':'3D window','thin':'3D bolts','difference':'3D bolts','short':'3D bolts','pressure':'3D window','report':'report.jpg','oversight':'report.jpg','stakes':'crew.jpg','mechanic':'scenes2.png:3','end':'captain.jpg'}
purpose={
'hold':'Immediate physical predicament, attendant holds legs through front windshield; no survival spoiler.',
'outside':'Exterior view establishes torso outside and orientation, not a passenger window.',
'height':'Whole aircraft and actual approximate pressure altitude at failure; no invented live instrument reading.',
'grip':'Close view of actual holding action in illustration; inability to pull inward.',
'braced':'A different profile view shows body braced, not just generic cockpit.',
'date':'Real G-BJRT before event; on-screen 1989 image date separate from10June1990 event date.',
'normal':'Ordinary meal-service context; no impending danger before spoken failure.',
'blow':'Externally mounted panel moves outward, fixed frame remains; no wrong-bolt explanation yet.',
'ejected':'Captain position; repeated exterior now identifies his role/name.',
'grab':'Previously shown grip returns to explain the rescue action in chronology.',
'help':'Another person physically braces the attendant; no invented named participant portrait.',
'copilot':'Right-seat copilot physically controls yoke during descent.',
'airport':'Illustrative ground coordination, not claimed authentic controller portrait.',
'radio':'Analog radio closeup supports wind/noise obstacle; no fake recorded radio speech.',
'numb':'Hands return to explain endurance/physical obstacle.',
'believed':'AAIB describes crew considering survival highly improbable, not actual death.',
'holding':'Crew continues supporting one another, not released body.',
'kick':'Distinct illustration of feet and retained grip; not authentic video.',
'alive':'Same grip context gains new meaning, no future hospital photo until landing.',
'duration':'Return to outside context adds approximately20min duration, not countdown.',
'landing':'Illustrative BACOneEleven landing, gear and runway visible.',
'survived':'Actual crew hospital photograph only AFTER landing;87onboard0fatalities.',
'why':'Empty opening model after the survival payoff, prepares technical mystery.',
'evidence':'Original AAIB AppendixE photograph, not generated forensic evidence.',
'repair':'Generic illustrative mechanic/fasteners, not a portrait accusing an actual person.',
'ninety':'Whole frame with ninety perimeter fasteners, geometric positions schematic.',
'thin':'Three enlarged physical models; nominal diameter difference, specimen comparison.',
'difference':'0.66mm dimension highlight, no invented exact defect location.',
'short':'Separate six short bolts;2.54mm length difference, not same diameter fault.',
'pressure':'Same assembly now explains cause with inside/outside arrows, not physics simulation.',
'report':'Actual AAIB findings page, publication1992.',
'oversight':'Independent inspection finding translated in separate overlay, not edited original quote.',
'stakes':'Actual rescued crew photograph returns with new accountability context.',
'mechanic':'Anonymous mechanic illustration returns as a question, not identification/scapegoating.',
'end':'Actual Lancaster later return-to-flying photograph labelled by period; discussion not invented verdict.'}
langs={}
for lang in ['ru','en']:
 words=json.loads((P/lang/'words.json').read_text());rows=[]
 for s in json.loads((P/lang/'timeline.json').read_text()):
  k=s['visual'];a=assets[k];source='original illustrative scene' if '.png' in a else ('original schematic3D' if a.startswith('3D') else 'authentic archival photograph/document; SOURCES.md')
  s.update(narration=' '.join(w['text'] for w in words if s['start']-.04<=w['start']<s['end']-.04),asset=a,provenance=source,purpose=purpose[k],camera='fixed; no routine pan/zoom',before_after=purpose[k],question=purpose[k].split(';')[0],early_reveal_guard='No survival before kick/alive; no hospital until after landing; no bolt cause before evidence phase.',movement='native30fps state change with ease-in/out and hold' if k in ['blow','pressure','thin','difference','short'] else 'meaningful static illustration/archive or timed label',audio_accent='restrained original score, lower at survival and technical question',manual_frame_review='preflight sampled; encoded review pending')
  rows.append(s)
 langs[lang]=rows
(P/'shot_plan.json').write_text(json.dumps({'episode':37,'case':'BA5390','status':'preview_pending_user_review','languages':langs,'final_qc':{'technical':'pending','encoded_frames':'pending','auditory_review_ru':False,'auditory_review_en':False}},ensure_ascii=False,indent=2))
