from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import math
p=Path(__file__).parent
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def label(d,xy,s,size=38,color='#f6f3e9',width=960):
 while max(ImageFont.truetype(font,size).getlength(l) for l in s.split('\n'))>width:size-=1
 d.multiline_text(xy,s,font=ImageFont.truetype(font,size),fill=color,anchor='mm',align='center',spacing=14)
def base(title):
 im=Image.new('RGB',(1080,1920),'#101b25');d=ImageDraw.Draw(im);label(d,(540,155),title,48);return im,d
def diagram(stage):
 im,d=base('КАК ПРОНИКЛИ ЧЕРЕЗ СТЕНУ')
 # Two bathrooms separated by shared service shaft; illustrative geometry.
 for y,title in [(350,'СОСЕДНЯЯ ПУСТАЯ КВАРТИРА'),(1050,'ВАННАЯ РУТИ')]:
  d.rounded_rectangle((80,y,1000,y+370),20,fill='#526975',outline='#93a8ad',width=6)
  for x in range(100,1000,75):d.line((x,y+70,x,y+360),fill='#69808b',width=2)
  for yy in range(y+70,y+365,65):d.line((100,yy,980,yy),fill='#69808b',width=2)
  d.rounded_rectangle((115,y+80,310,y+310),25,fill='#dae0da',outline='#9eadae',width=5)
  d.ellipse((145,y+130,280,y+270),fill='#98b2bb');d.rectangle((200,y+90,219,y+145),fill='#e6e8e1')
  d.rounded_rectangle((795,y+95,935,y+280),35,fill='#d2d8d1');d.ellipse((805,y+145,925,y+270),fill='#a1b3b8')
  label(d,(540,y+40),title,32)
 d.rectangle((80,730,1000,1040),fill='#26353e',outline='#9b9284',width=7)
 for x,c in [(250,'#b78e65'),(820,'#91a5ab')]:
  d.line((x,738,x,1030),fill='#172027',width=28);d.line((x-3,738,x-3,1030),fill=c,width=17)
  for yy in [780,970]:d.rectangle((x-18,yy,x+14,yy+12),fill='#c8c0a7')
 label(d,(540,880),'ПРОСТРАНСТВО\nС ТРУБАМИ',34)
 for y in [728,1034]:
  d.rectangle((430,y-18,650,y+20),fill='#0b1016',outline='#f0bc56',width=5)
 label(d,(540,680),'ШКАФЧИК СНЯТ',30,color='#ffce65')
 label(d,(540,1110),'ОТВЕРСТИЕ ЗА ШКАФЧИКОМ',28,color='#ffce65')
 # Highlight route in stages without pretending to know exact building dimensions.
 pts=[(540,570),(540,730),(690,800),(690,965),(540,1038),(540,1220)]
 progress=max(0,min(1,stage));lengths=[math.dist(pts[i],pts[i+1]) for i in range(5)];rem=sum(lengths)*progress
 for i,L in enumerate(lengths):
  if rem<=0:break
  a=pts[i];b=pts[i+1];f=min(1,rem/L);end=(a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1]));d.line((a,end),fill='#ffcd60',width=13);rem-=L
 if progress>.98:d.polygon([(520,1200),(560,1200),(540,1235)],fill='#ffcd60')
 label(d,(540,1370),'ОТВЕРСТИЕ → ТРУБЫ → СОСЕДНЯЯ ВАННАЯ',28,color='#ffce65')
 return im
def timeline(day):
 im,d=base('ДВА ДНЯ ЗА ЗАКРЫТОЙ ДВЕРЬЮ')
 rows=[('22 АПРЕЛЯ','Звонок. Полиция приезжает.','Ключ не подходит.'),('23 АПРЕЛЯ','Повторный приезд.','Дверь остаётся закрытой.'),('24 АПРЕЛЯ','В квартиру входят.','Рути находят погибшей.')]
 for i,(date,a,b) in enumerate(rows):
  y=390+i*330;c='#f1c563' if i==day else '#617481'
  d.rounded_rectangle((90,y,990,y+260),24,fill='#20323e',outline=c,width=5)
  label(d,(540,y+55),date,43,color=c)
  if i<=day:label(d,(540,y+145),a+'\n'+b,34)
 return im
