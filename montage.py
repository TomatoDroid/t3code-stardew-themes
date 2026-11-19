"""Tile screenshots into one sheet: python montage.py out.png a.png b.png ... (2 columns)."""
import sys
from PIL import Image
out,files=sys.argv[1],sys.argv[2:]
ims=[Image.open(f).convert('RGB') for f in files]
w,h=ims[0].size; cols=2; rows=(len(ims)+1)//2; g=12
sheet=Image.new('RGB',(cols*w+g*(cols-1),rows*h+g*(rows-1)),'#202020')
for i,im in enumerate(ims): sheet.paste(im.resize((w,h)),((i%cols)*(w+g),(i//cols)*(h+g)))
sheet.save(out)
