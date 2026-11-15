from pathlib import Path
import math
p=Path('docs/flora-design/vp1-629/prototype/assets')
keys=['uk-landscape','uk-forces','banking-landscape','banking-forces','lloyds-inside','lloyds-landscape','lloyds-forces','news','tools']
for i,k in enumerate(keys):
 lines=[]
 if 'forces' in k:
  for j in range(39):
   y=28*j+i*7;lines.append(f'<path d="M-80 {y} C180 {y-135} 360 {y+130} 550 {y-25} S870 {y-85} 1100 {y+35}"/>')
 elif k=='lloyds-inside':
  for j in range(11):
   x=60+j*90;lines.append(f'<path d="M{x} 1160 V390 Q500 {-80+j*20} {1000-x} 390 V1160"/>')
  for j in range(13):lines.append(f'<path d="M0 {j*92} L1000 {j*92+75}"/>')
 elif k=='news':
  for j in range(4):
   x=90+j*235;lines.append(f'<rect x="{x}" y="140" width="190" height="980"/>')
   for n in range(30):lines.append(f'<path d="M{x+12} {180+n*29} h166"/>')
 elif k=='tools':
  for rad in range(80,501,35):lines.append(f'<circle cx="700" cy="650" r="{rad}"/>')
  for a in range(0,360,10):
   z=math.radians(a);lines.append(f'<path d="M700 650 L{700+530*math.cos(z):.2f} {650+530*math.sin(z):.2f}"/>')
  lines.append('<path d="M120 1150 L860 160 L990 1100 Z"/>')
 else:
  for j in range(25):
   y=45*j+i*9;lines.append(f'<path d="M-50 {y} C250 {y+135} 330 {y-90} 610 {y+40} S900 {y+180} 1100 {y-40}"/>')
  for j in range(15):
   x=70+j*67;y=100+(j%5)*176+i*11;lines.append(f'<circle cx="{x}" cy="{y}" r="{20+j%4*9}"/><path d="M{x} {y} L{900-x/3} {y+220}"/>')
  if k=='uk-landscape':
   for j in range(9):lines.append(f'<path d="M{j*105} 1100 v-190 l35 -35 l35 35 v190 m-50 -140 h30 m-30 30 h30 m-30 30 h30"/>')
 p.joinpath('watermark-'+k+'.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1300" fill="none" stroke="#244738" stroke-width=".85">'+''.join(lines)+'</svg>\n')
print('Nine decorative watermark treatments, no relationships or metrics encoded')
