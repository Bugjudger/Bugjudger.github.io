"""Build hover previews from additional paper evidence, never decorative motion."""
from pathlib import Path
import base64, json, re, subprocess, html, io
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/projects/teasers';ASSETS=OUT/'hover-sources';ASSETS.mkdir(exist_ok=True)
SRC=Path('/tmp/homepage-real-media')
ID=Path('/Users/yedingqiang/Library/Mobile Documents/com~apple~CloudDocs/PhD/JHU/2027-IDWorld/fig1_package_2026-10-21/assets')
def crop(source,name,box=None,width=500):
 dest=ASSETS/(name+'.webp')
 if not dest.exists():
  filters=[]
  if box:filters.append('crop='+':'.join(map(str,[box[2],box[3],box[0],box[1]])))
  filters.append(f'scale=min({width}\\,iw):-1:flags=lanczos')
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-vf',','.join(filters),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
  Image.open(io.BytesIO(raw)).save(dest,quality=90,method=6)
 return dest
# Each crop below is taken from a rendered original paper figure.
for who in ['A','B']:
 for what in ['input','c_side','c_back','c_head']:crop(ID/f'{what}_{who}.png',f'id-{what}-{who}',width=180)
for case in range(2):
 # Figure 7: top row same subject, lower row different subjects; full pair plus part-similarity map.
 crop('/tmp/sapiens-hi.png',f'sapiens-case-{case}',(1815,300+case*309,489,303),width=600)
for row in range(3):
 for col,x in enumerate([100,138,176]):crop('/tmp/biggait-hi.png',f'big-stage-{row}-{col}',(x*3,(145+row*69)*3,34*3,65*3),width=120)
# Figure 7 appearance editing: original subject, +size, +hoodie; third subject, +hat.
for name,box in {'edit-original-1':(281,106,85,42),'edit-size':(375,106,85,42),'edit-hoodie':(468,106,85,42),'edit-original-3':(281,219,85,42),'edit-hat':(375,219,85,42)}.items():
 crop('/tmp/gaitediter-hi.png',name,tuple(v*3 for v in box),width=510)
for j,x in enumerate([48,237,423,608,795,982]):crop(SRC/'clue-example.png',f'clue-frame-{j}',(x,424,180,103),width=360)

def text(s,x,y,size=21,anchor='middle',color='#222',weight='400'):
 return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(s)}</text>'
CROP_ID=0
def image(file,x,y,w,h,view=None,fit="xMidYMid meet"):
 global CROP_ID
 f=Path(file);data=base64.b64encode(f.read_bytes()).decode();iw,ih=Image.open(f).size
 img=f'<image href="data:image/webp;base64,{data}" width="{iw}" height="{ih}"/>'
 vb=' '.join(map(str,view or [0,0,iw,ih]))
 if view:
  CROP_ID+=1;cid=f'crop-{CROP_ID}'
  img=f'<defs><clipPath id="{cid}"><rect x="{view[0]}" y="{view[1]}" width="{view[2]}" height="{view[3]}"/></clipPath></defs><g clip-path="url(#{cid})">{img}</g>'
 return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" preserveAspectRatio="{fit}">{img}</svg>'
