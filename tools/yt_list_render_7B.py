import subprocess, sys, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
D=os.path.dirname(os.path.abspath(__file__)); SIX=os.path.join(os.path.dirname(D),'six')
W,H,FPS=1080,1920,30
WHITE=(245,242,236); GOLD=(222,184,105); RED=(220,20,20)
F=lambda w,s: ImageFont.truetype(f"{SIX}/ebg-{w}.ttf",s)
PB=lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",s)
f_hook,f_q,f_g,f_sm,f_num=F("600-normal",132),F("600-normal",104),F("500-normal",80),F("500-normal",34),F("600-normal",120)
L=json.load(open(f"{D}/lists.json"))[int(sys.argv[1])]; out=sys.argv[2]; bgp=sys.argv[3]
# background grade: mono + warm tint, dark
src=Image.open(bgp).convert('L'); src=ImageOps.colorize(src,(0,0,0),(255,214,150)).convert('RGB')
src=ImageEnhance.Brightness(src).enhance(0.95)
sc=max(W*1.15/src.width,H*1.15/src.height); BIG=src.resize((int(src.width*sc),int(src.height*sc)),Image.LANCZOS)
vig=Image.new('L',(W,H),0); dv=ImageDraw.Draw(vig)
for i in range(60): dv.rectangle((i*6,i*9,W-i*6,H-i*9),fill=int(255*min(1,0.35+i/30)))
vig=vig.filter(ImageFilter.GaussianBlur(80))
def bg(gt,total,dim=1.0):
    z=1.0+0.13*(gt/total); w,h=int(W*1.15/1.15*z/1.0*BIG.width/(W*1.15)*1.0),0
    cw,ch=int(BIG.width/z),int(BIG.height/z)
    x0,y0=(BIG.width-cw)//2,(BIG.height-ch)//2
    im=BIG.crop((x0,y0,x0+cw,y0+ch)).resize((W,H),Image.BILINEAR)
    black=Image.new('RGB',(W,H),(0,0,0))
    im=Image.composite(im,black,vig)
    if dim<1: im=ImageEnhance.Brightness(im).enhance(dim)
    return im
def wrap(d,text,font,maxw=960):
    lines,cur=[], ""
    for w in text.split():
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    return lines+[cur]
N=len(L["items"])
scenes=[(2.0,[(L["hook1"],f_hook,WHITE,0,0),(L["hook2"],f_hook,GOLD,70,0),(L["tease"],f_g,GOLD,0,0.5)])]
for i,(a,b) in enumerate(L["items"]):
    scenes.append((2.4,[("#"+str(N-i),f_num,GOLD,30,0),(a,f_q,WHITE,60,0),(b,f_g,GOLD,0,0.6)]))
END=2.4; total=sum(s[0] for s in scenes)+END
def txt(im,xy,s,font,fill,alpha):
    sh=Image.new('RGBA',im.size,(0,0,0,0)); ds=ImageDraw.Draw(sh)
    ds.text((xy[0]+4,xy[1]+6),s,font=font,fill=(0,0,0,int(220*alpha)),anchor="mm")
    sh=sh.filter(ImageFilter.GaussianBlur(6)); im.paste(sh,(0,0),sh)
    d=ImageDraw.Draw(im); c=tuple(int(fill[k]*alpha) for k in range(3))
    d.text(xy,s,font=font,fill=c,anchor="mm")
def frame(blocks,t,gt):
    im=bg(gt,total); d=ImageDraw.Draw(im)
    d.text((W/2,140),"LEGENDCHIL",font=f_sm,fill=(150,128,90),anchor="mm")
    laid=[(wrap(d,tx,fo),fo,c,g,dl,int(fo.size*1.12)) for tx,fo,c,g,dl in blocks]
    y=(H-sum(len(l)*lh+g for l,_,_,g,_,lh in laid))/2-30
    for lines,fo,col,gap,dl,lh in laid:
        a=max(0.,min(1.,(t-dl)/0.15))
        for ln in lines:
            if a>0:
                # pop-in scale feel via vertical slide
                txt(im,(W/2,y+lh/2+(1-a)*24),ln,fo,col,a)
            y+=lh
        y+=gap
    return im
def endcard(t,gt):
    im=bg(gt,total,0.6); d=ImageDraw.Draw(im)
    txt(im,(W/2,680),"Want to read people",f_q,WHITE,1)
    txt(im,(W/2,800),"before they read you?",f_q,GOLD,1)
    s=1+0.06*max(0,1-abs((t%0.923)-0.1)/0.15)
    bw,bh=int(620*s),int(170*s); x0,y0=(W-bw)//2,1010-bh//2
    d=ImageDraw.Draw(im); d.rounded_rectangle((x0,y0,x0+bw,y0+bh),radius=bh//2,fill=RED)
    d.text((W/2,1010),"SUBSCRIBE",font=PB(int(74*s)),fill=(255,255,255),anchor="mm")
    txt(im,(W/2,1180),"A new one every day.",f_g,WHITE,1)
    if t>0.6:
        cx,cy=W/2+170,1045; d.polygon([(cx,cy),(cx,cy+70),(cx+18,cy+52),(cx+34,cy+86),(cx+46,cy+80),(cx+30,cy+46),(cx+54,cy+46)],fill=(255,255,255),outline=(0,0,0))
    return im
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-i",f"{D}/phonk.wav","-filter:a","volume=-6dB,afade=t=out:st=%.2f:d=0.5"%(total-0.5),"-t",f"{total}",
  "-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",out],stdin=subprocess.PIPE)
gt=0
for dur,bl in scenes:
    for n in range(int(dur*FPS)): p.stdin.write(frame(bl,n/FPS,gt).tobytes()); gt+=1/FPS
for n in range(int(END*FPS)): p.stdin.write(endcard(n/FPS,gt).tobytes()); gt+=1/FPS
p.stdin.close(); p.wait(); print(out,total)
