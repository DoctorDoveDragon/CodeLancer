"""
codelancer.api.gui
Self-contained HTML GUI served at GET /ui.
No external dependencies – all CSS and JS are inlined.
"""

GUI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CODELANCER AI</title>
<style>
:root{
  --bg:#0d1117;--surface:#161b22;--border:#30363d;
  --accent:#58a6ff;--accent2:#bc8cff;
  --text:#e6edf3;--muted:#8b949e;
  --ok:#3fb950;--err:#f85149;--warn:#d29922;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:var(--bg);color:var(--text);min-height:100vh}
header{background:var(--surface);border-bottom:1px solid var(--border);
  padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between}
header h1{font-size:1.4rem;font-weight:700;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text}
.badges{display:flex;gap:.6rem;align-items:center}
.badge{display:inline-flex;align-items:center;gap:.35rem;font-size:.72rem;
  padding:.22rem .55rem;border-radius:2rem;border:1px solid var(--border)}
.badge.ok{border-color:var(--ok);color:var(--ok)}
.badge.err{border-color:var(--err);color:var(--err)}
.badge.dev{border-color:var(--warn);color:var(--warn)}
.dot{width:6px;height:6px;border-radius:50%;background:currentColor}
nav{background:var(--surface);border-bottom:1px solid var(--border);
  padding:0 2rem;display:flex;gap:.25rem;align-items:stretch}
.tab{padding:.7rem 1rem;font-size:.85rem;color:var(--muted);background:none;
  border:none;border-bottom:2px solid transparent;cursor:pointer;
  transition:color .15s,border-color .15s;white-space:nowrap}
.tab:hover{color:var(--text)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.docs-link{color:var(--accent2) !important;text-decoration:none;
  margin-left:auto;display:none;align-items:center}
main{padding:1.75rem 2rem;max-width:1100px;margin:0 auto}
.panel{display:none}.panel.active{display:block}
.card{background:var(--surface);border:1px solid var(--border);
  border-radius:.5rem;padding:1.5rem;margin-bottom:1.5rem}
.card h2{font-size:1rem;font-weight:600;margin-bottom:1.1rem}
label{display:block;font-size:.8rem;color:var(--muted);margin-bottom:.35rem}
textarea,select,input[type=text],input[type=number]{
  width:100%;background:var(--bg);border:1px solid var(--border);
  color:var(--text);border-radius:.35rem;padding:.55rem .75rem;
  font-size:.85rem;font-family:inherit;resize:vertical}
textarea{font-family:'Fira Code','Consolas',monospace;min-height:40px}
textarea:focus,select:focus,input:focus{outline:none;border-color:var(--accent)}
.row{display:flex;gap:1rem;align-items:flex-end;margin-bottom:.9rem}
.row .f{flex:1}
.btn{display:inline-flex;align-items:center;gap:.4rem;padding:.45rem 1.1rem;
  border-radius:.35rem;font-size:.85rem;font-weight:500;cursor:pointer;
  transition:opacity .15s;border:none}
.btn-p{background:var(--accent);color:#0d1117}
.btn-p:hover{opacity:.85}
.btn-p:disabled{opacity:.45;cursor:not-allowed}
.result{margin-top:1rem}
pre{background:var(--bg);border:1px solid var(--border);border-radius:.35rem;
  padding:.9rem;font-size:.78rem;overflow-x:auto;white-space:pre-wrap;
  font-family:'Fira Code','Consolas',monospace;line-height:1.55}
.meta{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:.75rem}
.chip{background:var(--bg);border:1px solid var(--border);border-radius:.25rem;
  padding:.25rem .55rem;font-size:.72rem}
.chip span{color:var(--accent);font-weight:600}
.errmsg{background:rgba(248,81,73,.1);border:1px solid var(--err);
  color:var(--err);border-radius:.35rem;padding:.7rem;font-size:.85rem;margin-top:.75rem}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));
  gap:.65rem;margin-bottom:.9rem}
