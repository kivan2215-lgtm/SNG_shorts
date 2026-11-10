from PIL import Image,ImageDraw,ImageFont
import math,random
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(d,pos,s,size=38,color='#ede8db',width=980):
 while max(ImageFont.truetype(font,size).getlength(z) for z in s.split('\n'))>width:size-=1
 d.multiline_text(pos,s,font=ImageFont.truetype(font,size),fill=color,anchor='mm',align='center',spacing=12)
def diagram(lang,phase):
 T=lambda a,b:a if lang=='ru' else b
 im=Image.new('RGB',(1080,1920),'#111e27');d=ImageDraw.Draw(im)
 text(d,(540,130),T('ВСЕГО ТРИ МЕТРА','ONLY TEN FEET APART'),54,color='#f1cc73')
 text(d,(540,215),T('Версия полиции • условный план','Police theory • illustrative layout'),29,color='#b5c2c6')
 # Wood flooring, masonry perimeter, paper stacks: room plan, not measured evidence.
 d.rounded_rectangle((70,340,1010,1340),20,fill='#756d5e',outline='#b7b0a0',width=10)
 for y in range(350,1340,45):d.line((80,y,1000,y),fill='#514f46',width=3)
 rng=random.Random(21)
 for x in [95,760]:
  for y in range(370,1270,85):
   for j in range(5):
    yy=y+j*10;xx=x+rng.randint(-5,8);w=rng.randint(160,205)
    d.polygon([(xx,yy),(xx+w,yy-4),(xx+w+8,yy+13),(xx,yy+19)],fill=rng.choice(['#c0b19b','#a79d89','#d0c1a4']),outline='#645e54')
 d.rounded_rectangle((350,440,700,760),15,fill='#334a52',outline='#9eb1ad',width=5)
 d.rounded_rectangle((390,465,660,540),16,fill='#a8b1a6');d.rectangle((385,550,665,720),fill='#667d79')
 text(d,(525,625),T('ГОМЕР','HOMER'),45);text(d,(525,820),T('Не мог добыть еду','Unable to reach food'),28,width=440)
 text(d,(530,1200),T('ЛЭНГЛИ','LANGLEY'),42,color='#f1cc73')
 d.line((330,760,330,1160),fill='#dfc785',width=5)
 for yy in [760,1160]:d.line((315,yy,345,yy),fill='#dfc785',width=5)
 text(d,(220,950),T('≈ 3 м','≈ 10 ft'),31,width=210)
 # Food route appears then is blocked by a modeled falling pile.
 if phase<.6:
  yy=1140-int(phase/.6*260);d.line((530,1140,530,yy),fill='#e8c461',width=9);d.polygon([(515,yy+20),(545,yy+20),(530,yy)],fill='#e8c461')
  text(d,(540,1410),T('ЛЭНГЛИ НЁС ЕДУ БРАТУ','LANGLEY WAS BRINGING FOOD'),37)
 else:
  shift=min(1,(phase-.6)/.25)
  for j in range(7):
   x=int(750-shift*(270+j*9));y=920+j*21
   d.polygon([(x,y),(x+160,y-25),(x+180,y+14),(x+10,y+32)],fill=['#a79d89','#d0c1a4','#887d65'][j%3],outline='#4a463d')
  text(d,(535,1080),T('ПРОХОД ПЕРЕКРЫТ','PASSAGE BLOCKED'),31,color='#ffcb6b',width=470)
  text(d,(540,1410),T('ЛОВУШКА СРАБОТАЛА','THE TRAP WAS TRIGGERED'),37)
 return im
def calendar(lang,day):
 T=lambda a,b:a if lang=='ru' else b
 im=Image.new('RGB',(1080,1920),'#101e28');d=ImageDraw.Draw(im)
 text(d,(540,180),T('ПОИСКИ ЛЭНГЛИ','THE SEARCH FOR LANGLEY'),48)
 text(d,(540,400),T(f'{day} ДНЕЙ',f'{day} DAYS'),105,color='#f0c469')
 for i in range(18):
  x=110+(i%6)*145;y=650+(i//6)*150
  d.rounded_rectangle((x,y,x+120,y+120),12,fill='#a1874d' if i<day else '#263e4b',outline='#798a88',width=3);text(d,(x+60,y+60),str(i+1),38)
 text(d,(540,1250),T('21 МАРТА → 8 АПРЕЛЯ 1947','MARCH 21 → APRIL 8, 1947'),37)
 return im
def passage(lang,progress):
 T=lambda a,b:a if lang=='ru' else b
 im=Image.new('RGB',(1080,1920),'#111e27');d=ImageDraw.Draw(im)
 text(d,(540,150),T('ТОННЕЛИ СРЕДИ ЗАВАЛОВ','TUNNELS THROUGH THE CLUTTER'),48)
 text(d,(540,235),T('Условная схема проходов','Illustrative passage layout'),28,color='#b6c3c5')
 d.rounded_rectangle((90,360,990,1360),15,fill='#665d50',outline='#c4b99f',width=6)
 for y in range(375,1340,40):d.line((100,y,980,y),fill='#4d473e',width=3)
 rng=random.Random(9)
 for x,y,w,h in [(120,390,300,260),(630,390,320,430),(120,840,300,450),(640,1090,300,210)]:
  for yy in range(y,y+h,30):
   xx=x+rng.randint(-9,9);d.rectangle((xx,yy,xx+w,yy+23),fill=rng.choice(['#a89e87','#d6c9a7','#b9ad91']),outline='#4c4b43',width=3)
 pts=[(520,1300),(520,980),(800,950),(520,950),(520,730),(260,730),(520,730),(520,420)]
 for i in range(min(len(pts)-1,int(progress*(len(pts)-1))+1)):
  d.line((pts[i],pts[i+1]),fill='#edc875',width=10)
 text(d,(540,1450),T('УЗКИЕ ПРОХОДЫ • СКРЫТЫЕ ЛОВУШКИ','NARROW PASSAGES • HIDDEN TRAPS'),34,color='#edc875')
 return im