def pixel_reference_cutout(file,x,y,w,h,protect_hair=False):
 # Generate a native SVG clip from border-connected neutral background pixels.
 # The original photograph stays embedded unchanged; gray hair is explicitly protected.
 from collections import deque
 im=Image.open(file).convert('RGB');iw,ih=im.size;px=im.load()
 samples=[px[xx,yy] for xx,yy in [(0,0),(iw-1,0),(0,ih-1),(iw-1,ih-1),(0,ih//2),(iw-1,ih//2)]]
 bg=tuple(sorted(c[k] for c in samples)[len(samples)//2] for k in range(3))
 hair=[(59,30),(66,30),(71,33),(73,38),(72,45),(68,49),(60,48),(55,41),(55,34)]
 def protected(xx,yy):
  if not protect_hair:return False
  inside=False
  for j,p in enumerate(hair):
   q=hair[j-1]
   if (p[1]>yy)!=(q[1]>yy) and xx<(q[0]-p[0])*(yy-p[1])/(q[1]-p[1])+p[0]:inside=not inside
  return inside
 def is_background(xx,yy):
  c=px[xx,yy]
  return not protected(xx,yy) and max(abs(c[k]-bg[k]) for k in range(3))<=38 and max(c)-min(c)<=40
 removed=set();queue=deque([(xx,yy) for xx in range(iw) for yy in [0,ih-1]]+[(xx,yy) for yy in range(ih) for xx in [0,iw-1]])
 while queue:
  xx,yy=queue.popleft()
  if (xx,yy) in removed or not is_background(xx,yy):continue
  removed.add((xx,yy))
  queue.extend((a,b) for a,b in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)] if 0<=a<iw and 0<=b<ih and (a,b) not in removed)
 remaining={(xx,yy) for yy in range(ih) for xx in range(iw)}-removed;components=[]
 while remaining:
  start=remaining.pop();component={start};queue=deque([start])
  while queue:
   xx,yy=queue.popleft()
   for a,b in [(xx+dx,yy+dy) for dx in [-1,0,1] for dy in [-1,0,1] if dx or dy]:
    if (a,b) in remaining:remaining.remove((a,b));component.add((a,b));queue.append((a,b))
  components.append(component)
 foreground=max(components,key=len);runs=[]
 for yy in range(ih):
  xx=0
  while xx<iw:
   if (xx,yy) not in foreground:xx+=1;continue
   start=xx
   while xx<iw and (xx,yy) in foreground:xx+=1
   runs.append(f'M{start} {yy}h{xx-start}v1h{start-xx}z')
 cid='pixel-cutout-'+Path(file).stem
 data=base64.b64encode(Path(file).read_bytes()).decode()
 return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 {iw} {ih}"><defs><clipPath id="{cid}"><path d="{" ".join(runs)}"/></clipPath></defs><image href="data:image/webp;base64,{data}" width="{iw}" height="{ih}" clip-path="url(#{cid})"/></svg>'
def asset(name):return ASSETS/(name+'.webp')
def local(name):return OUT/name
manifest=[]
POSTERS={'idworld':'idworld-imagination.svg','puppet':'puppet-body-alignment.svg','videoresearcher':'videoresearcher-tools.svg','clue':'clue-distillation.svg','foundation':'foundation-scaling.svg','gaitmax':'gaitmax-poses.svg','biggergait':'bigger-layer-scan.svg','sapiensid':'sapiens-scales.svg','biggait':'biggait-features.svg','gaitediter':'gaitediter-edit.svg'}
def envelope(values,times,duration):
 return f'<animate attributeName="opacity" values="{values}" keyTimes="{times}" dur="{duration}s" calcMode="linear" repeatCount="indefinite"/>'
def base_image(poster):
 raw=base64.b64encode((OUT/poster).read_bytes()).decode()
 return f'<image href="data:image/svg+xml;base64,{raw}" x="0" y="0" width="360" height="240"/>'
def write_preview(stem,body,title):
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="540" height="360" viewBox="0 0 360 240" role="img"><title>{html.escape(title)}</title><style>text{{font-family:Lato,Helvetica,Arial,sans-serif}}</style>{body}</svg>'
 (OUT/(stem+'-evidence.svg')).write_text(svg)
def custom(stem,poster,overlay,title,source,extra,duration):
 write_preview(stem,base_image(poster)+overlay,title)
 manifest.append({'asset':stem+'-evidence.svg','extra_information':extra,'source':source,'transition':'Continuous local cross-dissolve within a fixed composition; begins at t=0','duration_seconds':duration,'starts_with_exact_static_image':poster,'poster_hold_seconds':0})
def save(stem,frames,title,source,extra,seconds=2.8):
 # The original cover begins dissolving immediately into additional evidence.
 frames=[base_image(POSTERS[stem])]+frames
 n=len(frames);transition=0.45;seconds=round(seconds*0.65,2);step=seconds+transition;total=(n-1)*step+transition;body=''
 for i,frame in enumerate(frames):
  if i==0:times=[0,transition/total,(total-transition)/total,1];values=[1,0,0,1]
  else:
   begin=(i-1)*step;end=begin+transition+seconds
   pairs=[(0,0)]
   if begin>0:pairs.append((begin/total,0))
   pairs.extend([((begin+transition)/total,1),(end/total,1),((end+transition)/total,0)])
   if pairs[-1][0]<1:pairs.append((1,0))
   times=[t for t,v in pairs];values=[v for t,v in pairs]
  anim=envelope(';'.join(map(str,values)),';'.join(str(round(t,7)) for t in times),total)
  body+=f'<g opacity="{1 if i==0 else 0}">{anim}{frame}</g>'
 write_preview(stem,body,title)
 manifest.append({'asset':stem+'-evidence.svg','extra_information':extra,'source':source,'states':n,'transition_seconds':transition,'poster_hold_seconds':0,'starts_with_exact_static_image':POSTERS[stem]})
# 1. Two real observations of the SAME identity: inconsistent explicit images,
# then consistent latent predictions. The two rows are essential evidence.
def poster_file(name,body,title):
 (OUT/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="540" height="360" viewBox="0 0 360 240" role="img"><title>{html.escape(title)}</title>{body}</svg>')
# A soft, native SVG alpha mask removes neutral figure backdrops, preserving
# colored feature/body pixels. It is never applied to RGB input photographs.
feature_filter='<defs><filter id="feature-alpha" color-interpolation-filters="sRGB"><feColorMatrix in="SourceGraphic" type="matrix" values="1 -1 0 0 0 0 1 -1 0 0 -1 0 1 0 0 0 0 1 0" result="chroma"/><feColorMatrix in="chroma" type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 30 30 30 0 -0.6"/><feComposite in="SourceGraphic" operator="in"/></filter></defs>'
def colored(content):return '<g filter="url(#feature-alpha)">'+content+'</g>'
def clean_figure(file,x,y,w,h,body=False):
 # Native vector clipping: suppress neutral plate backgrounds and red direction
 # arrows, while retaining the supplied RGB pixels and original proportions.
 im=Image.open(file).convert('RGB');iw,ih=im.size;px=im.load();runs=[]
 for yy in range(ih):
  xx=0
  def keep(xx):
   r,g,b=px[xx,yy];chroma=max(r,g,b)-min(r,g,b)
   return chroma>(18 if body else 32) and not (body and r>160 and g<85 and b<85)
  while xx<iw:
   if not keep(xx):xx+=1;continue
   a=xx
   while xx<iw and keep(xx):xx+=1
   runs.append(f'M{a} {yy}h{xx-a}v1h{a-xx}z')
 cid='clean-'+Path(file).stem
 data=base64.b64encode(Path(file).read_bytes()).decode()
 return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 {iw} {ih}"><defs><clipPath id="{cid}"><path d="{" ".join(runs)}"/></clipPath></defs><image href="data:image/webp;base64,{data}" width="{iw}" height="{ih}" clip-path="url(#{cid})"/></svg>'

def tight(markup):
 # Tighten the viewport around the existing SVG clipping geometry. Original
 # pixel data and silhouette proportions remain unchanged.
 runs=re.findall(r'M(\d+) (\d+)h(\d+)v1h-\d+z',markup)
 if not runs:return markup
 x=min(int(a) for a,b,c in runs);y=min(int(b) for a,b,c in runs)
 right=max(int(a)+int(c) for a,b,c in runs);bottom=max(int(b)+1 for a,b,c in runs)
 return re.sub(r'viewBox="[^"]+"',f'viewBox="{x-3} {y-3} {right-x+6} {bottom-y+6}"',markup,count=1)
def project(point,viewport,view,stretch=False):
 x,y,w,h=viewport;vx,vy,vw,vh=view;px,py=point
 if stretch:return (round(x+(px-vx)*w/vw,2),round(y+(py-vy)*h/vh,2))
 scale=min(w/vw,h/vh)
 return (round(x+(w-vw*scale)/2+(px-vx)*scale,2),round(y+(h-vh*scale)/2+(py-vy)*scale,2))

def add(key,title,before,after,description,source,note='',animated=None):
 # Publish the two approved compositions directly to homepage assets.
 poster='idworld-pixel-reference.svg' if key=='idworld' else 'puppet-body-alignment.svg'
 poster_file(poster,before,title)
 if animated is None:
  # Match the approved immediate 0.6s reveal; reset is handled on pointer leave.
  animated=before+'<defs><clipPath id="reveal"><rect width="0" height="240"><animate attributeName="width" from="0" to="360" dur="0.6s" fill="freeze"/></rect></clipPath></defs><g clip-path="url(#reveal)">'+after+'</g>'
 write_preview(key,animated,title)
 manifest.append({'asset':key+'-evidence.svg','source':source,'extra_information':description,'note':note,'starts_with_exact_static_image':poster,'poster_hold_seconds':0,'duration_seconds':0.6 if key=='idworld' else 2.6})
# IDWorld: same approved single observation + side/back views. Only composition
# and reveal change: large aligned foregrounds; wipe avoids ghosted faces.
fixed=image(OUT/'idworld-input_A.webp',9,18,96,204)
fixed+='<path d="M116 120 H148 M142 114 L148 120 L142 126" stroke="#969da2" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
before=fixed;after=fixed
def foreground_box(markup):
 runs=re.findall(r'M(\d+) (\d+)h(\d+)v1h-\d+z',markup)
 return (min(int(a) for a,b,c in runs),min(int(b) for a,b,c in runs),max(int(a)+int(c) for a,b,c in runs),max(int(b)+1 for a,b,c in runs))
def displayed_box(markup):
 import xml.etree.ElementTree as ET
 el=ET.fromstring(markup);x,y,w,h=[float(el.attrib[k]) for k in ['x','y','width','height']]
 vx,vy,vw,vh=map(float,el.attrib['viewBox'].split());scale=min(w/vw,h/vh)
 l,t,r,b=foreground_box(markup)
 return (x+(w-vw*scale)/2+(l-vx)*scale,y+(h-vh*scale)/2+(t-vy)*scale,(r-l)*scale,(b-t)*scale)
alignment=[]
for part,x in [('side',127),('back',245)]:
 pixel=tight(pixel_reference_cutout(OUT/f'idworld-b_{part}_A.webp',x+5.3,28.2,95.4,183.6,protect_hair=part=='side'))
 before+=pixel
 target=displayed_box(pixel)
 file=OUT/f'idworld-c_{part}_A.webp'
 # Use visible high-alpha body support, not the low-alpha halo/noise that
 # previously expanded the latent crop. Fit that body to the pixel foreground.
 alpha=Image.open(file).getchannel('A');l,t,r,b=alpha.point(lambda v:255 if v>=128 else 0).getbbox()
 preview=ASSETS/f'id-c_{part}-A.webp'
 factor=Image.open(preview).width/Image.open(file).width
 after+=image(preview,*target,[v*factor for v in [l,t,r-l,b-t]],fit='none')
 alignment.append({'view':part,'pixel_display_xywh':target,'latent_core_xywh':[l,t,r-l,b-t],'latent_display_xywh':target})
(OUT/'idworld-alignment.json').write_text(json.dumps(alignment,indent=2))
add('idworld','IDWorld',before,after,'保留单人、侧面和背面的原意。右侧两个人物同步缩小 10%；Pixel 与 Latent 的可见高度、宽度和中心对齐，切换时保持一致。','原论文 Figure 1：input_A、b_side/back_A、c_side/back_A。','像素图是显式生成的参考对比，并非 IDWorld 的中间输出。')
# PuppetGait: restore the approved fast correspondence demonstration,
# but use RGB as the input and calibrate its markers in RGB pixel coordinates.
feature_filter='<defs><filter id="puppet-feature-alpha" color-interpolation-filters="sRGB"><feColorMatrix in="SourceGraphic" type="matrix" values="1 -1 0 0 0 0 1 -1 0 0 -1 0 1 0 0 0 0 0 1 0" result="chroma"/><feColorMatrix in="chroma" type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 50 50 50 0 -1.5"/><feComponentTransfer><feFuncA type="discrete" tableValues="0 1"/></feComponentTransfer><feComposite in="SourceGraphic" operator="in"/></filter></defs>'
rgbview=[18,4,119,275]
frame=feature_filter+image(OUT/'puppet-input-clean.webp',15,24,82,192,rgbview)
frame+='<g filter="url(#puppet-feature-alpha)">'+image(ASSETS/'puppet-target-lvm.webp',261,24,94,192,[0,56,175,446],fit='none')+'</g>'
frame+='<path d="M105 126 H126 M120 120 L126 126 L120 132 M236 126 H257 M251 120 L257 126 L251 132" stroke="#9aa3ab" stroke-width="2" fill="none"/>'
sourcebody=image(OUT/'puppet-body-clean.webp',129,24,102,192,[8,15,211,395],fit='none')
canonical=image(ASSETS/'puppet-body-90-full.webp',129,24,102,192,[10,0,164,258],fit='none')
poster=frame+sourcebody;duration=2.6
motion=frame+'<g>'+envelope('1;1;0;0;1','0;.25;.5;.85;1',duration)+sourcebody+'</g>'
motion+='<g opacity="0">'+envelope('0;0;1;1;0','0;.25;.5;.85;1',duration)+canonical+'</g>'
placements=[((15,24,82,192),rgbview,False),((129,24,102,192),(8,15,211,395),True),((129,24,102,192),(10,0,164,258),True),((261,24,94,192),(0,56,175,446),True)]
anchors=[('#f5c444',[(77,37),(110,40),(137,25),(141,102)]),('#3297d3',[(79,134),(111,175),(108,108),(125,235)]),('#c35ab5',[(67,268),(116,380),(151,246),(130,401)])]
markers=[]
for color,pts in anchors:
 positions=[project(pt,*placement) for pt,placement in zip(pts,placements)]
 markers.append({'color':color,'rgb':positions[0],'observed_body':positions[1],'canonical_body':positions[2],'canonical_features':positions[3]})
 path=positions+[positions[-1],positions[-1]]
 motion+=f'<circle cx="{positions[0][0]}" cy="{positions[0][1]}" r="7" fill="{color}" stroke="white" stroke-width="1.8" opacity="0">'+envelope('0;1;1;0;0','0;.015;.83;.92;1',duration)
 for axis,attr in enumerate(['cx','cy']):
  coords=';'.join(str(pt[axis]) for pt in path)
  motion+=f'<animate attributeName="{attr}" values="{coords}" keyTimes="0;.25;.5;.75;.92;1" dur="{duration}s" calcMode="spline" keySplines=".35 0 .65 1;0 0 1 1;.35 0 .65 1;0 0 1 1;0 0 1 1" repeatCount="indefinite"/>'
 motion+='</circle>'
(OUT/'puppet-rgb-anchors.json').write_text(json.dumps({'duration_seconds':duration,'markers':markers},indent=2))
add('puppet','PuppetGait',poster,frame+canonical,'RGB 原图 → 3D body → 对齐后的特征。恢复滑动点演示；头、躯干与脚的标记从 RGB 人物出发，经过身体变换落在对应特征上。','原论文 Figure 2：RGB 输入、恢复的人体与规范化特征。','静态与动画均为同一尺寸；两种 3D body 固定在同一展示框。滑动全程由 4.2 秒缩短至 2.6 秒。',motion)
# 3. Explain tool creation, validation, and retention, rather than a video timestamp trace.
import xml.etree.ElementTree as ET
ET.register_namespace('', 'http://www.w3.org/2000/svg')
video_root=ET.fromstring(local('videoresearcher-tools.svg').read_text())
# Preserve the established agent icon and three authentic video frames only.
video_parts=[]
for child in video_root:
 tag=child.tag.split('}')[-1]
 if tag in ['image','svg'] or (tag=='g' and child.get('aria-label')=='Video agent'):
  video_parts.append(ET.tostring(child,encoding='unicode'))
video_fixed=''.join(video_parts)
video_fixed+='<path d="M180 108 V120 M174 114 L180 120 L186 114" stroke="#747b83" stroke-width="2" fill="none"/>'
video_fixed+='<rect x="0" y="126" width="360" height="77" rx="5" fill="#f2f4f6"/>'
video_fixed+=text('Build → Test → Reuse',180,232,22)
# Large, fixed-position states; no tiny code or timestamps.
build_icon='<g stroke="#1772d0" stroke-width="3" fill="none"><path d="M53 145 L42 156 L53 167 M77 145 L88 156 L77 167 M70 140 L59 173"/></g>'
build=build_icon+text('Build new tool',218,154,23)+text('Scene search',218,184,21,color='#555')
test='<path d="M43 159 L58 174 L88 140" stroke="#398064" stroke-width="4" fill="none"/>'+text('Test on video',218,154,23)+text('Validate evidence',218,184,21,color='#555')
reuse='<g fill="none" stroke="#1772d0" stroke-width="2.5"><rect x="40" y="145" width="49" height="35" rx="4"/><path d="M52 145 V137 H77 V145 M54 163 H75 M65 153 V173"/></g>'+text('Keep & reuse',218,154,23)+text('Toolbox +1',218,184,21,color='#1772d0')
poster=video_fixed+build
(OUT/'videoresearcher-tools.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="540" height="360" viewBox="0 0 360 240" role="img"><title>VideoResearcher: agents build new video tools, test them, and retain improvements</title><style>text{{font-family:Lato,Helvetica,Arial,sans-serif}}</style>{poster}</svg>')
body=video_fixed
# Sequential fades prevent overlapping words, while the layout stays fixed.
for content,values,times in [(build,'1;0;0;1','0;.22;.91;1'),(test,'0;0;1;1;0;0','0;.22;.3;.48;.57;1'),(reuse,'0;0;1;1;0;0','0;.57;.65;.83;.91;1')]:
 body+='<g>'+envelope(values,times,4.8)+content+'</g>'
# Building a tool immediately reveals its implementation; the subsequent states add validation and reuse.
for j,w in enumerate([25,38,31]):
 body+=f'<path d="M44 {182+j*5} h{w}" stroke="#1772d0" stroke-width="2" stroke-dasharray="{w}" stroke-dashoffset="{w}">'
 body+=f'<animate attributeName="stroke-dashoffset" values="{w};0;0;{w};{w}" keyTimes="0;.1;.16;.22;1" dur="4.8s" repeatCount="indefinite"/>'
 body+=envelope('1;1;0;0','0;.16;.22;1',4.8)+'</path>'
write_preview('videoresearcher',body,'VideoResearcher: build a scene-search tool, validate evidence, and add it to the toolbox')
manifest.append({'asset':'videoresearcher-evidence.svg','source':'https://arxiv.org/html/2609.19664v1, Section 3.3 and Figure 3','extra_information':'Illustrates tool development: implement scene search, validate on video, retain an accepted tool for reuse. Toolbox +1 is a schematic accepted update, not a measured result.','duration_seconds':4.8,'poster_hold_seconds':0,'starts_with_exact_static_image':'videoresearcher-tools.svg'})
# 4. Clue-OPSD: observed failure/success on the Grand Teton car-count question.
frames=[]
for j in range(6):
 f=text('How many cars passed?',180,24,22)+image(asset(f'clue-frame-{j}'),42,38,276,155)
 f+=text('Full video: 6 ✗',87,225,19,color='#b44b45')+text('Clue: 3 ✓',277,225,19,color='#26745b');frames.append(f)
save('clue',frames,'Clue-OPSD: sampled clue frames and the car-count answers','https://arxiv.org/html/2608.25356v1, Figure 1','Adds six sampled clue frames and actual full-video incorrect vs clue-only correct predictions.',1.5)
# 5. FoundationGait: fixed baseline, progressively drawn scaling performance.
import math
scaling=json.loads((OUT/'foundation-scaling-data.json').read_text())
parameters=scaling['parameters_millions'];scores=scaling['FoundationGait'];baseline=scaling['GaitSSB']
xs=[48+277*math.log(v/parameters[0])/math.log(parameters[-1]/parameters[0]) for v in parameters]
def scaling_y(value):return 182-(value-25)*4.8
def scaling_curve(values,color):
 points=' '.join(f'{x:.3f},{scaling_y(v):.3f}' for x,v in zip(xs,values))
 return f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'+''.join(f'<circle cx="{x:.3f}" cy="{scaling_y(v):.3f}" r="4.5" fill="{color}"/>' for x,v in zip(xs,values))
chart='<style>text{font-family:Lato,Helvetica,Arial,sans-serif}</style>'+text('Scaling on Gait3D',180,23,21,weight='700')+text('Rank-1 (%)',12,49,16,'start',color='#666')
for value in [30,40,50]:
 y=scaling_y(value)
 chart+=f'<path d="M48 {y}H325" stroke="#dce1e5" stroke-width="1"/>'+text(str(value),38,y+5,16,'end',color='#666')
for x,value in zip(xs,parameters):chart+=text(str(value)+'M',x,207,17,color='#555')
chart+=text('Parameters (log scale)',186,233,16,color='#666')
chart+=scaling_curve(baseline,'#939ba2')+text('Baseline (GaitSSB)',195,177,17,color='#666')+text('34.6',325,scaling_y(baseline[-1])-10,19,'end',color='#666')
chart+=text('FoundationGait',172,58,17,color='#1772d0')
chart+=f'<circle cx="48" cy="{scaling_y(scores[0])}" r="4.5" fill="#1772d0"/>'+text('32.5',48,scaling_y(scores[0])-12,19,color='#1772d0',weight='700')
poster_file('foundation-scaling.svg',chart,'FoundationGait: baseline scaling performance and the 6M starting point')
animated=chart+'<defs><clipPath id="foundation-growth"><rect x="48" y="60" width="0" height="130"><animate attributeName="width" from="0" to="284" dur="1.2s" fill="freeze"/></rect></clipPath></defs><g clip-path="url(#foundation-growth)">'+scaling_curve(scores,'#1772d0')+'</g>'
animated+='<g opacity="0"><animate attributeName="opacity" values="0;0;1" keyTimes="0;.9;1" dur="1.2s" fill="freeze"/>'+text('48.0',325,scaling_y(scores[-1])-12,21,'end',color='#1772d0',weight='700')+'</g>'
write_preview('foundation',animated,'FoundationGait: measured performance grows with model size against the fixed GaitSSB baseline')
manifest.append({'asset':'foundation-evidence.svg','source':scaling['source'],'extra_information':'Complete GaitSSB baseline stays visible. FoundationGait draws from 6M to 130M immediately on hover and holds its final curve. Logarithmic parameter axis, measured Figure 3 checkpoints; connecting lines are visual guides.','duration_seconds':1.2,'poster_hold_seconds':0,'starts_with_exact_static_image':'foundation-scaling.svg','parameters_millions':parameters,'FoundationGait':scores,'GaitSSB':baseline})
# 6. GaitMax: actual, spatially aligned part-attention maps from Figure 3.
# Native 32x64 RGB and attention outputs are preserved without invented motion.
# These are different part queries on ONE frame, not a temporal sequence.
gait_style='<style>text{font-family:Lato,Helvetica,Arial,sans-serif}</style>'
gait_input=image(asset('gaitmax-input'),16,12,104,208)+text('Input',68,236,17,color='#666')
gait_pairs=[]
for part,label in [('leg','Legs'),('foot','Feet'),('arm','Arms')]:
 gait_pairs.append(image(asset(f'gaitmax-{part}-left'),128,12,104,208)+image(asset(f'gaitmax-{part}-right'),240,12,104,208)+text(label,236,236,17,color='#666'))
gait_poster=gait_style+gait_input+gait_pairs[0]
poster_file('gaitmax-poses.svg',gait_poster,'GaitMax: RGB input and learned left/right leg attention')
# Immediate 0.25 s crossfade, then readable holds; returns to the exact cover.
gait_timing=[('1;0;0;0;0;1;1','0;.1;.36;.46;.72;.82;1'),('0;1;1;0;0;0;0','0;.1;.36;.46;.72;.82;1'),('0;0;0;1;1;0;0','0;.1;.36;.46;.72;.82;1')]
gait_body=gait_style+gait_input
for j,(values,times) in enumerate(gait_timing):
 gait_body+=f'<g opacity="{1 if j==0 else 0}">'+envelope(values,times,2.5)+gait_pairs[j]+'</g>'
write_preview('gaitmax',gait_body,'GaitMax: learned attention shifts between left/right legs, feet, and arms')
manifest.append({'asset':'gaitmax-evidence.svg','source':'GaitMax Figure 3, native RGB input and six learned part-attention outputs extracted from the official paper','extra_information':'The same input stays fixed while the two matching attention views cycle through legs, feet, and arms. These are actual part-query responses on one frame, not fabricated temporal trajectories. Native body scale and position remain identical.','duration_seconds':2.5,'poster_hold_seconds':0,'starts_with_exact_static_image':'gaitmax-poses.svg','native_source_resolution':[32,64]})
# 7. BiggerGait: original paper layer motifs, showing separate extraction and fusion.
# Four representative layers schematically stand for the sampled LVM layers.
# The final strips denote combined layer-wise distances, not measured feature maps.
bstyle='<style>text{font-family:Lato,Helvetica,Arial,sans-serif}</style>'
bbody=bstyle+text('LVM layers',76,229,17,color='#666')+text('Gait features',199,229,17,color='#666')+text('Fusion',319,229,17,color='#666')
bbody+=image(asset('bigger-input'),18,166,116,41)
bpaths=[];bcolors=['#d0a17a','#bf885c','#ad7040','#985a2f']
for j in range(4):
 y=30+j*34
 # Native green quadrilateral assets are stacked shallow-to-deep, bottom-up.
 bbody+=image(asset(f'bigger-layer-{3-j}'),18,y,116,41)
 path=f'M133 {y+11}C151 {y+11} 153 {y+31} 172 {y+31} M226 {y+31}C260 {y+31} 264 {78+j*24} 298 {78+j*24}'
 bpaths.append(path)
 bbody+=f'<path d="{path}" fill="none" stroke="#ccd0d2" stroke-width="1.6"/>'
 bbody+=f'<rect x="172" y="{y+22}" width="54" height="18" rx="2" fill="#e3e0dc"/>'
 bbody+=f'<rect x="298" y="{68+j*24}" width="42" height="20" rx="1" fill="#e3e0dc"/>'
poster_file('bigger-layer-scan.svg',bbody,'BiggerGait: multiple LVM layers feed separate gait features and a combined decision')
bactive=bbody
for j,(path,color) in enumerate(zip(bpaths,bcolors)):
 delay=j*.12
 bactive+=f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.6" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"><animate attributeName="stroke-dashoffset" from="1" to="0" begin="{delay:.2f}s" dur="0.7s" fill="freeze"/></path>'
 for x,y,w,h,begin in [(172,52+j*34,54,18,delay+.2),(298,68+j*24,42,20,delay+.58)]:
  bactive+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{color}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.16s" fill="freeze"/></rect>'
write_preview('biggergait',bactive,'BiggerGait: complementary intermediate layers are extracted separately and combined')
manifest.append({'asset':'biggergait-evidence.svg','source':'BiggerGait Figures 1(c), 2 and Section 3.5; native input and layer planes extracted from Figure 1','extra_information':'Schematic representative layers feed separate gait representations, then contribute to a combined decision. Uses original paper RGB input and layer motifs. Colored strips are conceptual layer contributions, not measured feature maps or a claimed learned fusion module. Section 3.5 ensembles layer-wise distances by averaging. Starts at the static diagram, immediately traces contributions, holds the combined result.','duration_seconds':1.1,'poster_hold_seconds':0,'starts_with_exact_static_image':'bigger-layer-scan.svg'})
# 8. SapiensID: one fixed reference, actual matching and nonmatching evidence.
# Figure 7 supplies both photo pairs and corresponding part-similarity maps.
# Keep all image slots unchanged through the transition; no synthetic motion.
ss_style='<style>text{font-family:Lato,Helvetica,Arial,sans-serif}</style>'
ss_fixed=ss_style+image(asset('sapiens-reference'),12,12,104,195)
ss_states=[]
for case,label,color in [('same','Same person','#26745b'),('different','Different people','#a65a50')]:
 state=image(asset(f'sapiens-{case}'),124,12,104,195)+image(asset(f'sapiens-{case}-map'),244,12,104,195)
 # Omit tiny original numerical annotations; retain the actual body/face maps.
 state+='<rect x="244" y="12" width="52" height="29" fill="white"/><rect x="244" y="193" width="104" height="14" fill="white"/>'
 state+=text(label,180,233,19,color=color)
 ss_states.append(state)
poster_file('sapiens-scales.svg',ss_fixed+ss_states[0],'SapiensID: same person across portrait and full-body views with part similarities')
ss_anim=ss_fixed
for j,(values,times) in enumerate([('1;0;0;1;1','0;.125;.5;.625;1'),('0;1;1;0;0','0;.125;.5;.625;1')]):
 ss_anim+=f'<g opacity="{1 if j==0 else 0}">'+envelope(values,times,2.4)+ss_states[j]+'</g>'
write_preview('sapiensid',ss_anim,'SapiensID: matching across pose and scale versus a different person, with real part-similarity evidence')
manifest.append({'asset':'sapiensid-evidence.svg','source':'SapiensID Figure 7, upper-right and lower-right pairs; original raster panels from page 8','extra_information':'Fixed portrait reference. The candidate and its corresponding part-similarity map switch together between the same person in a different pose/scale and a different person. Original similarities and imagery are preserved; tiny numeric annotations are hidden for thumbnail legibility. This is actual paper evidence, not generated heatmaps.','duration_seconds':2.4,'poster_hold_seconds':0,'starts_with_exact_static_image':'sapiens-scales.svg'})
# 9. BigGait restores its original walking/feature animation.
manifest.append({'asset':'biggait-original-loop.webp','source':'Original data/projects/2024-BigGait.webp, concluding walking sequence','extra_information':'RGB and all-purpose, silhouette, parsing, and skeleton representations from the original animation. Reflowed to 3:2 without stretching.','duration_seconds':0.76,'starts_with_exact_static_image':'biggait-original-poster.webp','poster_hold_seconds':0})
# 10. GaitEditer: thirteen real attribute/view edits, each with its matched original.
# PDF image order differs from column order; mappings are verified by page coordinates.
ge_cases=json.loads((OUT/'gaitediter-edit-cases.json').read_text())['cases']
ge_fixed='<style>text{font-family:Lato,Helvetica,Arial,sans-serif}</style><rect x="18" y="12" width="142" height="206" fill="black"/><rect x="200" y="12" width="142" height="206" fill="black"/>'+text('Original',89,236,18,color='#666')
ge_fixed+='<path d="M169 115H191M185 109L191 115L185 121" fill="none" stroke="#929aa0" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
ge_states=[]
for case in ge_cases:
 ge_states.append(image(asset(f"gaitediter-native-{case['original']:02}"),23,19,132,192)+image(asset(f"gaitediter-native-{case['edited']:02}"),205,19,132,192)+text(case['label'],271,236,18,color='#666'))
poster_file('gaitediter-edit.svg',ge_fixed+ge_states[0],'GaitEditer: original silhouette and a pronounced combined outfit edit')
# Each 0.72 s step adds a distinct real edit; 0.16 s crossfades, no initial hold.
ge_step=.72;ge_fade=.16;ge_total=len(ge_states)*ge_step
ge_anim=ge_fixed
for j,state in enumerate(ge_states):
 if j==0:
  timing=[0,ge_fade,ge_total-ge_step,ge_total-ge_step+ge_fade,ge_total];values=[1,0,0,1,1]
 else:
  begin=(j-1)*ge_step;end=j*ge_step
  pairs=[(0,0)]
  if begin>0:pairs.append((begin,0))
  pairs.extend([(begin+ge_fade,1),(end,1),(end+ge_fade,0),(ge_total,0)])
  timing=[t for t,v in pairs];values=[v for t,v in pairs]
 ge_anim+=f'<g opacity="{1 if j==0 else 0}">'+envelope(';'.join(map(str,values)),';'.join(f'{t/ge_total:.6f}' for t in timing),ge_total)+state+'</g>'
write_preview('gaitediter',ge_anim,'GaitEditer: thirteen native clothing, appearance and viewpoint edits with matched originals')
manifest.append({'asset':'gaitediter-evidence.svg','source':'GaitEditer v1 Figure 7; PDF image placements verified against labels','extra_information':'Thirteen real edits: skirt, hat/jacket/pants outfit, hat, 60-to-195 and 60-to-270 degree views, size, hoodie, hair, jacket, female, younger, older, and pants. The left original changes only when the source subject changes; every before/after pair uses native 44x64 geometry. No exaggerated or fabricated shapes.','duration_seconds':round(ge_total,2),'poster_hold_seconds':0,'starts_with_exact_static_image':'gaitediter-edit.svg','cases':'gaitediter-edit-cases.json'})
(OUT/'hover-evidence.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
# Bind the additional content while retaining every approved static thumbnail.
i=ROOT/'index.html';s=i.read_text();rows=list(re.finditer(r'<div class="research-media[^\n]+',s));assert len(rows)==12
stems={1:'idworld',2:'puppet',3:'videoresearcher',4:'clue',6:'foundation',7:'gaitmax',8:'biggergait',9:'sapiensid',10:'biggait',11:'gaitediter'}
for idx in reversed(range(12)):
 if idx not in stems:continue
 m=rows[idx];t=m.group();t=re.sub(r' (?:data-still|data-animated|tabindex|role|aria-label|aria-pressed)="[^"]*"','',t)
 still=re.search(r' src="([^"]+)"',t).group(1);stem=stems[idx]
 if stem=='idworld':
  newstill='data/projects/teasers/idworld-pixel-reference.svg?v=12'
  t=t.replace('src="'+still+'"','src="'+newstill+'"');still=newstill
  t=re.sub(r'alt="[^"]*"','alt="IDWorld: size-aligned side and back pixel references reveal predicted latent features"',t)
 if stem=='puppet':
  newstill='data/projects/teasers/puppet-body-alignment.svg?v=11'
  t=t.replace('src="'+still+'"','src="'+newstill+'"');still=newstill
  t=re.sub(r'alt="[^"]*"','alt="PuppetGait: RGB input, 3D body, and canonical features with fast correspondence markers"',t)
 if stem=='gaitediter':
  newstill='data/projects/teasers/gaitediter-edit.svg?v=3'
  t=t.replace('src="'+still+'"','src="'+newstill+'"');still=newstill
  t=re.sub(r'alt="[^"]*"','alt="GaitEditer: thirteen clothing, appearance, and viewpoint edits with matched original silhouettes"',t)
 if stem=='sapiensid':
  newstill='data/projects/teasers/sapiens-scales.svg?v=2'
  t=t.replace('src="'+still+'"','src="'+newstill+'"');still=newstill
  t=re.sub(r'alt="[^"]*"','alt="SapiensID: fixed portrait, matching or different person, and corresponding part similarity"',t)
 if stem=='biggergait':
  newstill='data/projects/teasers/bigger-layer-scan.svg?v=4'
  t=t.replace('src="'+still+'"','src="'+newstill+'"');still=newstill
  t=re.sub(r'alt="[^"]*"','alt="BiggerGait: complementary LVM layers feed separate gait features and a combined decision"',t)
 if stem=='gaitmax':
  newstill='data/projects/teasers/gaitmax-poses.svg?v=2'
  t=t.replace('src="'+still+'"','src="'+newstill+'"');still=newstill
  t=re.sub(r'alt="[^"]*"','alt="GaitMax: one RGB input with aligned left and right body-part attention maps"',t)
 if stem=='foundation':
  t=re.sub(r'alt="[^"]*"','alt="FoundationGait: performance scales from 6M to 130M against the fixed GaitSSB baseline"',t)
  newstill='data/projects/teasers/foundation-scaling.svg?v=4'
  t=t.replace('src="'+still+'"','src="'+newstill+'"');still=newstill
 if stem=='biggait':
  newstill='data/projects/teasers/biggait-original-poster.webp?v=3'
  t=t.replace('src="'+still+'"','src="'+newstill+'"');still=newstill
  t=re.sub(r'alt="[^"]*"','alt="BigGait: original walking sequence and four visual representations"',t)
 preview_version={'idworld':18,'puppet':19,'clue':11,'foundation':13,'gaitmax':11,'biggergait':13,'sapiensid':11,'gaitediter':12,'videoresearcher':12}.get(stem,10)
 t=t.replace('/></div>',f' data-still="{still}" data-animated="data/projects/teasers/{stem}-evidence.svg?v={preview_version}" tabindex="0" role="button" aria-label="Show additional {stem} evidence" aria-pressed="false"/></div>')
 if stem=='biggait':t=t.replace('data/projects/teasers/biggait-evidence.svg?v=10','data/projects/teasers/biggait-original-loop.webp?v=3')
 s=s[:m.start()]+t+s[m.end():]
i.write_text(s)
print('Built 10 evidence-based hover previews; retained 2 real-video GIFs.')
