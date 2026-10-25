import numpy as np, wave, sys
SR=44100; BPM=130; B=60/BPM; S=B/4
dur=float(sys.argv[2]); N=int(SR*dur); out=np.zeros(N)
rng=np.random.default_rng(7)
def add(sig,t):
    i=int(t*SR); j=min(N,i+len(sig))
    if i<N: out[i:j]+=sig[:j-i]
def env(n,d): return np.exp(-np.arange(n)/(SR*d))
def kick():
    n=int(SR*0.5); t=np.arange(n)/SR; f=45+120*np.exp(-t*30)
    return np.tanh(3*np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.25))*0.9
def clap():
    n=int(SR*0.2); x=rng.standard_normal(n)*env(n,0.05)
    x=np.convolve(x,np.ones(4)/4,'same'); return x*0.35
def hat(o=False):
    n=int(SR*(0.12 if o else 0.03)); x=rng.standard_normal(n); x=np.diff(x,prepend=0)
    return x*env(n,0.04 if o else 0.008)*0.12
def bell(f):
    n=int(SR*0.35); t=np.arange(n)/SR
    sq=lambda fr: np.sign(np.sin(2*np.pi*fr*t))
    x=(sq(f)+sq(f*1.48))*env(n,0.09); x=np.diff(x,prepend=0)*0.6+x*0.4
    return np.tanh(x*1.5)*0.16
def bass(f,l):
    n=int(SR*l); t=np.arange(n)/SR
    return np.tanh(2.5*np.sin(2*np.pi*f*t))*env(n,l*0.7)*0.45
mel=[587,0,698,587,0,523,0,466, 587,0,698,880,0,784,698,0]
bl=[73.4,0,0,0,0,0,73.4,0, 58.3,0,0,0,65.4,0,0,0]
steps=int(dur/S)+1
for k in range(steps):
    t=k*S; s=k%16; bar=(k//16)%2
    if s in (0,10) or (bar and s==7): add(kick(),t)
    if s in (4,12): add(clap(),t)
    add(hat(s%4==2),t+(0.012 if s%2 else 0))
    if mel[s]: add(bell(mel[s]*(0.89 if bar else 1)),t)
    if bl[s]: add(bass(bl[s],S*5),t)
out=np.tanh(out*1.3); out/=np.max(np.abs(out))*1.12
fade=int(SR*0.4); out[-fade:]*=np.linspace(1,0,fade)
st=np.stack([out,out],1); st=(st*32767).astype(np.int16)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
