import sys,subprocess,os
from PIL import Image,ImageDraw,ImageFont,ImageChops
src=open(f"{os.environ['S']}/posts/build.py").read().split("posts=[]")[0]
exec(src)   # PAL,FACTS,GIRLS,wrap,ILL,prep_ill,B,M
W2,H2,FPS=1080,1920,30
SIX=f"{os.environ['S']}/ytw/six"
GOLD=(184,151,90);RED=(220,20,20);WHITE=(238,236,232);BG=(10,10,10)
EB=lambda s:ImageFont.truetype(f"{SIX}/ebg-500-normal.ttf",s)
PB=lambda s:ImageFont.truetype(B,s)
def slide_v(tag,head,body,c,ill):
    p=PAL[c]; im=Image.new("RGB",(W2,H2),p["bg"]); d=ImageDraw.Draw(im)
    ft=PB(34); tw=d.textlength(tag,font=ft)+80
    d.rectangle((W2/2-tw/2,200,W2/2+tw/2,270),fill=(15,15,15)); d.text((W2/2,235),tag,font=ft,fill=(255,255,255),anchor="mm")
    f1=PB(104); f2=ImageFont.truetype(M,50)
    l1=wrap(d,head,f1,W2-140); l2=wrap(d,body,f2,W2-140); y=340
    for ln in l1: d.text((70,y),ln,font=f1,fill=p["fg"]); y+=124
    y+=34
    for ln in l2: d.text((70,y),ln,font=f2,fill=p["fg"]); y+=68
    g=prep_ill(ill); top=y+40; bh=1560-top; bw=W2-80
    k=min(bh/g.height,bw/g.width); g=g.resize((int(g.width*k),int(g.height*k)),Image.LANCZOS)
    x=(W2-g.width)//2; yy=top+(bh-g.height)//2
    reg=im.crop((x,yy,x+g.width,yy+g.height)); im.paste(ImageChops.multiply(reg,g.convert("RGB")),(x,yy))
    return im
def endcard(t):
    im=Image.new("RGB",(W2,H2),BG); d=ImageDraw.Draw(im)
    d.text((W2/2,150),"LEGENDCHIL",font=ImageFont.truetype(f"{SIX}/ebg-500-normal.ttf",30),fill=(120,104,72),anchor="mm")
    d.text((W2/2,700),"Want to read people",font=EB(76),fill=WHITE,anchor="mm")
    d.text((W2/2,800),"before they read you?",font=EB(76),fill=GOLD,anchor="mm")
    s=1+0.06*max(0,1-abs((t%0.923)-0.1)/0.15); bw,bh=int(560*s),int(150*s); x0,y0=(W2-bw)//2,980-bh//2
    d.rounded_rectangle((x0,y0,x0+bw,y0+bh),radius=bh//2,fill=RED)
    d.text((W2/2,980),"SUBSCRIBE",font=PB(int(66*s)),fill=(255,255,255),anchor="mm")
    d.text((W2/2,1130),"A new one every day.",font=EB(64),fill=WHITE,anchor="mm")
    if t>0.6:
        cx,cy=W2/2+150,1010; d.polygon([(cx,cy),(cx,cy+70),(cx+18,cy+52),(cx+34,cy+86),(cx+46,cy+80),(cx+30,cy+46),(cx+54,cy+46)],fill=(255,255,255),outline=BG)
    return im
def make(ser,i,c,out):
    tag="PSYCHOLOGY SAYS" if ser=="facts" else "PSYCHOLOGY ABOUT GIRLS"
    h,b=(FACTS if ser=="facts" else GIRLS)[i]; base=slide_v(tag,h,b,c,ILL[(ser,i)])
    A,TOT=8.4,12.0
    p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W2}x{H2}","-r",str(FPS),"-i","-",
      "-i",f"{os.environ['S']}/ytw/tools/phonk.wav","-filter:a","volume=-6dB,afade=t=out:st=%.2f:d=0.5"%(TOT-0.5),"-t",str(TOT),
      "-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",out],stdin=subprocess.PIPE)
    for n in range(int(A*FPS)):
        z=1+0.05*n/(A*FPS); w,h=int(W2/z),int(H2/z); x,y=(W2-w)//2,(H2-h)//2
        p.stdin.write(base.crop((x,y,x+w,y+h)).resize((W2,H2),Image.BILINEAR).tobytes())
    for n in range(int((TOT-A)*FPS)): p.stdin.write(endcard(n/FPS).tobytes())
    p.stdin.close(); p.wait(); print(out)
if __name__=="__main__":
    make(sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4])
