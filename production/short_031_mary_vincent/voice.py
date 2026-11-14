import asyncio, json, os, re, ssl, subprocess, sys, unicodedata, wave
from pathlib import Path
import edge_tts
import edge_tts.communicate

ROOT = Path(__file__).resolve().parent
LANG = sys.argv[1]
P = ROOT / LANG
VOICE = {'ru':'ru-RU-DmitryNeural','en':'en-US-GuyNeural'}[LANG]
RATES = ['+0%','+1%','+1%','-3%','-2%']
PITCHES = ['+1Hz','+1Hz','+1Hz','-2Hz','-2Hz']
ca = os.environ.get('SSL_CERT_FILE') or os.environ.get('CODEX_PROXY_CERT')
old_context = ssl.create_default_context
def trusted_context(*args, **kwargs):
    ctx = old_context(*args, **kwargs)
    if ca: ctx.load_verify_locations(cafile=ca)
    return ctx
ssl.create_default_context = trusted_context

def spoken_text(s):
    if LANG == 'ru':
        for a,b in {'Мэри':'Мэ́ри','Винсент':'Ви́нсент','Лоуренс':'Ло́уренс','Синглтон':'Си́нглтон','Синглтона':'Си́нглтона','Синглтоном':'Си́нглтоном','Роксану':'Рокса́ну','Хейс':'Хе́йс'}.items():
            s = re.sub(r'\b'+a+r'\b', b, s)
    return unicodedata.normalize('NFC',s)

async def main():
    paragraphs = [s.strip().replace('\n',' ') for s in (P/'narration.txt').read_text().split('\n\n') if s.strip()]
    assert len(paragraphs)==5
    all_boundaries=[]; offset=0; all_pcm=[]; meta=[]
    for i, paragraph in enumerate(paragraphs):
        text=spoken_text(paragraph)
        (P/f'tts_{i}.txt').write_text(text)
        out=P/f'voice_{i}.mp3'; cache=P/f'voice_{i}.json'
        if out.exists() and cache.exists():
            words=json.loads(cache.read_text())
        else:
            for attempt in range(5):
                try:
                    communicator=edge_tts.Communicate(text,VOICE,rate=RATES[i],pitch=PITCHES[i],boundary='WordBoundary',proxy=os.environ.get('HTTPS_PROXY'))
                    words=[]
                    with out.open('wb') as f:
                        async for msg in communicator.stream():
                            if msg['type']=='audio':f.write(msg['data'])
                            elif msg['type']=='WordBoundary':words.append(msg)
                    if not words:raise RuntimeError('No word boundaries')
                    cache.write_text(json.dumps(words,ensure_ascii=False));break
                except Exception:
                    if attempt==4:raise
                    await asyncio.sleep(2)
        pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-ar','48000','-ac','1','-f','s16le','-'])
        duration=len(pcm)/96000
        start=max(0,words[0]['offset']/1e7-.07)
        end=min(duration,(words[-1]['offset']+words[-1]['duration'])/1e7+.14)
        a=int(start*48000); b=int(end*48000)
        all_pcm.append(pcm[a*2:b*2])
        for w in words:
            all_boundaries.append({'text':unicodedata.normalize('NFC',w['text'].replace('\u0301','')),'start':max(offset,offset+w['offset']/1e7-a/48000),'end':offset+(w['offset']+w['duration'])/1e7-a/48000,'paragraph':i})
        meta.append({'paragraph':i,'start':offset,'end':offset+(b-a)/48000,'rate':RATES[i],'pitch':PITCHES[i]})
        offset+=(b-a)/48000
        if i<4:
            # Small paragraph breath; TTS sentence punctuation provides inner phrasing.
            all_pcm.append(b'\0'*(int(.16*48000)*2));offset+=.16
        print(LANG,i,round((b-a)/48000,2),flush=True)
    with wave.open(str(P/'voice.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(b''.join(all_pcm))
    (P/'words.json').write_text(json.dumps(all_boundaries,ensure_ascii=False,indent=2))
    (P/'voice_uncut.wav').write_bytes((P/'voice.wav').read_bytes())
    (P/'words_uncut.json').write_bytes((P/'words.json').read_bytes())
    (P/'voice_settings.json').write_text(json.dumps({'voice':VOICE,'duration':offset,'paragraphs':meta,'source_preset':'SNG 016 V2 / persistent master settings'},ensure_ascii=False,indent=2))
    print('DONE',LANG,round(offset,3),flush=True)

asyncio.run(main())
