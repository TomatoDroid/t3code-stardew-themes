import base64, io, os, shutil
from PIL import Image
SRC=os.path.dirname(os.path.abspath(__file__))
A=os.path.join(SRC,'wiki-assets','')
OUT=os.path.join(SRC,'themes','')
def uri(im, fmt='PNG', colors=None, **kw):
    if colors: im = im.convert('RGBA').quantize(colors, method=Image.Quantize.FASTOCTREE)
    b=io.BytesIO(); im.save(b, fmt, optimize=True, **kw)
    mime={'PNG':'image/png','JPEG':'image/jpeg','GIF':'image/gif'}[fmt]
    return 'data:%s;base64,%s'%(mime, base64.b64encode(b.getvalue()).decode())
def raw(name, mime='image/png'):
    return 'data:%s;base64,%s'%(mime, base64.b64encode(open(A+name,'rb').read()).decode())
def bbox_split_rows(im):
    a=im.split()[3]; rows=[any(a.getpixel((x,y)) for x in range(im.width)) for y in range(im.height)]
    segs=[];s=None
    for y,r in enumerate(rows+[False]):
        if r and s is None: s=y
        if not r and s is not None: segs.append((s,y)); s=None
    return segs
def build():
    out={}
    lz=Image.open(A+'Main_Logo_ZH.png').convert('RGBA'); h=60; lz=lz.resize((int(lz.width*h/lz.height),h),Image.LANCZOS)
    out['logo']=uri(lz,colors=48); out['logo_w']=lz.width/2
    out['menu']=raw('Menu_border.png')
    f=Image.open(A+'Fishing.png').convert('RGBA'); segs=bbox_split_rows(f)
    bob=f.crop((0,segs[0][0],f.width,segs[0][1])); bob=bob.crop(bob.getbbox()); out['bobber']=uri(bob)
    fish=f.crop((0,segs[-1][0],f.width,segs[-1][1])); fish=fish.crop(fish.getbbox()); out['fish']=uri(fish)
    out['pole']=raw('Bamboo_Pole.png')
    out['stardrop']=uri(Image.open(A+'Stardrop.png').convert('RGBA'),colors=24)
    out['junimo']=raw('Junimo.gif','image/gif')
    bl=Image.open(A+'Banner_Left.png').convert('RGBA'); bl=bl.crop(bl.getbbox()); w=188; bl=bl.resize((w,int(bl.height*w/bl.width)),Image.LANCZOS)
    out['coop']=uri(bl,colors=32); out['coop_h']=bl.height
    return out
def backgrounds():
    """Write the one background image each theme ships beside its JSON file."""
    os.makedirs(OUT,exist_ok=True)
    b=Image.open(A+'Beach_Overview.jpg').convert('RGB')
    b.crop((476,565,1107,952)).save(OUT+'stardew-island.jpg',quality=92)
    shutil.copyfile(os.path.join(SRC,'art','cover-background.png'),OUT+'stardew-cover.png')
    import farm; farm.build(OUT+'stardew-menu.png')
if __name__=='__main__':
    o=build(); print({k:(len(v) if isinstance(v,str) else v) for k,v in o.items()})
    backgrounds()
