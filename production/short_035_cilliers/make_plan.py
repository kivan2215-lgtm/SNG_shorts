from pathlib import Path
import json
from visuals import N
p=Path(__file__).parent
langs=['ru','en'];timelines={l:json.loads((p/l/'timeline.json').read_text()) for l in langs};words={l:json.loads((p/l/'words.json').read_text()) for l in langs}
art={'fall':'scenes1:0','reserve':'scenes3_fixed:0','hook':'scenes3:1','date':'scenes1:2','gift':'scenes1:1','field':'scenes1:3','rescue':'scenes2:3','accident':'scenes2:0','strange':'scenes2:1','question':'scenes3:2','truth':'scenes2:2','arranged':'scenes1:1','verdict':'scenes2:2','minimum':'scenes2:2'}
archive={'victoria':'victoria','alive':'victoria','survived':'victoria','end':'victoria','husband':'couple','betrayal':'couple','emile':'emile','motive':'emile','insurance':'emile','failed':'parachute','evidence':'parachute','both':'parachute','sabotage':'parachute'}
beats=[]
for i,row in enumerate(timelines['ru']):
 k=row['visual'];asset=art.get(k,archive.get(k,'descent' if k=='height' else 'house'));kind='reconstruction' if k in art else 'archive' if k in archive else 'diagram'
 b={'id':f'B{i+1:03}','visual':k,'narration':{},'timing':{},'viewer_question':N[k][0],'new_information':N[k][1],'visual_type':kind,'asset_ids':[asset],'fact_source_ids':['Guardian_2018_05_24' if k not in ['verdict','minimum'] else 'Guardian_2018_06_15'],'source_status':'court reporting checked; illustration provenance separated','rights_basis':'User-reported archive permission; generated art and original models separately identified in SOURCES.md','spoilers_to_hide':['Do not show Emile or couple portrait until husband reveal'] if i<19 else [],'on_screen_text':dict(zip(langs,N[k])),'animation_events':[],'camera_reason':'Stable framing; no routine pan/zoom','sound':{'narration_intent':'Escalating questions; restrained serious reveal','music_change':'Brief dip at husband reveal; quieter ending','original_audio_range':None},'qc':{'encoded_frame_review':None,'auditory_review':False}}
 for l in langs:
  r=next(x for x in timelines[l] if x['visual']==k);b['timing'][l]={'start_s':r['start'],'end_s':r['end']};b['narration'][l]=' '.join(w['text'] for w in words[l] if r['start']-.02<=w['start']<r['end']-.02)
 if k=='height':b['animation_events']=[{'object':'generic parachutist and slack canopy','change':'downward movement over continuous terrain','duration_s':2,'not_to_scale':True,'native_fps':30}]
 if k in ['linked','attempt']:b['animation_events']=[{'object':'event connector','change':'gas leak linked to jump, then two attempted murders stated','duration_s':1.2}]
 if k=='insurance':b['animation_events']=[{'object':'motive sequence','change':'death -> payout -> debts; no invented monetary amount','duration_s':.7}]
 beats.append(b)
plan={'episode_id':35,'languages':langs,'status':'complete_preview_pending_user_review','export':{'width':1080,'height':1920,'fps':30,'video_codec':'h264','pixel_format':'yuv420p','audio_codec':'aac','faststart':True},'continuity_bible':{'characters':['Anonymous adult woman, dark hair, teal suit and black helmet in generated jump scenes','Genuine Victoria and Emile photographs only as identified in sources'],'locations':['Generic English skydiving environment','Generic kitchen, not the actual home plan'],'persistent_landmarks':['Furrowed field, verge and fence','Kitchen counter/window and event connector']},'assets':json.loads((p/'assets.json').read_text()),'beats':beats,'final_qc':{'full_decode':None,'encoded_frame_review':None,'audio_listened_ru':False,'audio_listened_en':False,'review_status':'pending'}}
(p/'shot_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
