import json,subprocess,sys,os
D=os.path.dirname(os.path.abspath(__file__));R=os.path.dirname(D)
for L in json.load(open(sys.argv[1])):
    out=f"{R}/videos/yt_green/{L['slug']}.mp4"
    r=subprocess.run([sys.executable,'-I',f"{D}/yt_green_render.py",f"{R}/images/yt_c/bg_{L['bg']}.jpg",json.dumps({'title':L['head'],'items':L['items']}),out],capture_output=True,text=True)
    print(L['slug'],r.returncode,r.stdout.strip(),r.stderr[-200:])
