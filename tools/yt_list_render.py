import subprocess, sys, os, json
from PIL import Image, ImageDraw, ImageFont
D=os.path.dirname(os.path.abspath(__file__)); SIX=os.path.join(os.path.dirname(D),'six')
W,H,FPS=1080,1920,30
BG=(10,10,10); WHITE=(238,236,232); GOLD=(184,151,90); DIM=(120,104,72); RED=(220,20,20)
F=lambda w,s: ImageFont.truetype(f"{SIX}/ebg-{w}.ttf",s)
PB=lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",s)
f_hook,f_q,f_g,f_sm,f_num=F("600-normal",92),F("500-normal",76),F("500-normal",64),F("500-normal",30),F("600-normal",60)
L=json.load(open(f"{D}/lists.json"))[int(sys.argv[1])]
def wrap(d,text,font,maxw=920):
    if "\n" in text: return text.split("\n")
    lines,cur=[], ""
    for w in text.split():
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    return lines+[cur]
scenes=[(1.6,[(L["hook1"],f_hook,WHITE,0,0),(L["hook2"],f_hook,GOLD,60,0),(L["tease"],f_g,GOLD,0,0.5)])]
for i,(a,b) in enumerate(L["items"],1):
    scenes.append((1.6,[(str(i),f_num,GOLD,40,0),(a,f_q,WHITE,50,0),(b,f_g,GOLD,0,0.5)]))
END=2.4
def frame(blocks,t):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    d.text((W/2,150),"LEGENDCHIL",font=f_sm,fill=DIM,anchor="mm")
    laid=[(wrap(d,tx,fo),fo,c,g,dl,int(fo.size*1.18)) for tx,fo,c,g,dl in blocks]
    y=(H-sum(len(l)*lh+g for l,_,_,g,_,lh in laid))/2-40
    for lines,fo,col,gap,dl,lh in laid:
        a=max(0.,min(1.,(t-dl)/0.18))
        c=tuple(int(BG[k]+(col[k]-BG[k])*a) for k in range(3))
        for ln in lines:
            if a>0: d.text((W/2,y+lh/2+(1-a)*14),ln,font=fo,fill=c,anchor="mm")
            y+=lh
        y+=gap
    d.line([(W/2-28,y+30),(W/2+28,y+30)],fill=GOLD,width=2)
    return im
def endcard(t):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    d.text((W/2,150),"LEGENDCHIL",font=f_sm,fill=DIM,anchor="mm")
    d.text((W/2,700),"Want to read people",font=f_q,fill=WHITE,anchor="mm")
    d.text((W/2,800),"before they read you?",font=f_q,fill=GOLD,anchor="mm")
    s=1+0.06*max(0,1-abs((t%0.923)-0.1)/0.15)  # beat pulse
    bw,bh=int(560*s),int(150*s); x0,y0=(W-bw)//2,980-bh//2
    d.rounded_rectangle((x0,y0,x0+bw,y0+bh),radius=bh//2,fill=RED)
    d.text((W/2,980),"SUBSCRIBE",font=PB(int(66*s)),fill=(255,255,255),anchor="mm")
    d.text((W/2,1130),"A new one every day.",font=f_g,fill=WHITE,anchor="mm")
    # cursor tap
    if t>0.6:
        cx,cy=W/2+150,1010; d.polygon([(cx,cy),(cx,cy+70),(cx+18,cy+52),(cx+34,cy+86),(cx+46,cy+80),(cx+30,cy+46),(cx+54,cy+46)],fill=(255,255,255),outline=BG)
    return im
out=sys.argv[2]; total=sum(s[0] for s in scenes)+END
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-i",f"{D}/phonk.wav","-filter:a","volume=-6dB,afade=t=out:st=%.2f:d=0.5"%(total-0.5),"-t",f"{total}",
  "-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",out],stdin=subprocess.PIPE)
for dur,bl in scenes:
    for n in range(int(dur*FPS)): p.stdin.write(frame(bl,n/FPS).tobytes())
for n in range(int(END*FPS)): p.stdin.write(endcard(n/FPS).tobytes())
p.stdin.close(); p.wait(); print(out,total)
