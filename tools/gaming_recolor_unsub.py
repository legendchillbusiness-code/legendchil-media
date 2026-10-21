import subprocess,numpy as np,sys
from PIL import Image,ImageFilter
src,dst,dup=sys.argv[1],sys.argv[2],sys.argv[3]=='1'
W,H=1080,1920
BLUE=np.array([40,160,255],float)
BANDS=[(440,720),(960,1140)]
Y0,Y1=1755,1905
fps=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0',src]).decode().strip()
FPSF=eval(fps)
# feather mask for blur strip
fe=np.ones((Y1-Y0,1));k=18
for i in range(k): fe[i]=fe[-1-i]=(i+1)/k
def recolor(a,t):
  for j,(y0,y1) in enumerate(BANDS):
    if j==0 and t>4.0: continue
    s=a[y0:y1].astype(float);r,g,b=s[...,0],s[...,1],s[...,2]
    mx=s.max(-1);mn=s.min(-1);sat=(mx-mn)/np.maximum(mx,1)
    m=(r>110)&(g>0.62*r)&(g<1.05*r)&(b<0.55*g)&(sat>0.5)
    if m.any():
      v=(mx[m]/245.0)[:,None]
      s[m]=np.clip(BLUE*v,0,255)
      a[y0:y1]=s.astype(np.uint8)
  return a
def unsub(a):
  strip=Image.fromarray(a[Y0:Y1]).filter(ImageFilter.GaussianBlur(22))
  bl=np.asarray(strip).astype(float)*0.55
  o=a[Y0:Y1].astype(float)
  a[Y0:Y1]=(o*(1-fe)[:,:,None]*0+o*(1-fe[:,:,None])+bl*fe[:,:,None]).astype(np.uint8)
  return a
dec=subprocess.Popen(['ffmpeg','-v','error','-i',src,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
has_a=subprocess.check_output(['ffprobe','-v','error','-select_streams','a','-show_entries','stream=index','-of','csv=p=0',src]).strip()!=b''
cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',fps,'-i','-','-i',src,'-map','0:v']+(['-map','1:a','-c:a','copy'] if has_a else [])+['-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',dst]
enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
n=0
while True:
  b=dec.stdout.read(W*H*3)
  if len(b)<W*H*3:break
  a=np.frombuffer(b,np.uint8).reshape(H,W,3).copy()
  a=recolor(a,n/FPSF)
  if dup: a=unsub(a)
  enc.stdin.write(a.tobytes());n+=1
enc.stdin.close();enc.wait();print(dst,n,'dup' if dup else '')