.stat{background:var(--bg);border:1px solid var(--border);border-radius:.35rem;
  padding:.65rem;text-align:center}
.stat .v{font-size:1.35rem;font-weight:700;color:var(--accent)}
.stat .l{font-size:.72rem;color:var(--muted);margin-top:.15rem}
.syntax-ok{color:var(--ok)}.syntax-err{color:var(--err)}
.sugg{list-style:none;margin-top:.6rem}
.sugg li{font-size:.8rem;color:var(--muted);padding:.12rem 0}
.sugg li::before{content:'💡 '}
.fix-list{list-style:none;margin:.5rem 0}
.fix-list li{font-size:.78rem;color:var(--ok);padding:.1rem 0}
.fix-list li::before{content:'✓ '}
.spinner{display:inline-block;width:13px;height:13px;
  border:2px solid rgba(255,255,255,.25);border-top-color:currentColor;
  border-radius:50%;animation:spin .55s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.log-wrap{max-height:500px;overflow-y:auto;border:1px solid var(--border);
  border-radius:.35rem}
.log-row{display:flex;gap:.65rem;align-items:flex-start;padding:.38rem .6rem;
  border-bottom:1px solid var(--border);font-size:.77rem}
.log-row:last-child{border-bottom:none}
.log-ts{color:var(--muted);min-width:170px;flex-shrink:0;font-size:.7rem}
.lvl{min-width:58px;padding:.12rem .35rem;border-radius:.2rem;text-align:center;
  font-size:.68rem;font-weight:600;flex-shrink:0}
.lvl.DEBUG{background:rgba(139,148,158,.18);color:var(--muted)}
.lvl.INFO{background:rgba(88,166,255,.15);color:var(--accent)}
.lvl.WARNING{background:rgba(210,153,34,.15);color:var(--warn)}
.lvl.ERROR,.lvl.CRITICAL{background:rgba(248,81,73,.15);color:var(--err)}
.log-msg{color:var(--text);flex:1;word-break:break-all}
.toolbar{display:flex;gap:.65rem;flex-wrap:wrap;margin-bottom:1rem;align-items:flex-end}
.toolbar .f{flex:1;min-width:110px}
.empty{color:var(--muted);font-size:.85rem;padding:.5rem 0}
.log-range-display{font-size:.8rem;color:var(--muted);margin-bottom:.75rem;
  padding:.5rem .75rem;background:var(--bg);border:1px solid var(--border);
  border-radius:.35rem;display:flex;align-items:center;gap:.5rem}
.log-range-display .range-sep{color:var(--border)}
.log-range-display .range-ts{color:var(--accent);font-weight:500}
.log-boundary{text-align:center;font-size:.75rem;color:var(--muted);
  padding:.45rem;border:1px dashed var(--border);border-radius:.25rem;margin:.35rem 0}
</style>
</head>
<body>
<header>
  <h1>&#9889; CODELANCER AI</h1>
  <div class="badges">
    <span id="hbadge" class="badge"><span class="dot"></span> Checking&hellip;</span>
    <span id="dbadge" class="badge dev" style="display:none"><span class="dot"></span> DEV MODE</span>
  </div>
</header>
<nav>
  <button class="tab active" data-tab="analyze">Analyze</button>
  <button class="tab" data-tab="generate">Generate</button>
  <button class="tab" data-tab="correct">Correct</button>
  <button class="tab" data-tab="logs">Logs</button>
  <a id="docs-link" class="tab docs-link" href="/docs" target="_blank" rel="noopener">Swagger Docs &#8599;</a>
</nav>
<main>

<!-- Analyze -->
<div class="panel active" id="panel-analyze">
  <div class="card">
    <h2>Code Analyzer</h2>
    <div class="row">
      <div class="f"><label for="ana-lang">Language</label>
        <select id="ana-lang">
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="typescript">TypeScript</option>
          <option value="other">Other</option>
        </select>
      </div>
    </div>
    <label for="ana-code">Code</label>
    <textarea id="ana-code" rows="12" placeholder="Paste code to analyze&hellip;"></textarea>
    <div style="margin-top:.75rem">
      <button class="btn btn-p" id="ana-btn"><span>Analyze</span></button>
    </div>
    <div id="ana-res" class="result"></div>
  </div>
</div>

<!-- Generate -->
<div class="panel" id="panel-generate">
  <div class="card">
    <h2>Code Generator</h2>
    <div class="row">
      <div class="f"><label for="gen-lang">Language</label>
        <select id="gen-lang">
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
        </select>
      </div>
    </div>
    <label for="gen-desc">Description</label>
    <textarea id="gen-desc" rows="4" placeholder="Describe what you want to generate&hellip;"></textarea>
    <label for="gen-ctx" style="margin-top:.75rem">Context <span style="font-size:.72rem">(optional)</span></label>
    <textarea id="gen-ctx" rows="3" placeholder="Optional context or existing code&hellip;"></textarea>
    <div style="margin-top:.75rem">
      <button class="btn btn-p" id="gen-btn"><span>Generate</span></button>
    </div>
    <div id="gen-res" class="result"></div>
  </div>
</div>

<!-- Correct -->
<div class="panel" id="panel-correct">
  <div class="card">
    <h2>Auto-Corrector</h2>
    <div class="row">
      <div class="f"><label for="cor-lang">Language</label>
        <select id="cor-lang">
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
        </select>
      </div>
    </div>
    <label for="cor-code">Code to Correct</label>
    <textarea id="cor-code" rows="12" placeholder="Paste code with bugs or typos&hellip;"></textarea>
    <div style="margin-top:.75rem">
      <button class="btn btn-p" id="cor-btn"><span>Correct</span></button>
    </div>
    <div id="cor-res" class="result"></div>
  </div>
</div>

<!-- Logs -->
<div class="panel" id="panel-logs">
  <div class="card">
    <h2>Filter and search logs</h2>
    <div class="toolbar">
      <div class="f"><label for="log-range">Time range</label>
        <select id="log-range">
          <option value="">All time</option>
          <option value="15">Last 15 min</option>
          <option value="60">Last 1 hour</option>
          <option value="360">Last 6 hours</option>
          <option value="1440">Last 24 hours</option>
        </select>
      </div>
      <div class="f"><label for="log-lvl">Level</label>
        <select id="log-lvl">
          <option value="">All</option>
          <option value="DEBUG">DEBUG</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>
      </div>
      <div class="f"><label for="log-srch">Search</label>
        <input type="text" id="log-srch" placeholder="Filter messages&hellip;">
      </div>
      <div class="f" style="max-width:90px"><label for="log-lim">Limit</label>
        <!-- max=1000 matches server-side le=1000 constraint on /logs -->
        <input type="number" id="log-lim" value="50" min="1" max="1000">
      </div>
      <button class="btn btn-p" id="log-btn"><span>Refresh</span></button>
    </div>
    <div id="log-range-display" class="log-range-display" style="display:none">
      <span>&#128337;</span>
      <span class="range-ts" id="log-range-from"></span>
      <span class="range-sep">&mdash;</span>
      <span class="range-ts" id="log-range-to"></span>
    </div>
    <div id="log-res"></div>
  </div>
</div>

</main>
<script>
(function(){
  // Tab navigation
  var tabs = document.querySelectorAll('.tab[data-tab]');
  var panels = document.querySelectorAll('.panel');
  tabs.forEach(function(t){
    t.addEventListener('click', function(){
      tabs.forEach(function(x){ x.classList.remove('active'); });
      panels.forEach(function(p){ p.classList.remove('active'); });
      t.classList.add('active');
      document.getElementById('panel-'+t.dataset.tab).classList.add('active');
      if(t.dataset.tab==='logs') loadLogs();
    });
  });

  function esc(s){
    return String(s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function errHtml(msg){
    return '<div class="errmsg">&#9888; '+esc(msg)+'</div>';
  }
  function spin(btn,label){
    btn.disabled=true;
    btn.innerHTML='<span class="spinner"></span> '+esc(label)+'&hellip;';
  }
  function restore(btn,label){
    btn.disabled=false;
    btn.innerHTML='<span>'+esc(label)+'</span>';
  }
  function post(path,body){
    return fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(body)}).then(function(r){
        if(!r.ok) return r.text().then(function(t){ throw new Error(t); });
        return r.json();
      });
  }

  // Status check
  fetch('/').then(function(r){ return r.json(); }).then(function(d){
    var b=document.getElementById('hbadge');
    b.className='badge ok';
    b.innerHTML='<span class="dot"></span> Healthy';
    if(d.dev){
      document.getElementById('dbadge').style.display='';
      var dl=document.getElementById('docs-link');
      dl.style.display='flex';
    }
  }).catch(function(){
    var b=document.getElementById('hbadge');
    b.className='badge err';
    b.innerHTML='<span class="dot"></span> Offline';
  });

  // Analyze
  document.getElementById('ana-btn').addEventListener('click', function(){
    var btn=this, code=document.getElementById('ana-code').value.trim();
    var lang=document.getElementById('ana-lang').value;
    var res=document.getElementById('ana-res');
    if(!code){ res.innerHTML=errHtml('Please enter some code to analyze.'); return; }
    spin(btn,'Analyzing');
    post('/analyze',{code:code,language:lang}).then(function(d){
      var a=d.analysis;
      var sy=a.syntax_valid
        ?'<span class="syntax-ok">&#10003; Valid</span>'
        :'<span class="syntax-err">&#10007; '+esc(a.syntax_error||'Invalid')+'</span>';
      var sugg=d.suggestions&&d.suggestions.length
        ?'<ul class="sugg">'+d.suggestions.map(function(s){return '<li>'+esc(s)+'</li>';}).join('')+'</ul>'
        :'';
      res.innerHTML=
        '<div class="stat-grid">'
        +'<div class="stat"><div class="v">'+a.lines+'</div><div class="l">Lines</div></div>'
        +'<div class="stat"><div class="v">'+a.characters+'</div><div class="l">Characters</div></div>'
        +'<div class="stat"><div class="v">'+a.words+'</div><div class="l">Words</div></div>'
        +'<div class="stat"><div class="v">'+a.estimated_complexity+'</div><div class="l">Complexity</div></div>'
        +'<div class="stat"><div class="v">'+a.density+'</div><div class="l">Density</div></div>'
        +'</div>'
        +'<div style="font-size:.85rem">Syntax: '+sy+'</div>'
        +sugg;
    }).catch(function(e){ res.innerHTML=errHtml(e.message); })
    .finally(function(){ restore(btn,'Analyze'); });
  });

  // Generate
  document.getElementById('gen-btn').addEventListener('click', function(){
    var btn=this, desc=document.getElementById('gen-desc').value.trim();
    var ctx=document.getElementById('gen-ctx').value.trim();
    var lang=document.getElementById('gen-lang').value;
    var res=document.getElementById('gen-res');
    if(!desc){ res.innerHTML=errHtml('Please enter a description.'); return; }
    spin(btn,'Generating');
    var body={description:desc,language:lang};
    if(ctx) body.context=ctx;
    post('/generate',body).then(function(d){
      res.innerHTML=
        '<div class="meta">'
        +'<div class="chip">Function: <span>'+esc(d.function_name||'')+'</span></div>'
        +'<div class="chip">At: <span>'+esc(d.timestamp||'')+'</span></div>'
        +'</div>'
        +'<pre>'+esc(d.generated_code||'')+'</pre>';
    }).catch(function(e){ res.innerHTML=errHtml(e.message); })
    .finally(function(){ restore(btn,'Generate'); });
  });

  // Correct
  document.getElementById('cor-btn').addEventListener('click', function(){
    var btn=this, code=document.getElementById('cor-code').value.trim();
    var lang=document.getElementById('cor-lang').value;
    var res=document.getElementById('cor-res');
    if(!code){ res.innerHTML=errHtml('Please enter some code to correct.'); return; }
    spin(btn,'Correcting');
    post('/correct',{code:code,language:lang}).then(function(d){
      var fixes=d.corrections||[];
      res.innerHTML=
        '<div class="meta"><div class="chip">Fixes applied: <span>'+(d.total_fixes||0)+'</span></div></div>'
        +(fixes.length?'<ul class="fix-list">'+fixes.map(function(f){return '<li>'+esc(f)+'</li>';}).join('')+'</ul>':'')
        +'<pre>'+esc(d.corrected||'')+'</pre>';
    }).catch(function(e){ res.innerHTML=errHtml(e.message); })
    .finally(function(){ restore(btn,'Correct'); });
  });

  // Logs
  function fmtTs(iso){
    if(!iso) return '';
    try{ return new Date(iso).toLocaleString(); }catch(e){ return iso; }
  }
  function loadLogs(){
    var btn=document.getElementById('log-btn');
    var range=document.getElementById('log-range').value;
    var lvl=document.getElementById('log-lvl').value;
    var srch=document.getElementById('log-srch').value.trim();
    var lim=document.getElementById('log-lim').value||50;
    var res=document.getElementById('log-res');
    var rangeDisplay=document.getElementById('log-range-display');
    spin(btn,'Loading');
    var url='/logs?limit='+encodeURIComponent(lim);
    if(lvl) url+='&level='+encodeURIComponent(lvl);
    if(srch) url+='&search='+encodeURIComponent(srch);
    var sinceTs=null, untilTs=null;
    if(range){
      sinceTs=new Date(Date.now()-parseInt(range,10)*60000).toISOString();
      untilTs=new Date().toISOString();
      url+='&since='+encodeURIComponent(sinceTs);
      url+='&until='+encodeURIComponent(untilTs);
    }
    fetch(url).then(function(r){ return r.json(); }).then(function(d){
      // Date range display
      var from=d.from_time||sinceTs, to=d.to_time||untilTs;
      if(from||to){
        document.getElementById('log-range-from').textContent=fmtTs(from)||'';
        document.getElementById('log-range-to').textContent=fmtTs(to)||'';
        rangeDisplay.style.display='flex';
      } else {
        rangeDisplay.style.display='none';
      }
      if(!d.logs.length){
        res.innerHTML='<p class="empty">No log entries found.</p>';
      } else {
        var startMsg='You reached the start of the range'+(from?' '+fmtTs(from):'');
        var endMsg='You reached the end of the range'+(to?' '+fmtTs(to):'');
        res.innerHTML=
          '<div class="log-boundary">&#8593; '+esc(startMsg)+'</div>'
          +'<div class="log-wrap">'
          +d.logs.slice().reverse().map(function(l){
            return '<div class="log-row">'
              +'<span class="log-ts">'+esc(l.timestamp)+'</span>'
              +'<span class="lvl '+esc(l.level)+'">'+esc(l.level)+'</span>'
              +'<span class="log-msg">'+esc(l.message)+'</span>'
              +'</div>';
          }).join('')
          +'</div>'
          +'<div class="log-boundary">&#8595; '+esc(endMsg)+'</div>';
      }
    }).catch(function(e){ res.innerHTML=errHtml(e.message); })
    .finally(function(){ restore(btn,'Refresh'); });
  }
  document.getElementById('log-btn').addEventListener('click', loadLogs);
})();
</script>
</body>
</html>"""
