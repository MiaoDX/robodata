"""Generate the hand-laid-out SVG diagrams in docs/assets/.

Run from anywhere:  python docs/assets/src/generate_svgs.py
Shared colour semantics (see docs/visual-guide.md):
green = measured evidence, amber = estimated, blue = exact derivation,
purple = retargeted/simulated, grey = packaging and delivery.
"""
from pathlib import Path
OUT = str(Path(__file__).resolve().parent.parent) + "/"
FONT='font-family="Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif"'
C=dict(ev="#2e8b57",evf="#d9f2e3",est="#c98a1a",estf="#fbe9c9",ex="#3b6fb6",exf="#dbe8fb",rt="#7d4bb3",rtf="#eadcf7",bad="#c0392b",ink="#1f2430",mut="#5b6475",grid="#d6dae2")
def svg(w,h,body,title,desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" {FONT}>
<title id="t">{title}</title><desc id="d">{desc}</desc>
<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="{C['mut']}"/></marker>
<marker id="arb" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="{C['ex']}"/></marker>
<marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="{C['bad']}"/></marker></defs>
<rect width="{w}" height="{h}" rx="14" fill="#ffffff"/>
{body}</svg>'''
def t(x,y,s,size=13,fill=C['ink'],w=400,anchor="start",style=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}" {style}>{s}</text>'

# ---------- time model ----------
X0,X1=210,740; ms=lambda v:X0+(X1-X0)*v/300
b=[t(24,34,"Native clocks, explicit alignment",18,w=700),
   t(24,56,"Each stream keeps its own clock; a versioned mapping places it on a common timeline; the aligned grid is a view.",12.5,C['mut'])]
lanes=[("Camera · device clock","30 Hz · exposure intervals",100),("IMU · device clock","100 Hz",150),("Gripper · host clock","50 Hz · mapped by sync_v4",200),("Aligned view","20 Hz grid",270)]
for name,sub,y in lanes:
    b.append(t(24,y-2,name,13,w=600)); b.append(t(24,y+14,sub,11.5,C['mut']))
    b.append(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="{C["grid"]}" stroke-width="1.5"/>')
cam=[0,33.3,66.7,100,133.3,166.7,200,233.3,266.7]
dropped={200,233.3}
for f in cam:
    x=ms(f)
    if f in dropped:
        b.append(f'<rect x="{x-5}" y="{92}" width="10" height="16" rx="2" fill="none" stroke="{C["bad"]}" stroke-dasharray="3 2"/>')
        b.append(t(x,88,"drop",10,C['bad'],anchor="middle"))
    else:
        b.append(f'<rect x="{x-5}" y="92" width="10" height="16" rx="2" fill="{C["evf"]}" stroke="{C["ev"]}"/>')
for i in range(0,31):
    x=ms(i*10); b.append(f'<line x1="{x}" y1="143" x2="{x}" y2="157" stroke="{C["ev"]}" stroke-width="1.4"/>')
for i in range(0,16):
    x=ms(i*20+3.1); b.append(f'<circle cx="{x}" cy="200" r="3.6" fill="{C["evf"]}" stroke="{C["ev"]}"/>')
b.append(t(ms(150),224,"host-clock samples shifted +3.1 ms by clock mapping sync_v4 (residual 0.8 ms)",11,C['est'],anchor="middle",style='paint-order="stroke" stroke="#fff" stroke-width="4"'))
# grid
for g in [0,50,100,150,200,250,300]:
    x=ms(g); ok=g!=250
    col=C['ex'] if ok else C['bad']
    b.append(f'<circle cx="{x}" cy="270" r="6" fill="{C["exf"] if ok else "#fbe0dd"}" stroke="{col}" stroke-width="1.6"/>')
    b.append(t(x,294,f"{g} ms",10.5,C['mut'],anchor="middle"))
    src=max(f for f in cam if f<=g and f not in dropped)
    if ok:
        b.append(f'<path d="M{ms(src)} 110 C {ms(src)} 200, {x} 200, {x} 262" fill="none" stroke="{C["ex"]}" stroke-width="1.2" stroke-dasharray="4 3" marker-end="url(#arb)"/>')
    else:
        b.append(f'<path d="M{ms(src)} 110 C {ms(src)} 200, {x} 200, {x} 262" fill="none" stroke="{C["bad"]}" stroke-width="1.2" stroke-dasharray="4 3" marker-end="url(#arr)"/>')
b.append(t(ms(250)-12,248,"latest frame is 83 ms old",11,C['bad'],anchor="end",style='paint-order="stroke" stroke="#fff" stroke-width="4"'))
b.append(t(ms(250)-12,261,"&gt; 60 ms → reject segment",11,C['bad'],anchor="end",style='paint-order="stroke" stroke="#fff" stroke-width="4"'))
b.append(f'<rect x="24" y="314" width="716" height="40" rx="8" fill="#f5f7fa"/>')
b.append(t(38,331,"Contract: output 20 Hz · image selection latest_available · max image age 60 ms · missing stream → reject_segment",11.5))
b.append(t(38,346,"Grid points reuse or skip frames explicitly; the view never rewrites source timestamps.",11.5,C['mut']))
open(OUT+'time-model.svg','w').write(svg(764,372,"\n".join(b),"Multi-clock alignment","Camera, IMU and gripper streams on their own clocks are mapped onto a 20 Hz aligned grid; one grid point is rejected because the latest image exceeds the maximum age."))

# ---------- action representations ----------
import math
def seg(x0,y0,x,y,col,wd=1.5):
    dx,dy=x-x0,y-y0; L=math.hypot(dx,dy); x2,y2=x-dx/L*7,y-dy/L*7
    return f'<line x1="{x0}" y1="{y0}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{wd}" marker-end="url(#arb)"/>'
pts=[(36,150),(70,80),(140,55),(196,115)]
panels=[("Absolute","a_k = T_k in world frame","abs"),("Fixed-anchor relative","R_k = T_0⁻¹ · T_k","rel"),("Stepwise delta","Δ_k = T_(k−1)⁻¹ · T_k","dlt")]
b=[t(24,34,"One trajectory, three action representations",18,w=700),
   t(24,56,"Same poses T_0…T_3. Values differ, and so does how errors accumulate when a policy replays them.",12.5,C['mut'])]
for i,(name,formula,kind) in enumerate(panels):
    ox=24+i*246; oy=74
    b.append(f'<rect x="{ox}" y="{oy}" width="232" height="218" rx="10" fill="#f8f9fb" stroke="{C["grid"]}"/>')
    b.append(t(ox+14,oy+24,name,14,w=700)); b.append(t(ox+14,oy+44,formula,12,C['ex'],style='font-family="ui-monospace,Menlo,monospace"'))
    P=[(ox+px,oy+px2+20) for px,px2 in pts]
    W=(ox+205,oy+196)
    d="M"+" L".join(f"{x} {y}" for x,y in P)
    b.append(f'<path d="{d}" fill="none" stroke="{C["grid"]}" stroke-width="6" stroke-linecap="round"/>')
    if kind=="abs":
        b.append(f'<rect x="{W[0]-5}" y="{W[1]-5}" width="10" height="10" fill="{C["mut"]}"/>'); b.append(t(W[0]-10,W[1]+4,"world",10.5,C['mut'],anchor="end"))
        for x,y in P: b.append(seg(W[0],W[1],x,y,C['ex']))
    elif kind=="rel":
        for x,y in P[1:]: b.append(seg(P[0][0],P[0][1],x,y,C['ex']))
        b.append(t(ox+14,oy+206,"anchor T0 = window start",10.5,C['mut']))
    else:
        for (x0,y0),(x,y) in zip(P,P[1:]): b.append(seg(x0,y0,x,y,C['ex'],1.8))
        b.append(t(ox+14,oy+206,"errors accumulate over the chunk",10.5,C['mut']))
    for k,(x,y) in enumerate(P):
        b.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="{C["ink"]}" stroke-width="1.5"/>'); b.append(t(x+7,y-7,f"T{k}",11,C['ink'],w=600))
b.append(f'<rect x="24" y="304" width="716" height="44" rx="8" fill="#f5f7fa"/>')
b.append(t(38,322,"Mixed representations are normal: arm pose anchor-relative, gripper width absolute (metres).",11.5))
b.append(t(38,338,"RDIR declares representation, reference frame, reference instant, units and rotation convention per action slice.",11.5,C['mut']))
open(OUT+'action-representations.svg','w').write(svg(764,364,"\n".join(b),"Action representations","The same four poses encoded as absolute poses, relative to a fixed anchor, and as stepwise deltas."))

# ---------- roles x stages ----------
stages=["Capture","Evidence","Derivation","Curation","Release","Training","Evaluation"]
roles=[("Collector","consent · pay · task clarity",[2,0,0,0,0,0,0]),
       ("Supplier","cost · single source · metering",[2,2,2,2,2,0,1]),
       ("Platform","catalog · lineage · search",[0,2,2,2,1,0,0]),
       ("Acceptance","audit · reconcile hours",[0,0,0,1,2,0,0]),
       ("Training consumer","semantics · throughput",[0,0,0,1,2,2,1]),
       ("Evaluator","failure attribution",[0,0,0,1,0,1,2])]
LX,SX,CW,RH,TY=24,214,74,40,96
b=[t(24,34,"Who touches which stage",18,w=700),
   t(24,56,"● primary responsibility   ○ consumes or influences",12.5,C['mut'])]
for j,s in enumerate(stages):
    cx=SX+j*CW+CW/2
    b.append(t(cx,TY-10,s,11,C['mut'],w=600,anchor="middle"))
for i,(r,c,v) in enumerate(roles):
    y=TY+i*RH
    if i%2==0: b.append(f'<rect x="16" y="{y}" width="732" height="{RH}" rx="6" fill="#f6f8fb"/>')
    b.append(t(LX,y+17,r,13,w=700)); b.append(t(LX,y+32,c,10.5,C['mut']))
    for j,val in enumerate(v):
        cx=SX+j*CW+CW/2; cy=y+RH/2
        if val==2: b.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{C["ex"]}"/>')
        elif val==1: b.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="#fff" stroke="{C["ex"]}" stroke-width="2"/>')
ny=TY+len(roles)*RH+14
b.append(f'<rect x="24" y="{ny}" width="716" height="40" rx="8" fill="#f5f7fa"/>')
b.append(t(38,ny+17,"Every normative feature in spec/ should trace back to a need in at least one row.",11.5))
b.append(t(38,ny+32,"Rows are roles, not companies: one organization may play several.",11.5,C['mut']))
open(OUT+'perspectives-map.svg','w').write(svg(764,ny+56,"\n".join(b),"Perspectives map","Matrix of roles against lifecycle stages showing primary responsibilities and influences."))
print("ok")

# ---------- architecture (README hero) ----------
W_,H_=1200,740
b=[t(48,62,"ROBODATA",13,C['ex'],w=700,style='letter-spacing="2"'),
   t(48,102,"Facts in. Verifiable data products out.",32,w=750),
   t(48,132,"A semantic IR and typed transformation runtime for heterogeneous robotics data.",16,C['mut'])]
cols=[(48,"SOURCE EVIDENCE"),(296,"SEMANTIC CORE · RDIR"),(594,"TRANSFORMATION · RDX"),(930,"DELIVERY PRODUCTS")]
for x,s_ in cols: b.append(t(x,186,s_,12.5,C['mut'],w=700,style='letter-spacing="1.2"'))
src=[("UMI","video · gripper · motion"),("Egocentric","media · hands · body"),("Physical robot","sensors · state · commands"),("Simulation","observations · actions · truth")]
for i,(n,sub) in enumerate(src):
    y=206+i*84
    b.append(f'<rect x="48" y="{y}" width="212" height="70" rx="12" fill="{C["evf"]}" stroke="{C["ev"]}" stroke-width="1.4"/>')
    b.append(t(66,y+30,n,17,w=700)); b.append(t(66,y+52,sub,13,C['mut']))
# core
b.append(f'<rect x="296" y="206" width="262" height="322" rx="16" fill="{C["exf"]}" stroke="{C["ex"]}" stroke-width="1.6"/>')
b.append(t(318,240,"RoboData IR",20,w=750)); b.append(t(318,262,"components · async streams · versions",12,C['mut']))
pills=[["Time","Geometry"],["Action semantics"],["Epistemic roles"],["Capabilities","Quality"],["Access &amp; consent"],["Lineage &amp; stable identity"]]
for r,row in enumerate(pills):
    x=318; y=282+r*38
    for p_ in row:
        w_=len(p_.replace("&amp;","&"))*8.2+26
        b.append(f'<rect x="{x}" y="{y}" width="{w_:.0f}" height="28" rx="14" fill="#ffffff" stroke="{C["ex"]}"/>')
        b.append(t(x+13,y+19,p_,13,C['ink'],w=600)); x+=w_+10
# rdx
b.append(f'<rect x="594" y="206" width="300" height="322" rx="16" fill="#f5f7fa" stroke="{C["mut"]}" stroke-width="1.4"/>')
b.append(t(616,240,"Robot Data Exchange",20,w=750)); b.append(t(616,262,"contract-driven compiler",13,C['mut']))
steps=["capability preflight","typed transform graph","materialization policy","lineage + loss report","target-reader test"]
for i,s_ in enumerate(steps):
    y=296+i*38
    b.append(f'<circle cx="628" cy="{y-5}" r="11" fill="{C["ex"]}"/>'); b.append(t(628,y-1,str(i+1),12,"#fff",w=700,anchor="middle"))
    b.append(t(648,y,s_,14,C['ink'],w=500))
b.append(f'<rect x="616" y="486" width="256" height="26" rx="13" fill="{C["ex"]}"/>')
b.append(t(744,504,"CONTRACT-CHECKED RELEASE",10.5,"#fff",w=700,anchor="middle",style='letter-spacing="0.6"'))
# delivery
dl=[("LeRobot v3","default training delivery"),("MCAP","lossless · visualization"),("Zarr","chunked random access"),("Custom contract","customer-specific layouts"),("Training views","aligned shards · latents")]
for i,(n,sub) in enumerate(dl):
    y=206+i*65
    b.append(f'<rect x="930" y="{y}" width="222" height="56" rx="12" fill="#eeeeee" stroke="#8a8a8a" stroke-width="1.2"/>')
    b.append(t(948,y+24,n,15.5,w=700)); b.append(t(948,y+43,sub,12.5,C['mut']))
# arrows
for x0,x1 in [(264,292),(562,590),(898,926)]:
    b.append(f'<line x1="{x0}" y1="367" x2="{x1}" y2="367" stroke="{C["mut"]}" stroke-width="2" marker-end="url(#ar)"/>')
# feedback
b.append(f'<path d="M1041 532 L1041 560 L154 560 L154 546" fill="none" stroke="{C["mut"]}" stroke-width="1.4" stroke-dasharray="5 4" marker-end="url(#ar)"/>')
b.append(t(600,578,"feedback: rejection · evaluation failure · capability gap → curation or new capture",12.5,C['mut'],anchor="middle"))
# invariants
b.append(f'<rect x="48" y="598" width="1104" height="98" rx="14" fill="#f5f7fa" stroke="{C["grid"]}"/>')
b.append(t(72,626,"INVARIANTS",12.5,C['mut'],w=700,style='letter-spacing="1.2"'))
inv=["measured ≠ estimated ≠ commanded ≠ executed","demonstrated ≠ retargeted ≠ simulated truth","logical identity ≠ file location",
     "source evidence ≠ delivery view","unknown stays unknown","one hour of evidence is one hour, in any format"]
for i,s_ in enumerate(inv):
    x=72+(i%3)*362; y=654+(i//3)*28
    b.append(t(x,y,s_,13.5,C['ink']))
b.append(t(48,724,"ROBODATA ARCHITECTURE · DESIGN BASELINE · see docs/visual-guide.md",11.5,C['mut'],w=600))
open(OUT+'architecture.svg','w').write(svg(W_,H_,"\n".join(b),"RoboData architecture","Four source families flow through source evidence, RoboData IR and the RDX contract-driven compiler into delivery formats and training views, with feedback into curation and capture."))
print("architecture ok")
