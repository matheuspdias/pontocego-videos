import os, sys; sys.path.insert(0, "/home/claude/pontocego-videos"); os.chdir("/home/claude/pontocego-videos")
os.environ["PC_VERTICAL"]="1"
import engine; engine.STYLE="ilustrado"; engine.TOM="sombrio"
from engine import *
from ilustrado import *
import ilustrado
from pov import *
import numpy as np, subprocess, sfx
DUR=10.0; SUSTO=5.0
OLHO = lambda t: "normal" if t < SUSTO else "vazios"
SEN = dict(SENHOR); SEN["olhos"]=OLHO
def fora(c,t):
    estrada_noite(c,t,1.0)
    nevoa_i(c,t,980,0.45,seed=2)
def cena(c,t):
    if t < SUSTO:
        z = 1 + 1.4*ease_io(prog(t,1.0,SUSTO-1.0))
        mx,my = W/2, 345
        c.save(); c.translate(mx,my); c.scale(z,z); c.translate(-mx,-my)
        carro_pov(c,t,fora,retrovisor=banco_tras(True,False,quem=SEN,look=0.0),celular=tela_corrida("aguardando",espera="09:40",hora="03:12"))
        c.restore()
        legendas(c,t,[] ) if False else None
    else:
        k = t-SUSTO
        shake = 14*max(0,1-k/0.5)
        c.save(); c.translate(math.sin(t*90)*shake, math.cos(t*77)*shake)
        lgrad(c,0,0,0,H,[(0,(0.05,0.06,0.09),1),(1,(0.01,0.01,0.02),1)]); c.paint()
        old=ilustrado._L; ilustrado._L=LUZES["sombrio"]
        s = 7.0 + 0.3*k
        boneco(c,t,W/2,820+403*s, s, exprs=((0,"sinistro"),), look=0.0, **SEN)
        ilustrado._L=old
        c.restore()
        if k < 0.18:
            c.set_source_rgba(1,1,1,0.85*(1-k/0.18)); c.paint()
        c.set_source_rgba(0.6,0,0,0.18*max(0,1-k/1.2)); c.paint()
    engine.overlay(c,t)
os.makedirs("/tmp/demo/f",exist_ok=True)
N=int(DUR*30)
for i in range(N):
    t=i/30
    s_=cairo.ImageSurface(cairo.FORMAT_RGB24,W,H); c=cairo.Context(s_)
    cena(c,t); s_.write_to_png(f"/tmp/demo/f/{i:04d}.png")
SR=sfx.SR; out=np.zeros(int(SR*(DUR+3)))
def put(t0,x,g=1.0):
    i=int(t0*SR); out[i:i+len(x)]+=x[:len(out)-i]*g
put(0, sfx.drone_terror(DUR), 0.55)
put(0.3, sfx.vibra_celular(2), 0.5)
put(1.0, sfx.coracao_acelerando(SUSTO-1.0), 0.8)
put(SUSTO-3.0, sfx.cordas_subindo(3.0), 0.6)
put(SUSTO, sfx.susto(), 0.95)
put(SUSTO+1.6, sfx.sino_funebre(), 0.5)
out=out[:int(SR*DUR)]; out[int(SUSTO*SR)-int(0.04*SR):int(SUSTO*SR)]*=np.linspace(1,0.2,int(0.04*SR))
sfx.write_wav("/tmp/demo/a.wav", np.clip(out*0.9,-1,1))
subprocess.run(["ffmpeg","-v","error","-y","-framerate","30","-i","/tmp/demo/f/%04d.png","-i","/tmp/demo/a.wav","-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-b:a","192k","-shortest","/home/claude/pontocego-videos/out/teste_terror.mp4"],check=True)
