"""Reflow the original BigGait walking animation into the homepage's 3:2 frame."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/projects/2024-BigGait.webp';out=ROOT/'data/projects/teasers'
im=Image.open(source)
# Use the original concluding walking/feature sequence, retaining all five
# representations. Start on a fully revealed frame and remove the multi-second
# title/end holds; no invented intermediate features or new person imagery.
# Frame 179 is an end-title card: exclude it to prevent the white flash.
indices=list(range(160,179))
boxes=[(28,100,130,303),(277,100,379,303),(529,90,631,294),(681,88,783,292),(834,86,938,294)]
slots=[(45,12,108,216),(199,12,52,104),(263,12,52,104),(199,124,52,104),(263,124,52,104)]
frames=[]
for idx in indices:
 im.seek(idx);raw=im.convert('RGB');canvas=Image.new('RGB',(360,240),'#f4f4f4');draw=ImageDraw.Draw(canvas)
 draw.line([(165,120),(187,120)],fill='#929aa0',width=2);draw.line([(182,115),(187,120),(182,125)],fill='#929aa0',width=2)
 for box,(x,y,w,h) in zip(boxes,slots):
  f=raw.crop(box);scale=min(w/f.width,h/f.height);f=f.resize((round(f.width*scale),round(f.height*scale)),Image.LANCZOS);canvas.paste(f,(x+(w-f.width)//2,y+(h-f.height)//2))
 frames.append(canvas)
# Encode once, then derive the cover from its decoded first frame for an exact
# match on hover, including compression. 40 ms vs original 70 ms frame delays.
dest=out/'biggait-original-loop.webp'
frames[0].save(dest,save_all=True,append_images=frames[1:],duration=40,loop=0,quality=78,method=6)
first=Image.open(dest);first.seek(0);first.save(out/'biggait-original-poster.webp',lossless=True,method=6)
(out/'biggait-original-preview.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'source_frames':indices,'crop_boxes':boxes,'duration_ms':40,'display':'RGB input and four original representations; original pixels reflowed into 3:2','bytes':dest.stat().st_size},indent=2)+'\n')
print(dest.stat().st_size,'bytes')
