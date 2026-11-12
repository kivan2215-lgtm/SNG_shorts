from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from functools import lru_cache
import math
A=Path(__file__).parent/'assets'
@lru_cache(100)
def font(n,bold=True):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',n)
def txt(d,xy,s,n=46,c='#f2f0e8',w=930):
 while max(font(n).getlength(z) for z in s.split('\n'))>w:n-=1
 d.multiline_text(xy,s,font=font(n),fill=c,anchor='mm',align='center',spacing=18)
def base(title):
 im=Image.new('RGB',(1080,1920),'#101e29');d=ImageDraw.Draw(im)
 for x in range(0,1080,90):d.line((x,320,x,1420),fill='#152733')
 for y in range(320,1420,90):d.line((40,y,1040,y),fill='#152733')
 d.line((75,135,180,135),fill='#e6be70',width=5);txt(d,(540,235),title,52)
 return im
def photo(name,title,detail=''):
 im=base(title);pic=Image.open(A/(name+'.jpg')).convert('RGB');pic=ImageOps.contain(pic,(1000,1100),Image.Resampling.LANCZOS);im.paste(pic,((1080-pic.width)//2,340+(1100-pic.height)//2))
 if detail:txt(ImageDraw.Draw(im),(540,1380),detail,33,'#e6be70')
 return im
def panel(d,y,title,sub,col='#77ccd0'):
 d.rounded_rectangle((80,y,1000,y+220),22,fill='#1c3442',outline=col,width=3);txt(d,(540,y+65),title,48,col);txt(d,(540,y+150),sub,34,w=850)
def arrow(d,y):
 d.line((540,y,540,y+60),fill='#e6be70',width=7);d.polygon([(525,y+44),(555,y+44),(540,y+67)],fill='#e6be70')
def recon(i,title):
 sheet=Image.open(A/('recon_corrected.png' if i==0 else 'recon.png')).convert('RGB');w,h=sheet.size;pic=sheet.crop((i*w//3+6,4,(i+1)*w//3-6,h-4));im=ImageOps.fit(pic,(1080,1920),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,0,1080,340),fill=(5,15,25,165));d.rectangle((0,1400,1080,1920),fill=(5,15,25,120));txt(d,(540,230),title,49);return im
def render(lang,kind,p=1):
 T=lambda a,b:a if lang=='ru' else b
 if kind in ['opening','return','ending']:
  # Intentionally repeat the very same genuine portrait for the circular ending.
  title=T('КЭССИ ДЖО СТОДДАРТ • 16 ЛЕТ','CASSIE JO STODDART • AGE 16')
  im=base(title);pic=Image.open(A/'cassie-stoddart.jpg').convert('RGB');w,h=pic.size;pic=pic.crop((int(w*.322),int(h*.025),int(w*.69),int(h*.985)));pic=ImageOps.contain(pic,(900,1070),Image.Resampling.LANCZOS);im.paste(pic,((1080-pic.width)//2,350+(1070-pic.height)//2))
  if kind=='ending':
   d=ImageDraw.Draw(im);d.rectangle((80,1300,1000,1405),fill='#10202a');txt(d,(540,1350),T('ОНА ЕЩЁ НИЧЕГО НЕ ЗНАЛА','SHE HAD NO IDEA'),40,'#e6be70')
  return im
 if kind=='recorded':return photo('cassie-stoddart-brian-torey-library',T('ОНИ УЖЕ ВСЁ СПЛАНИРОВАЛИ','THEY HAD ALREADY MADE THEIR PLAN'),T('Подлинный кадр их видеозаписи','An authentic frame from their recording'))
 if kind=='tape':return photo('cassie-stoddart-tape',T('КАССЕТУ НАШЛИ В ОВРАГЕ','THE TAPE WAS FOUND IN A RAVINE'))
 if kind=='house':return photo('cassie-stoddart-true-crime',T('АЙДАХО • СЕНТЯБРЬ 2006','IDAHO • SEPTEMBER 2006'),T('Дом, за которым присматривала Кэсси','The house Cassie was looking after'))
 if kind=='evening':return recon(0,T('ОБЫЧНЫЙ ВЕЧЕР С ДРУЗЬЯМИ','AN ORDINARY EVENING WITH FRIENDS'))
 if kind=='stairs':return recon(1,T('ВНИЗУ ПОСЛЫШАЛИСЬ ЗВУКИ','NOISES CAME FROM DOWNSTAIRS'))
 if kind=='phone':return recon(2,T('ОН ОТВЕЧАЛ ШЁПОТОМ','HE ANSWERED IN A WHISPER'))
 if kind=='discovered':return photo('oxygen',T('24 СЕНТЯБРЯ • КЭССИ НАШЛИ МЁРТВОЙ','24 SEPTEMBER • CASSIE WAS FOUND DEAD'))
 if kind=='investigator':return photo('cassie-stoddart-investigator',T('СЛЕДОВАТЕЛЕЙ ПРИВЕЛИ К ТАЙНИКУ','INVESTIGATORS WERE LED TO THE STASH'),T('Следователь с материалами дела','An investigator with evidence from the case'))
 if kind=='evidence':
  im=photo('cassie-stoddart-tape',T('НОЖИ. МАСКИ. ВИДЕОКАССЕТА.','KNIVES. MASKS. A VIDEOTAPE.'));return im
 if kind=='court':return photo('court',T('ЗАПИСЬ РАСКРЫЛА ПЛАН','THE RECORDING REVEALED THE PLAN'),T('Верховный суд Айдахо • 2012','Idaho Supreme Court • 2012'))
 if kind=='offenders':
  im=base(T('БРАЙАН ДРЕЙПЕР И ТОРИ АДАМЧИК','BRIAN DRAPER AND TOREY ADAMCIK'))
  for i,n in enumerate(['brian-lee-draper','torey-adamcik']):
   pic=Image.open(A/(n+'.jpg')).convert('RGB');pic=ImageOps.contain(pic,(970,455),Image.Resampling.LANCZOS);im.paste(pic,((1080-pic.width)//2,380+i*500))
  return im
 titles={'outage':T('ЧЕРЕЗ 15 МИНУТ ПОГАС СВЕТ','15 MINUTES LATER: THE POWER WENT OUT'),'alone':T('КЭССИ ОСТАЛАСЬ ОДНА','CASSIE WAS LEFT ALONE'),'missed':T('НА СЛЕДУЮЩИЙ ДЕНЬ — ТИШИНА','THE NEXT DAY: NO ANSWER'),'alibi':T('ИХ ВЕРСИЯ: ОНИ БЫЛИ В КИНО','THEIR STORY: THEY WERE AT THE MOVIES'),'contradiction':T('НО О ЧЁМ БЫЛ ФИЛЬМ?','BUT WHAT WAS THE MOVIE ABOUT?'),'route':T('ПЛАН, ВОССТАНОВЛЕННЫЙ СУДОМ','THE PLAN RECONSTRUCTED IN COURT'),'sentence':T('ПРИГОВОРЫ • 2007','THE SENTENCES • 2007')}
 im=base(titles[kind]);d=ImageDraw.Draw(im)
 if kind in ['outage','alone']:
  d.polygon([(130,610),(540,370),(950,610)],fill='#536975');d.rectangle((170,610,910,1220),fill='#314854',outline='#aac0c2',width=5);d.line((170,930,910,930),fill='#acb8af',width=7)
  lit='#c4af69' if kind=='outage' and p<.2 else '#10202d'
  for x in [270,620]:d.rectangle((x,690,x+160,835),fill=lit,outline='#9cb0b5',width=5);d.line((x+80,690,x+80,835),fill='#9cb0b5',width=3)
  txt(d,(540,1020),T('НИЖНИЙ ЭТАЖ','DOWNSTAIRS'),37)
  if kind=='alone':txt(d,(540,1280),T('ПАРЕНЬ УЕХАЛ','HER BOYFRIEND LEFT'),43,'#e6be70')
  else:txt(d,(540,1310),T('СВЕТ ОТКЛЮЧИЛСЯ','POWER OFF'),48,'#e6be70')
 elif kind=='missed':
  d.rounded_rectangle((270,380,810,1350),60,fill='#070e16',outline='#95adb6',width=6);d.rounded_rectangle((305,480,775,1200),20,fill='#233c4b')
  for k in range(3):d.arc((405-k*28,660-k*28,675+k*28,930+k*28),210,330,fill='#e6be70',width=5)
  txt(d,(540,1030),T('ВЫЗОВ\nБЕЗ ОТВЕТА','NO\nANSWER'),49,w=440)
 elif kind in ['alibi','contradiction']:
  d.rounded_rectangle((100,400,980,930),20,fill='#1d3441',outline='#9bafb2',width=4)
  d.rectangle((175,460,905,775),fill='#111d27');txt(d,(540,615),T('КИНОТЕАТР','MOVIE THEATER'),62,'#e6be70')
  for y in [820,880]:
   for x in range(190,900,100):d.rounded_rectangle((x,y,x+65,y+40),8,fill='#6c4441')
  panel(d,1060,T('НЕ СМОГ ПЕРЕСКАЗАТЬ ФИЛЬМ','COULD NOT DESCRIBE THE FILM') if kind=='contradiction' else T('ПОКАЗАНИЯ ДРУЗЕЙ','THE FRIENDS’ ACCOUNT'),T('Противоречие на допросе','A contradiction during questioning') if kind=='contradiction' else T('Полиция проверяла их слова','Police examined their story'))
 elif kind=='route':
  rows=[(T('ОСТАВИЛИ ДВЕРЬ НЕЗАПЕРТОЙ','LEFT A DOOR UNLOCKED'),T('До ухода из дома','Before leaving the house')),(T('ВЕРНУЛИСЬ','RETURNED'),T('Кэсси и её парень ещё были внутри','Cassie and her boyfriend were still inside')),(T('ДОЖДАЛИСЬ ЕГО ОТЪЕЗДА','WAITED FOR HIM TO LEAVE'),T('Кэсси осталась одна','Cassie was alone'))]
  for i,(a,b) in enumerate(rows):
   if p>=i*.26:panel(d,380+i*330,a,b);arrow(d,610+i*330) if i<2 else None
 elif kind=='sentence':
  txt(d,(540,490),'2007',130,'#e6be70');panel(d,700,T('ОБА — ПОЖИЗНЕННО','BOTH: LIFE IN PRISON'),T('Без права на освобождение','Without parole'));txt(d,(540,1150),T('За убийство Кэсси','For Cassie’s murder'),45)
 return im
