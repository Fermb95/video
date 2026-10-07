import numpy as np, wave
import json,subprocess
TM=json.load(open('/home/user/video/src/timemap.json'))
B,KK=TM['bounds'],TM['K']
starts=[0]
for i,k in enumerate(KK): starts.append(starts[-1]+k*(B[i+1]-B[i]))
def T(x):
    for i in range(len(KK)):
        if x<=B[i+1] or i==len(KK)-1: return starts[i]+(x-B[i])*KK[i]
SR=44100; D=starts[-1]
N=int(SR*D); t=np.arange(N)/SR
rng=np.random.default_rng(3)
mus=np.zeros(N); sfx=np.zeros(N)
def add(buf,start,sig,g=1.0):
    i=int(start*SR); n=min(len(sig),N-i)
    if n>0: buf[i:i+n]+=sig[:n]*g
def tone(f,dur,att=.01,dec=3.0,harm=(1,.35,.15)):
    x=np.arange(int(dur*SR))/SR
    env=np.minimum(x/att,1)*np.exp(-dec*x)
    return sum(a*np.sin(2*np.pi*f*(k+1)*x) for k,a in enumerate(harm))*env
def pad(f,dur,g=1.0):
    x=np.arange(int(dur*SR))/SR
    env=np.minimum(x/.8,1)*np.minimum((dur-x)/.8,1)
    s=sum(np.sin(2*np.pi*f*d*x+ph) for d,ph in ((1,0),(1.004,1),(0.996,2)))/3
    s+=.3*np.sin(2*np.pi*f*2*x)
    return s*env*g
hz=lambda m:440*2**((m-69)/12)
# progression C G Am F, 2.5 s/bar (96 bpm)
bar=2.5; chords=[[48,52,55,60],[43,50,55,59],[45,52,57,60],[41,48,53,57]]
for b in range(int(D/2.5)+1):
    c=chords[b%4]
    for m in c: add(mus,b*bar,pad(hz(m),bar+.6),.11)
    add(mus,b*bar,tone(hz(c[0]-12),bar,.02,1.1,(1,.4)),.35)
    beat=bar/8
    if b>=1 and b*2.5<D:
        arp=[c[1]+12,c[2]+12,c[3]+12,c[2]+12+0,c[3]+12,c[2]+12,c[1]+12+12,c[2]+12]
        for k,m in enumerate(arp):
            if b>=9 and False: pass
            add(mus,b*bar+k*beat,tone(hz(m),.7,.004,6,(1,.3,.1)),.13 if k%2==0 else .09)
    # soft pulse
    for k in range(5):
        x=np.arange(int(.18*SR))/SR
        add(mus,b*bar+k*bar/5*0+k*.5,np.sin(2*np.pi*(90*np.exp(-x*18))*x*0+2*np.pi*60*x)*np.exp(-x*22),.0)
mus*= np.minimum(t/1.5,1)*np.clip((D-t)/2.0,0,1)
# final resolving chord
for m in (60,64,67,72): add(mus,T(26.6),tone(hz(m),3.4,.02,.9,(1,.3,.1)),.12)
import os
if os.path.exists('/home/user/video/src/music.mp3'):
    r=subprocess.run(['ffmpeg','-v','error','-i','/home/user/video/src/music.mp3','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True,check=True)
    m=np.frombuffer(r.stdout,dtype=np.float32).astype(np.float64); m/=np.abs(m).max()
    xf=int(3*SR); full=m.copy()
    while len(full)<N:
        fade=np.linspace(0,1,xf); full=np.concatenate([full[:-xf],full[-xf:]*(1-fade)+m[:xf]*fade,m[xf:]])
    mus=full[:N].copy()*np.minimum(t/1.5,1)*np.clip((D-t)/3.0,0,1)*.62
def whoosh(dur,up=True,g=.5):
    x=np.arange(int(dur*SR))/SR; n=rng.standard_normal(len(x))
    k=np.cumsum(n); # brownian-ish
    f=np.exp(-((x-dur*.5)/(dur*.28))**2)
    s=np.convolve(n,np.ones(24)/24,'same')*f
    return s*(1 if up else 1)
def click(g=1):
    x=np.arange(int(.05*SR))/SR; return rng.standard_normal(len(x))*np.exp(-x*140)*.5
def pop(f=700):
    x=np.arange(int(.18*SR))/SR; return np.sin(2*np.pi*(f+400*np.exp(-x*30))*x)*np.exp(-x*22)
def ding(f=1318):
    return tone(f,.9,.002,5,(1,.4,.2))
add(sfx,T(2.2),whoosh(1.4),.9)
add(sfx,T(25.5),whoosh(1.4),.9)
add(sfx,T(3.2),tone(hz(84),1.6,.01,2.5,(1,.4,.3)),.18); add(sfx,T(3.35),tone(hz(91),1.4,.01,2.5,(1,.4,.3)),.14)
for s,L in ((7,59),(12,45),(17,24)):
    add(sfx,T(s+2.3),pop(),.5)
    add(sfx,T(s+3.3),ding(),.22)
add(sfx,T(12+3.65),click(),1.2); add(sfx,T(12+3.65),pop(500),.3)
add(sfx,T(7+4.5),click(),1.2); add(sfx,T(7+4.5),pop(500),.3)
for i in range(6): add(sfx,T(22.7+i*.18),tone(hz(72+[0,4,7,12,7,4][i]),.6,.003,6,(1,.3)),.1)
add(sfx,T(26.7),tone(hz(96),1.5,.005,2.5,(1,.4,.3)),.15)
add(sfx,T(28.5),pop(900),.3)
import os
def load(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True,check=True)
    x=np.frombuffer(r.stdout,dtype=np.float32).astype(np.float64)
    return x/np.abs(x).max()*.9
V='/home/user/video/src/voice/'
vo=np.zeros(N)
for f,st in (('presentacion',starts[1]+1.0),('codigos',starts[2]+.2),('guia',starts[3]+.5),('organigrama',starts[4]+.5),('mucho_mas',starts[5]+.6),('cierre',starts[6]+2.6)):
    if os.path.exists(V+f+'.mp3'):
        x=load(V+f+'.mp3'); print(f,round(st,2),'->',round(st+len(x)/SR,2)); add(vo,st,x,1.0)
env=np.convolve(np.abs(vo),np.ones(int(.15*SR))/int(.15*SR),'same')
env=np.convolve(np.minimum(env*8,1),np.ones(int(.4*SR))/int(.4*SR),'same')
duck=1-.6*np.minimum(env,1)
out=mus*.55*duck+sfx*.6*(1-.3*np.minimum(env,1))+vo*1.0
out=np.tanh(out*1.05); out/=np.abs(out).max()/.9
st=np.stack([out,np.roll(out,int(.004*SR))],1)
w=wave.open('/home/user/video/src/audio.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((st*32767).astype('<i2').tobytes());w.close()
