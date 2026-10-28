"""Formato C — YouTube Shorts: silhueta + gancho (0-3s) -> corte seco -> revelação (3-7.4s), loop.
uso: python3 yt_c_render.py BG.jpg "hook com *chave*" "reveal com *chave*" out.mp4"""
import sys, os, subprocess, tempfile, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
D=os.path.dirname(os.path.abspath(__file__))
W,H,FPS=1080,1920,30; DUR=7.385; CUT=3.0
Y=(236,221,30); WH=(255,255,255); GOLD=(200,163,97)
F=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',s)
FM=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf',s)
def wrap(d,words,f,maxw):
    L,c=[],[]
    for w in words:
        t=c+[w]
        if d.textlength(' '.join(x for x,_ in t),font=f)<=maxw: c=t
        else: L.append(c); c=[w]
    return L+[c]
def text(im,s,cy,sizes=(92,84,76,68),maxw=900,maxl=4):
    d=ImageDraw.Draw(im); words=[(w.replace('*',''),'*' in w) for w in s.split()]
    for sz in sizes:
        f=F(sz); L=wrap(d,words,f,maxw)
        if len(L)<=maxl: break
    lh=int(sz*1.22); y0=cy-lh*len(L)/2
    for i,ln in enumerate(L):
        tw=d.textlength(' '.join(x for x,_ in ln),font=f); x=(W-tw)/2; y=y0+i*lh
        for w,k in ln:
            d.text((x,y),w,font=f,fill=Y if k else WH,stroke_width=4,stroke_fill=(0,0,0)); x+=d.textlength(w+' ',font=f)
def base(bg,dark,blur=0):
    im=ImageOps.fit(Image.open(bg).convert('RGB'),(W,H),Image.LANCZOS)
    im=ImageEnhance.Color(im).enhance(0.15); im=ImageEnhance.Brightness(im).enhance(dark)
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    g=Image.new('L',(1,H)); 
    for y in range(H): g.putpixel((0,y),int(170*max(0,(y-H*0.35)/(H*0.65))))
    im=Image.composite(Image.new('RGB',(W,H)),im,g.resize((W,H)))
    return im
def frames(bg,hook,rev):
    a=base(bg,0.75); d=ImageDraw.Draw(a)
    d.text((W/2,300),'PSYCHOLOGY SAYS…',font=FM(44),fill=GOLD,anchor='mm')
    text(a,hook,1180)
    b=base(bg,0.45,6); text(b,rev,960,sizes=(100,92,84,76))
    for im in (a,b):
        ImageDraw.Draw(im).text((W/2,H-150),'@legendchil',font=FM(36),fill=(170,170,170),anchor='mm')
    return a,b
def zoom(im,z):
    w,h=int(W*z),int(H*z); r=im.resize((w,h),Image.BILINEAR); x=(w-W)//2; y=(h-H)//2
    return r.crop((x,y,x+W,y+H))
if __name__=='__main__':
    bg,hook,rev,out=sys.argv[1:5]
    a,b=frames(bg,hook,rev); tmp=tempfile.mkdtemp()
    wav=f'{tmp}/a.wav'; subprocess.run([sys.executable,'-I',f'{D}/phonk_synth.py',wav,str(DUR)],check=True)
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',wav,
        '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out],stdin=subprocess.PIPE)
    n=int(DUR*FPS)
    for i in range(n):
        t=i/FPS
        fr=zoom(a,1+0.05*t/CUT) if t<CUT else zoom(b,1.06-0.04*(t-CUT)/(DUR-CUT))
        if CUT<=t<CUT+0.08: fr=Image.blend(fr,Image.new('RGB',(W,H),WH),0.35)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
