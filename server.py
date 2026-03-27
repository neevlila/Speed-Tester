import time, os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Network Speed Test</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--bg:#06091a;--card:rgba(255,255,255,.05);--border:rgba(255,255,255,.09);--primary:#00d4ff;--purple:#7c3aed;--green:#00ff88;--yellow:#fbbf24;--red:#f87171;--muted:#64748b}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:var(--bg);min-height:100vh;color:#e2e8f0;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 50% at 20% 20%,rgba(0,212,255,.08),transparent 60%),radial-gradient(ellipse 60% 40% at 80% 80%,rgba(124,58,237,.08),transparent 60%);pointer-events:none}
.c{max-width:860px;margin:0 auto;padding:2rem 1rem;position:relative;z-index:1}
h1{font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#00d4ff,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-align:center;margin-bottom:.3rem}
.sub{text-align:center;color:var(--muted);margin-bottom:1.5rem}
.info-bar{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:.6rem 1rem;font-size:.82rem;color:var(--muted);text-align:center;margin-bottom:1.5rem}
.info-bar span{color:var(--primary);font-weight:600}
/* Gauge */
.gauge-card{background:var(--card);border:1px solid var(--border);border-radius:24px;padding:2.5rem 2rem 2rem;text-align:center;margin-bottom:1.2rem;backdrop-filter:blur(10px)}
.g-wrap{position:relative;display:inline-block}
.g-svg{width:200px;height:200px;transform:rotate(-90deg)}
.g-bg{fill:none;stroke:rgba(255,255,255,.07);stroke-width:14}
.g-fill{fill:none;stroke:url(#gg);stroke-width:14;stroke-linecap:round;stroke-dasharray:565.5;stroke-dashoffset:565.5;transition:stroke-dashoffset .25s ease}
.g-text{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.g-num{font-size:2.8rem;font-weight:800;color:var(--primary);line-height:1}
.g-unit{font-size:.85rem;color:var(--muted);margin-top:3px}
.g-lbl{color:var(--muted);font-size:.82rem;text-transform:uppercase;letter-spacing:.08em;margin-top:.5rem}
/* Settings */
.settings{display:flex;gap:.8rem;justify-content:center;flex-wrap:wrap;margin-top:1rem}
.sg{display:flex;align-items:center;gap:.4rem;font-size:.82rem;color:var(--muted)}
.sg select{background:rgba(255,255,255,.07);border:1px solid var(--border);border-radius:8px;padding:.3rem .5rem;color:#e2e8f0;font-size:.82rem}
.sg select option{background:#1a2035;color:#e2e8f0;}
/* Button */
.btn{margin-top:1.4rem;background:linear-gradient(135deg,#00d4ff,#7c3aed);color:#fff;border:none;padding:.9rem 2.8rem;font-size:1rem;font-weight:700;border-radius:50px;cursor:pointer;transition:all .3s;letter-spacing:.04em}
.btn:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,212,255,.4)}
.btn:disabled{opacity:.55;cursor:not-allowed}
.status{color:var(--muted);font-size:.88rem;margin-top:.8rem;min-height:1.4rem;text-align:center}
/* Steps */
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.2rem}
.step{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.2rem 1rem;text-align:center;transition:all .3s;backdrop-filter:blur(8px)}
.step.active{border-color:var(--primary);box-shadow:0 0 18px rgba(0,212,255,.18)}
.step.done{border-color:var(--green)}
.s-icon{font-size:1.8rem;margin-bottom:.5rem}
.s-title{font-size:.75rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.09em;margin-bottom:.4rem}
.s-val{font-size:1.4rem;font-weight:700;color:#e2e8f0}
.s-unit{font-size:.78rem;color:var(--muted)}
.ptrack{height:4px;background:rgba(255,255,255,.06);border-radius:2px;margin-top:.8rem;overflow:hidden}
.pfill{height:100%;width:0%;border-radius:2px;background:linear-gradient(90deg,#00d4ff,#7c3aed);transition:width .25s}
/* Results */
.results{display:none}
.rg{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-bottom:1rem}
.mc{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.3rem;display:flex;align-items:center;gap:1rem;backdrop-filter:blur(8px)}
.mi{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.4rem;flex-shrink:0}
.mi.dl{background:rgba(0,153,255,.15)}.mi.ul{background:rgba(0,255,136,.12)}.mi.pi{background:rgba(251,191,36,.12)}.mi.lo{background:rgba(248,113,113,.12)}
.ml{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.2rem}
.mv{font-size:1.7rem;font-weight:700;line-height:1}
.mv.dl{color:#0099ff}.mv.ul{color:#00ff88}.mv.pi{color:var(--yellow)}.mv.lo{color:var(--red)}
.mu{font-size:.8rem;color:var(--muted)}
.dg{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}
.dc{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.3rem;backdrop-filter:blur(8px)}
.dt{font-size:.75rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.8rem;padding-bottom:.6rem;border-bottom:1px solid var(--border)}
.dr{display:flex;justify-content:space-between;padding:.4rem 0;font-size:.88rem;border-bottom:1px solid rgba(255,255,255,.03)}
.dr:last-child{border:none}
.dk{color:var(--muted)}.dv{font-weight:600}
.alert{border-radius:10px;padding:.8rem 1rem;margin-top:.8rem;font-size:.88rem;display:flex;align-items:center;gap:.5rem}
.aw{background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.2);color:var(--yellow)}
.ae{background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.2);color:var(--red)}
.footer{text-align:center;color:var(--muted);font-size:.78rem;margin-top:1.5rem;padding-top:1rem;border-top:1px solid var(--border)}
.spin{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.2);border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;margin-right:5px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
.shimmer{background:linear-gradient(90deg,#00d4ff 0%,#7c3aed 50%,#00d4ff 100%);background-size:200% 100%;animation:shimmer 1.2s linear infinite}
.hidden{display:none}
@media(max-width:600px){.steps,.rg,.dg{grid-template-columns:1fr}.g-svg{width:168px;height:168px}.g-num{font-size:2.1rem}}
</style>
</head>
<body>
<div class="c">
  <h1>🌐 Network Speed Test</h1>
  <p class="sub">Real-time measurement from your browser to this server</p>

  <div class="gauge-card">
    <div class="g-wrap">
      <svg class="g-svg" viewBox="0 0 200 200">
        <defs><linearGradient id="gg" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#00d4ff"/><stop offset="100%" style="stop-color:#7c3aed"/>
        </linearGradient></defs>
        <circle class="g-bg" cx="100" cy="100" r="90"/>
        <circle class="g-fill" id="gf" cx="100" cy="100" r="90"/>
      </svg>
      <div class="g-text"><div class="g-num" id="gn">0</div><div class="g-unit">Mbps</div></div>
    </div>
    <div class="g-lbl" id="gl">Ready to test</div>
    <div class="settings">
      <div class="sg"><label>Download</label><select id="dl"><option value="10">10 MB</option><option value="25" selected>25 MB</option><option value="50">50 MB</option></select></div>
      <div class="sg"><label>Upload</label><select id="ul"><option value="5">5 MB</option><option value="20" selected>20 MB</option><option value="40">40 MB</option></select></div>
      <div class="sg"><label>Pings</label><select id="pc"><option value="10">10</option><option value="20" selected>20</option><option value="50">50</option></select></div>
    </div>
    <div><button class="btn" id="sb" onclick="run()">🚀 Start Speed Test</button></div>
    <div class="status" id="st"></div>
  </div>

  <div class="steps">
    <div class="step" id="sp-ping"><div class="s-icon">📡</div><div class="s-title">Latency</div><div class="s-val" id="sv-ping">— <span class="s-unit">ms</span></div><div class="ptrack"><div class="pfill" id="pf-ping"></div></div></div>
    <div class="step" id="sp-download"><div class="s-icon">📥</div><div class="s-title">Download</div><div class="s-val" id="sv-download">— <span class="s-unit">Mbps</span></div><div class="ptrack"><div class="pfill" id="pf-download"></div></div></div>
    <div class="step" id="sp-upload"><div class="s-icon">📤</div><div class="s-title">Upload</div><div class="s-val" id="sv-upload">— <span class="s-unit">Mbps</span></div><div class="ptrack"><div class="pfill" id="pf-upload"></div></div></div>
  </div>

  <div class="results" id="results">
    <div class="rg">
      <div class="mc"><div class="mi dl">⬇️</div><div><div class="ml">Download</div><div class="mv dl" id="r-dl">—</div><div class="mu">Mbps</div></div></div>
      <div class="mc"><div class="mi ul">⬆️</div><div><div class="ml">Upload</div><div class="mv ul" id="r-ul">—</div><div class="mu">Mbps</div></div></div>
      <div class="mc"><div class="mi pi">📶</div><div><div class="ml">Latency</div><div class="mv pi" id="r-ms">—</div><div class="mu">ms</div></div></div>
      <div class="mc"><div class="mi lo">📦</div><div><div class="ml">Packet Loss</div><div class="mv lo" id="r-lo">—</div><div class="mu">%</div></div></div>
    </div>
    <div class="dg">
      <div class="dc"><div class="dt">🔵 Latency Details</div>
        <div class="dr"><span class="dk">Avg</span><span class="dv" id="d-avg">—</span></div>
        <div class="dr"><span class="dk">Min</span><span class="dv" id="d-min">—</span></div>
        <div class="dr"><span class="dk">Max</span><span class="dv" id="d-max">—</span></div>
        <div class="dr"><span class="dk">Jitter</span><span class="dv" id="d-jit">—</span></div>
        <div class="dr"><span class="dk">Packet Loss</span><span class="dv" id="d-pkt">—</span></div>
      </div>
      <div class="dc"><div class="dt">🟢 Speed Details</div>
        <div class="dr"><span class="dk">Download</span><span class="dv" id="d-dl">—</span></div>
        <div class="dr"><span class="dk">Upload</span><span class="dv" id="d-ul">—</span></div>
        <div class="dr"><span class="dk">DL Data Sent</span><span class="dv" id="d-dls">—</span></div>
        <div class="dr"><span class="dk">UL Data Sent</span><span class="dv" id="d-uls">—</span></div>
        <div class="dr"><span class="dk">Protocol</span><span class="dv">HTTP/HTTPS</span></div>
      </div>
    </div>
    <div id="alerts"></div>
  </div>
</div>

<script>
const B=window.location.origin;
const C=2*Math.PI*90;

function gauge(mbps){
  const p=Math.min(mbps/1000,1);
  document.getElementById('gf').style.strokeDashoffset=C*(1-p);
  const n=document.getElementById('gn');
  n.textContent=mbps<10?mbps.toFixed(1):Math.round(mbps);
}
function gl(t){document.getElementById('gl').textContent=t;}
function st(m){document.getElementById('st').innerHTML=m;}
function sv(s,v,u){document.getElementById('sv-'+s).innerHTML=`${v} <span class="s-unit">${u}</span>`;}
function pf(s,p){
  const f=document.getElementById('pf-'+s);
  f.style.width=(p*100)+'%';
  p<1?f.classList.add('shimmer'):f.classList.remove('shimmer');
}
function active(s){
  ['ping','upload','download'].forEach(x=>{
    document.getElementById('sp-'+x).classList.remove('active','done');
  });
  if(s)document.getElementById('sp-'+s).classList.add('active');
}
function done(s){
  document.getElementById('sp-'+s).classList.remove('active');
  document.getElementById('sp-'+s).classList.add('done');
}

async function pingTest(n){
  active('ping'); gl('Testing Latency…');
  const rtts=[];let sent=0,recv=0;
  for(let i=0;i<n;i++){
    try{
      const t=performance.now();
      const r=await fetch(B+'/ping?_='+Date.now(),{cache:'no-store'});
      const rtt=performance.now()-t;
      sent++;if(r.ok){rtts.push(rtt);recv++;}
    }catch(e){sent++;}
    pf('ping',(i+1)/n);
    const avg=rtts.length?rtts.reduce((a,b)=>a+b,0)/rtts.length:0;
    sv('ping',avg.toFixed(1),'ms');
    st(`<span class="spin"></span>Ping ${i+1}/${n} — ${avg.toFixed(1)} ms`);
  }
  const avg=rtts.length?rtts.reduce((a,b)=>a+b,0)/rtts.length:0;
  const mn=rtts.length?Math.min(...rtts):0;
  const mx=rtts.length?Math.max(...rtts):0;
  const loss=((sent-recv)/Math.max(sent,1)*100);
  sv('ping',avg.toFixed(1),'ms'); pf('ping',1); done('ping');
  return{avg:avg.toFixed(1),min:mn.toFixed(1),max:mx.toFixed(1),jitter:(mx-mn).toFixed(1),loss:loss.toFixed(1),sent,recv};
}

function uploadTest(mb){
  active('upload'); gl('Testing Upload…');
  st('<span class="spin"></span>Preparing data…');
  const size=mb*1024*1024;
  const data=new Uint8Array(size).fill(88);
  return new Promise(res=>{
    const xhr=new XMLHttpRequest();
    xhr.open('POST',B+'/upload');
    xhr.setRequestHeader('Content-Type','application/octet-stream');
    const t0=performance.now();
    xhr.upload.onprogress=e=>{
      const el=(performance.now()-t0)/1000;
      const sp=(e.loaded*8)/(el*1e6);
      pf('upload',e.loaded/e.total);
      sv('upload',sp.toFixed(1),'Mbps');
      gauge(sp);
      st(`<span class="spin"></span>Uploading… ${(e.loaded/1024/1024).toFixed(1)}/${mb} MB — ${sp.toFixed(1)} Mbps`);
    };
    xhr.onload=()=>{
      pf('upload',1); done('upload');
      if(xhr.status===200){const r=JSON.parse(xhr.responseText);gauge(r.speed_mbps);sv('upload',r.speed_mbps.toFixed(1),'Mbps');res(r.speed_mbps);}
      else res(0);
    };
    xhr.onerror=()=>{pf('upload',1);done('upload');res(0);};
    xhr.send(data.buffer);
  });
}

async function downloadTest(mb){
  active('download'); gl('Testing Download…');
  st('<span class="spin"></span>Starting download…');
  const target=mb*1024*1024;
  let got=0;
  const t0=performance.now();
  try{
    const resp=await fetch(`${B}/download?size_mb=${mb}&_=${Date.now()}`,{cache:'no-store'});
    const reader=resp.body.getReader();
    while(true){
      const{done:d,value:v}=await reader.read();
      if(d)break;
      got+=v.length;
      const el=(performance.now()-t0)/1000;
      const sp=(got*8)/(el*1e6);
      pf('download',got/target);
      sv('download',sp.toFixed(1),'Mbps');
      gauge(sp);
      st(`<span class="spin"></span>Downloading… ${(got/1024/1024).toFixed(1)}/${mb} MB — ${sp.toFixed(1)} Mbps`);
    }
    const el=(performance.now()-t0)/1000;
    const sp=(got*8)/(el*1e6);
    pf('download',1); sv('download',sp.toFixed(1),'Mbps'); done('download');
    return sp;
  }catch(e){pf('download',1);done('download');return 0;}
}

async function run(){
  const btn=document.getElementById('sb');
  btn.disabled=true; btn.innerHTML='<span class="spin"></span>Testing…';
  document.getElementById('results').style.display='none';
  document.getElementById('alerts').innerHTML='';
  gauge(0);
  const np=parseInt(document.getElementById('pc').value);
  const ds=parseInt(document.getElementById('dl').value);
  const us=parseInt(document.getElementById('ul').value);
  ['ping','upload','download'].forEach(s=>{
    document.getElementById('sp-'+s).classList.remove('active','done');
    pf(s,0); sv(s,'—',s==='ping'?'ms':'Mbps');
  });
  try{
    const pr=await pingTest(np);
    const dn=await downloadTest(ds);
    const up=await uploadTest(us);
    gauge(dn); gl('Test Complete ✓'); st('✅ All tests complete!');
    document.getElementById('r-dl').textContent=dn.toFixed(2);
    document.getElementById('r-ul').textContent=up.toFixed(2);
    document.getElementById('r-ms').textContent=pr.avg;
    document.getElementById('r-lo').textContent=pr.loss;
    document.getElementById('d-avg').textContent=pr.avg+' ms';
    document.getElementById('d-min').textContent=pr.min+' ms';
    document.getElementById('d-max').textContent=pr.max+' ms';
    document.getElementById('d-jit').textContent=pr.jitter+' ms';
    document.getElementById('d-pkt').textContent=pr.loss+'%';
    document.getElementById('d-dl').textContent=dn.toFixed(2)+' Mbps';
    document.getElementById('d-ul').textContent=up.toFixed(2)+' Mbps';
    document.getElementById('d-dls').textContent=ds+' MB';
    document.getElementById('d-uls').textContent=us+' MB';
    document.getElementById('results').style.display='block';
    const al=document.getElementById('alerts');
    if(parseFloat(pr.loss)>20)al.innerHTML+=`<div class="alert ae">⚠️ Very high packet loss (${pr.loss}%). Network is very unstable.</div>`;
    else if(parseFloat(pr.loss)>5)al.innerHTML+=`<div class="alert aw">⚠️ Moderate packet loss (${pr.loss}%) detected.</div>`;
    if(parseFloat(pr.avg)>150)al.innerHTML+=`<div class="alert aw">⚠️ High latency (${pr.avg} ms). Long distance or congestion.</div>`;
    if(parseFloat(pr.jitter)>50)al.innerHTML+=`<div class="alert aw">⚠️ High jitter (${pr.jitter} ms). VoIP/gaming affected.</div>`;
  }catch(e){st('❌ Error: '+e.message);}
  btn.disabled=false; btn.innerHTML='🔄 Run Again';
}
</script>
</body></html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML)

@app.get("/ping")
def ping():
    return {"pong": True, "server_time": time.time()}

@app.get("/download")
def download(size_mb: int = 25):
    size_mb = max(1, min(size_mb, 100))
    target  = size_mb * 1024 * 1024
    CHUNK   = b"Z" * 65536
    def generate():
        sent = 0
        while sent < target:
            block = min(len(CHUNK), target - sent)
            yield CHUNK[:block]
            sent += block
    return StreamingResponse(generate(), media_type="application/octet-stream",
        headers={"Content-Length": str(target), "Cache-Control": "no-store"})

@app.post("/upload")
async def upload(request: Request):
    start, total = time.perf_counter(), 0
    async for chunk in request.stream():
        total += len(chunk)
    dur = max(time.perf_counter() - start, 0.001)
    return JSONResponse({"bytes_received": total, "duration_s": round(dur,3),
                         "speed_mbps": round((total*8)/(dur*1_000_000), 2)})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)