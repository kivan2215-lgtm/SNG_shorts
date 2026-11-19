import asyncio,os,ssl
import edge_tts
from pathlib import Path
from edge_tts import communicate
ca=os.environ.get('SSL_CERT_FILE') or os.environ.get('CODEX_PROXY_CERT')
if ca and hasattr(communicate,'_SSL_CTX'): communicate._SSL_CTX.load_verify_locations(cafile=ca)
text='Числа-то передали. А перевести единицы кто-нибудь догадался? Да хрен там. Один, блядь, считает в бананах, а второй глянул на цифры и решил, что это физика.'
original_context=ssl.create_default_context
def trusted(*args,**kwargs):
    ctx=original_context(*args,**kwargs)
    ctx.load_verify_locations(cafile=ca or "/etc/ssl/certs/ca-certificates.crt")
    return ctx
ssl.create_default_context=trusted
async def main():
    voice=edge_tts.Communicate(text,'ru-RU-DmitryNeural',pitch='+5Hz',rate='-2%',proxy=os.environ.get('HTTPS_PROXY'))
    await voice.save('take.mp3')
asyncio.run(main())
