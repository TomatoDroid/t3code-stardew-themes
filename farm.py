import os
from PIL import Image
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'wiki-assets-farm','')
def build(dest):
    m=Image.open(D+'Standard_Farm.png').convert('RGBA')
    X0,Y0,W,H=834,118,256,168
    s=m.crop((X0,Y0,X0+W,Y0+H))
    clean=m.crop((1128,262,1144,278))
    # soil patch from Sprinkler_Range (4x) right patch
    sp=Image.open(D+'Sprinkler_Range.png').convert('RGBA')
    sp=sp.resize((sp.width//4,sp.height//4),Image.NEAREST)
    px=sp.load()
    def brown(c): r,g,b,a=c; return r<215 and g<140
    # find bbox of right patch
    xs=[x for x in range(sp.width*6//10,sp.width) for y in range(sp.height) if brown(px[x,y])]
    ys=[y for x in range(sp.width*6//10,sp.width) for y in range(sp.height) if brown(px[x,y])]
    bx=(min(xs),min(ys),max(xs)+1,max(ys)+1)
    patch=sp.crop(bx); pp=patch.load()
    cx,cy=patch.width//2,patch.height//2
    for x in range(patch.width):
        for y in range(patch.height):
            inner=abs(x-cx)<=11 and abs(y-cy)<=14
            if inner or not brown(pp[x,y]): pp[x,y]=(0,0,0,0)
    # solid soil fill for centre from a soil tile
    tile=sp.crop((bx[0]+6,bx[1]+6,bx[0]+22,bx[1]+22))
    fx,fy=840-X0,192-Y0  # field origin
    base=Image.new('RGBA',patch.size,(0,0,0,0))
    for i in range(0,patch.width,16):
        for j in range(0,patch.height,16): base.paste(clean,(i,j))
    s.paste(base,(fx,fy)); 
    ct=Image.new('RGBA',(26,30),(0,0,0,0))
    for i in (0,13):
        for j in (0,15): ct.paste(tile.crop((0,0,13,15)),(i,j))
    s.paste(ct,(fx+cx-12,fy+cy-15))
    s.alpha_composite(patch,(fx,fy))
    def spr(n,k=3):
        im=Image.open(D+n+'.png').convert('RGBA'); return im.resize((round(im.width/k),round(im.height/k)),Image.NEAREST)
    rows=['Pumpkin_Stage_6','Melon_Stage_6','Cauliflower_Stage_6','Strawberry_Stage_7','Parsnip_Stage_5']
    tw=patch.width/5; th=patch.height/5
    for r,n in enumerate(rows):
        c=spr(n)
        for col in range(5):
            x=int(fx+col*tw+(tw-c.width)/2); y=int(fy+(r+1)*th-c.height-1)
            s.alpha_composite(c,(x,y))
    sc=spr('Scarecrow'); s.alpha_composite(sc,(fx+patch.width+3,fy+30))
    ch=spr('White_Chicken'); s.alpha_composite(ch,(196,150))
    s.convert('RGB').resize((W*3,H*3),Image.NEAREST).save(dest)
if __name__=='__main__':
    build(os.path.join(os.path.dirname(os.path.abspath(__file__)),'themes','stardew-menu.png'))
