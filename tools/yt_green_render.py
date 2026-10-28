"""Formato verde — lista inteira num ecrã, 10 s, foto escura tingida + phonk.
uso: python3 yt_green_render.py BG.jpg 'json da lista' out.mp4   (json: {"title":..., "items":[[a,b],...]})"""
import sys, os, json, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
D=os.path.dirname(os.path.abspath(__file__)); W,H=1080,1920; DUR=10.0
P=lambda w,s:ImageFont.truetype(f'/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf',s)
WH=(240,240,236); GR=(170,180,172)
def wrap(d,t,f,maxw):
    L,c=[],''
    for w in t.split():
        x=(c+' '+w).strip()
        if d.textlength(x,font=f)<=maxw: c=x
        else: L.append(c); c=w
    return L+[c]
def card(bg,title,items):
    im=ImageOps.fit(Image.open(bg).convert('RGB'),(W,H),Image.LANCZOS).convert('L')
    im=ImageEnhance.Brightness(im).enhance(0.55)
    im=Image.merge('RGB',[im.point(lambda v:int(v*a)) for a in (0.62,0.78,0.66)])
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov); od.rectangle((0,0,W,H),fill=(0,0,0,95)); im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
    d=ImageDraw.Draw(im); x0=70; y=330; mw=W-2*x0
    ft=P('Bold',78)
    for ln in wrap(d,title.upper(),ft,mw): d.text((x0,y),ln,font=ft,fill=WH); y+=92
    y+=40; fi=P('Medium',44)
    for a,b in items:
        for ln in wrap(d,f'{a} {b}',fi,mw): d.text((x0,y),ln,font=fi,fill=WH); y+=58
        y+=18
    y+=24; fb=P('SemiBold',38) if os.path.exists('/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf') else P('Medium',38)
    t='One sign proves nothing. The pattern does.'; tw=d.textlength(t,font=fb)
    d.rectangle((x0-8,y-8,x0+tw+12,y+54),outline=WH,width=3); d.text((x0+2,y),t,font=fb,fill=WH); y+=100
    d.text((x0,y),'Full guide on my channel.',font=P('Medium',44),fill=WH)
    d.text((x0,H-150),'@legendchil',font=P('Regular',32),fill=GR)
    d.text((W-x0,H-150),'Ψ',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',56),fill=GR,anchor='ra')
    return im,y
if __name__=='__main__':
    bg,js,out=sys.argv[1:4]; L=json.loads(js); im,yend=card(bg,L['title'],L['items'])
    if yend>H-230: print('WARN overflow',yend)
    tmp=tempfile.mkdtemp(); im.save(f'{tmp}/c.png'); wav=f'{tmp}/a.wav'
    subprocess.run([sys.executable,'-I',f'{D}/phonk_synth.py',wav,str(DUR)],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-i',f'{tmp}/c.png','-i',wav,'-t',str(DUR),'-r','30','-vf','format=yuv420p',
      '-c:v','libx264','-preset','veryfast','-crf','20','-tune','stillimage','-c:a','aac','-b:a','160k','-movflags','+faststart',out],check=True)
