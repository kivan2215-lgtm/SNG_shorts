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
 sheet=Image.open(A/'recon.png').convert('RGB');w,h=sheet.size;pic=sheet.crop((i*w//3+6,4,(i+1)*w//3-6,h-4));im=ImageOps.fit(pic,(1080,1920),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,0,1080,340),fill=(5,15,25,165));d.rectangle((0,1400,1080,1920),fill=(5,15,25,120));txt(d,(540,230),title,49);return im
def render(lang,kind,p=1):
 T=lambda a,b:a if lang=='ru' else b
 if kind=='call':return recon(2,T('ОНА ПОЗВОНИЛА В ПОЛИЦИЮ','SHE CALLED THE POLICE'))
 if kind=='note':return recon(1,T('ЗАПИСКА ИЗМЕНИЛА ВСЁ','A NOTE CHANGED EVERYTHING'))
 if kind=='claim':return recon(0,T('ПО ЕЁ СЛОВАМ: ПОПЫТКА ПОХИЩЕНИЯ','HER CLAIM: AN ATTEMPTED ABDUCTION'))
 if kind=='house_open':return photo('house',T('ОНА ЗАСТРЕЛИЛА НЕЗНАКОМЦА','SHE HAD SHOT A STRANGER'))
 if kind=='house':return photo('house',T('МИССУРИ • 2016','MISSOURI • 2016'),T('Дом, где произошла стрельба','The home where the shooting took place'))
 if kind in ['louis','ending']:return photo('louis',T('ЛУИС ГАМПЕНБЕРГЕР','LOUIS GUMPENBERGER'),T('Ему было 33 года','He was 33 years old'))
 if kind=='betsy':return photo('betsy',T('БЕТСИ ФАРИЯ • УБИТА В 2011','BETSY FARIA • KILLED IN 2011'))
 if kind=='russ':return photo('russ',T('РАСС ФАРИЯ','RUSS FARIA'),T('2013: осуждён → 2015: оправдан','2013: convicted → 2015: acquitted'))
 if kind=='pam':return photo('pam',T('ПАМЕЛА ХАПП','PAMELA HUPP'),T('Полицейский снимок • 2019','Booking photograph • 2019'))
 titles={'cash':T('ЧТО НАШЛИ ПРИ ПОГИБШЕМ','WHAT INVESTIGATORS FOUND'),'phone':T('ТЕЛЕФОН ВЫДАЛ ПРОТИВОРЕЧИЕ','PHONE DATA RAISED A QUESTION'),'question':T('ОНА УЖЕ БЫЛА РЯДОМ С НИМ?','HAD SHE ALREADY BEEN NEAR HIM?'),'witness':T('ПРЕДЛОЖЕНИЕ СВИДЕТЕЛЬНИЦЕ','THE OFFER TO A WITNESS'),'refusal':T('ОНА ОТКАЗАЛАСЬ','SHE REFUSED'),'camera':T('АВТОМОБИЛЬ ПОПАЛ НА КАМЕРУ','THE VEHICLE WAS RECORDED'),'match':T('СЛЕДОВАТЕЛИ ОПОЗНАЛИ МАШИНУ','INVESTIGATORS IDENTIFIED THE CAR'),'past':T('СЛЕД ПРИВЁЛ К СТАРОМУ ДЕЛУ','A LINK TO AN OLDER CASE'),'insurance':T('СТРАХОВАЯ ВЫПЛАТА','THE LIFE INSURANCE PAYMENT'),'plot':T('ВЕРСИЯ ПРОКУРАТУРЫ','THE PROSECUTION’S ACCOUNT'),'sentence':T('ПРИГОВОР ЗА УБИЙСТВО ЛУИСА','SENTENCE FOR LOUIS’S MURDER')}
 im=base(titles[kind]);d=ImageDraw.Draw(im)
 if kind=='cash':
  d.rounded_rectangle((95,405,985,790),15,fill='#e8dfca');txt(d,(540,500),T('ЗАПИСКА С ИНСТРУКЦИЯМИ','A NOTE WITH INSTRUCTIONS'),39,'#20313a');txt(d,(540,635),T('Похищение → банк → деньги','Abduction → bank → money'),35,'#20313a')
  txt(d,(540,1050),'$900',145,'#edc46b');txt(d,(540,1220),T('Девять купюр по $100','Nine $100 bills'),39)
 elif kind in ['phone','question']:
  d.rounded_rectangle((110,390,460,1170),45,fill='#060d15',outline='#89a3ac',width=6);d.rounded_rectangle((135,450,435,1070),18,fill='#254451');txt(d,(285,690),T('ДАННЫЕ\nТЕЛЕФОНА','PHONE\nRECORDS'),36,w=270)
  x=710;y=720;d.polygon([(550,y),(710,y-170),(890,y)],fill='#71848b');d.rectangle((580,y,850,y+240),fill='#b9b5a0');d.rectangle((680,y+100,750,y+240),fill='#263d49')
  for i in range(3):d.arc((400-i*22,580-i*25,700+i*22,880+i*25),-55,55,fill='#78c9d0',width=4)
  txt(d,(720,1050),T('РАЙОН ДОМА\nЛУИСА','LOUIS’S\nNEIGHBORHOOD'),37,w=480)
  txt(d,(540,1310),T('Незадолго до стрельбы','Shortly before the shooting'),42,'#edc46b')
 elif kind in ['witness','refusal']:
  txt(d,(540,500),'$1,000',135,'#edc46b');panel(d,700,T('ПОСТАНОВОЧНЫЙ ЗВОНОК','A STAGED PHONE CALL'),T('Предложение незнакомки','An offer from a stranger'))
  if kind=='refusal':arrow(d,940);panel(d,1030,T('ОТКАЗ','REFUSED'),T('Свидетельница не согласилась','The witness declined'),'#d39f8a')
 elif kind in ['camera','match']:
  d.rounded_rectangle((90,410,990,980),24,fill='#223b48',outline='#7eabb8',width=4)
  d.rectangle((150,450,310,520),fill='#8199a1');d.polygon([(310,450),(365,420),(365,550),(310,520)],fill='#8199a1');d.line((200,520,200,565),fill='#8199a1',width=12)
  x=300+int(180*min(p,1));y=800;d.rounded_rectangle((x-150,y-50,x+150,y+65),20,fill='#c7c7b9');d.polygon([(x-95,y-50),(x-50,y-125),(x+85,y-125),(x+130,y-50)],fill='#c7c7b9');d.polygon([(x-68,y-60),(x-35,y-108),(x+70,y-108),(x+104,y-60)],fill='#243d4b')
  for xx in [x-100,x+100]:d.ellipse((xx-28,y+35,xx+28,y+91),fill='#101923',outline='#89959c',width=5)
  txt(d,(540,1050),T('ДОМАШНЕЕ ВИДЕОНАБЛЮДЕНИЕ','HOME SECURITY FOOTAGE'),35)
  if kind=='match':panel(d,1150,T('МАШИНА ХОЗЯЙКИ ДОМА','THE HOMEOWNER’S CAR'),T('По данным расследования','According to investigators'))
 elif kind=='past':
  for i,(a,b) in enumerate([('2011',T('Убийство Бетси','Betsy is murdered')),('2013',T('Муж осуждён','Her husband is convicted')),('2015',T('Повторный процесс: оправдан','Retrial: acquitted'))]):
   if i/3<=p:panel(d,400+i*320,a,b)
 elif kind=='insurance':
  panel(d,400,T('СТРАХОВКА БЕТСИ','BETSY’S LIFE INSURANCE'),T('Выплата после её смерти','Payment after her death'));arrow(d,655)
  txt(d,(540,875),'$150,000',120,'#edc46b');arrow(d,1000);panel(d,1100,T('ПОЛУЧАТЕЛЬ: ХОЗЯЙКА ДОМА','RECIPIENT: THE HOMEOWNER'),T('Связь между двумя делами','The connection between the cases'))
 elif kind=='plot':
  for i,(a,b) in enumerate([(T('ЛУИСА ЗАМАНИЛИ В ДОМ','LOUIS WAS LURED TO THE HOUSE'),T('Затем его убили','He was then killed')),(T('ПОДБРОСИЛИ ЗАПИСКУ','THE NOTE WAS PLANTED'),T('Чтобы направить подозрение на Расса','To point suspicion toward Russ')),(T('ИНСЦЕНИРОВАЛИ НАПАДЕНИЕ','AN ATTACK WAS STAGED'),T('Версия обвинения','The prosecution’s account'))]):
   if p>=i*.24:panel(d,380+i*335,a,b);arrow(d,610+i*335) if i<2 else None
 elif kind=='sentence':
  txt(d,(540,500),'2019',125,'#edc46b');panel(d,730,T('ПОЖИЗНЕННО','LIFE IN PRISON'),T('Без права на освобождение','Without parole'));txt(d,(540,1150),T('За убийство Луиса Гампенбергера','For the murder of Louis Gumpenberger'),36)
 return im
