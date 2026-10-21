import subprocess,numpy as np,sys
from PIL import Image
src,dst=sys.argv[1],sys.argv[2];W,H,FPS=1080,1920,30
CARD=int(round(28.3*FPS))
card=Image.open('/root/repo/ebook_v2/endcard_pt.png').convert('RGB')
GOLD=np.array([184,151,90],float)
def cardframe(k):
  t=min(k/6,1.0); s=1.04-0.04*t
  im=card.resize((int(W*s),int(H*s)),Image.LANCZOS)
  x=(im.width-W)//2;y=(im.height-H)//2
  a=np.asarray(im.crop((x,y,x+W,y+H))).astype(float)
  return (a*(0.35+0.65*t)).astype(np.uint8)
dec=subprocess.Popen(['ffmpeg','-v','error','-i',src,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',src,'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart','-shortest',dst],stdin=subprocess.PIPE)
i=0;n=0
while True:
  b=dec.stdout.read(W*H*3)
  if len(b)<W*H*3:break
  if i>=CARD:
    out=cardframe(i-CARD)
  else:
    a=np.frombuffer(b,np.uint8).reshape(H,W,3).copy()
    band=a[1050:1650].astype(float)
    r,g,bb=band[...,0],band[...,1],band[...,2]
    mx=band.max(-1);mn=band.min(-1);sat=(mx-mn)/np.maximum(mx,1)
    m=(r>110)&(r>1.9*g)&(r>1.9*bb)&(sat>0.55)
    if m.any():
      n+=1
      lum=(r/ max(1,1))[m]
      k=np.clip(r[m]/150.0,0.5,1.3)[:,None]
      band[m]=np.clip(GOLD*k,0,255)
      a[1050:1650]=band.astype(np.uint8)
    out=a
  enc.stdin.write(out.tobytes());i+=1
enc.stdin.close();enc.wait();print(dst,i,'frames, recolored',n)
