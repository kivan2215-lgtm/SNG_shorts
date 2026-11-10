from PIL import Image,ImageDraw,ImageFont
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,p,s,n=42,c='#f2ecde',w=950):
 while max(ImageFont.truetype(font,n).getlength(x) for x in s.split('\n'))>w:n-=1
 d.multiline_text(p,s,font=ImageFont.truetype(font,n),fill=c,anchor='mm',align='center',spacing=14)
def card(lang,kind):
 T=lambda a,b:a if lang=='ru' else b;im=Image.new('RGB',(1080,1920),'#14232d');d=ImageDraw.Draw(im)
 if kind=='bone':
  text(d,(540,420),T('ЭТО БЫЛ НЕ МАНЕКЕН','THIS WAS NOT A MANNEQUIN'),53)
  text(d,(540,820),T('ЧЕЛОВЕЧЕСКАЯ\nКОСТЬ','A HUMAN\nBONE'),92,c='#f1ca6a')
  text(d,(540,1180),T('НАЧИНАЕТСЯ РАССЛЕДОВАНИЕ','AN INVESTIGATION BEGINS'),37)
 elif kind=='age':
  text(d,(540,400),T('ЭКСПЕРТИЗА РАСКРЫЛА ПРОШЛОЕ','THE PAST COMES TO LIGHT'),44)
  text(d,(540,820),T('65 ЛЕТ','65 YEARS'),135,c='#f1ca6a');text(d,(540,1110),T('МЕЖДУ СМЕРТЬЮ И ОБНАРУЖЕНИЕМ','BETWEEN DEATH AND REDISCOVERY'),34)
 elif kind=='clues':
  text(d,(540,210),T('УЛИКИ ДЛЯ ОПОЗНАНИЯ','CLUES TO HIS IDENTITY'),48)
  for i,(a,b) in enumerate([(T('МОНЕТА','A COIN'),T('Американский цент 1924 года','A 1924 American penny')),(T('БИЛЕТЫ','TICKET STUBS'),T('Музей преступлений Луиса Сонни',"Louis Sonney’s Museum of Crime"))]):
   y=460+i*420;d.rounded_rectangle((95,y,985,y+300),20,fill='#27424c',outline='#a79464',width=4);text(d,(540,y+85),a,57,c='#f1ca6a');text(d,(540,y+205),b,35)
 return im
def timeline(lang,stage):
 T=lambda a,b:a if lang=='ru' else b;im=Image.new('RGB',(1080,1920),'#14232d');d=ImageDraw.Draw(im)
 text(d,(540,180),T('ЖИЗНЬ ПОСЛЕ СМЕРТИ','AN AFTERLIFE ON DISPLAY'),49)
 rows=[('1911',T('Погиб. Тело забальзамировали.','Killed. His body was embalmed.')),('1916–1976',T('Владельцы, музеи, передвижные шоу','Owners, museums, traveling shows')),('1976',T('Обнаружен на съёмках сериала','Rediscovered during a TV shoot')),('1977',T('Похоронен в Оклахоме','Buried in Oklahoma'))]
 for i,(year,detail) in enumerate(rows):
  y=380+i*265
  d.ellipse((90,y+55,125,y+90),fill='#e9bf66' if i<=stage else '#61727b')
  if i<3:d.line((107,y+90,107,y+320),fill='#61727b',width=5)
  if i<=stage:
   text(d,(575,y+50),year,57,c='#efca78');text(d,(575,y+145),detail,34,w=830)
 return im
