"""Construit la page interactive (terminal cliquable, console, mini-jeu, radio) à partir du README.

Usage :
  python scripts/site/build_site.py               -> docs/index.html (GitHub Pages, images externes conservées)
  python scripts/site/build_site.py --preview OUT -> aperçu autonome (images externes remplacées par des cadres)
Dépendance : pip install markdown
"""
import re, base64, html, sys, markdown
from pathlib import Path
HERE = Path(__file__).resolve().parent
repo = HERE.parent.parent
PREVIEW = "--preview" in sys.argv
args = [a for a in sys.argv[1:] if a != "--preview"]
out = Path(args[0]) if args else repo / "docs" / "index.html"
md = (repo / "README.md").read_text(encoding="utf-8").replace("<details>", "<details markdown=\"1\">")
body = markdown.markdown(md, extensions=["fenced_code", "md_in_html"])

def local(m):
    src = m.group(1)
    data = base64.b64encode((repo / src.lstrip("./")).read_bytes()).decode()
    return m.group(0).replace(src, "data:image/svg+xml;base64," + data)
body = re.sub(r'<img[^>]*src="(\./assets/[^"]+)"[^>]*>', local, body)

def remote(m):
    tag = m.group(0); src = m.group(1)
    if "skillicons" in src:
        n = len(re.search(r"i=([^&]+)", src).group(1).split(","))
        label = f"{n} icônes de compétences"; cls = "ph wide"
    elif "shields.io" in src:
        label = re.search(r"badge/([^-?]+)", src).group(1).replace("%20", " "); cls = "ph badge"
    elif "komarev" in src:
        label = "Compteur de vues"; cls = "ph badge"
    elif "streak" in src:
        label = "Série de jours actifs"; cls = "ph card"
    elif "top-langs" in src:
        label = "Langages les plus utilisés"; cls = "ph card"
    else:
        label = "Statistiques GitHub"; cls = "ph card"
    return f'<span class="{cls}">{html.escape(label)}</span>'
if PREVIEW:
    body = re.sub(r'<img[^>]*src="(https?://[^"]+)"[^>]*>', remote, body)
body = re.sub(r'<p><img alt="([^"]*)"[^>]*></p>', "", body)

parts = re.split(r'<p><a name="(\w+)"></a>', body)
intro, secs = parts[0], dict(zip(parts[1::2], ["<p>" + x for x in parts[2::2]]))
for k in secs:
    secs[k] = re.sub(r'<img[^>]*alt="(STAT|INV|DATA|MAP|RADIO)"[^>]*>', "", secs[k], count=1)
intro_term = re.search(r'<img[^>]*alt="Terminal[^>]*>', intro).group(0)
intro_xp = re.search(r'<img[^>]*alt="Niveau[^>]*>', intro).group(0)
secs["stat"] = intro_term + secs["stat"]
TABS = ["stat", "inv", "data", "map", "radio"]
RADIO_PLAYER = """<div class="radio-player">
  <div class="rp-top"><button id="radio-btn">▶ ÉCOUTER</button><span id="radio-now">RADIO ABRI 27 · 06.27 MHz</span>
  <label class="rp-vol">VOL <input id="radio-vol" type="range" min="0" max="100" value="55"></label></div>
  <canvas id="osc" width="1000" height="170"></canvas>
  <div class="rp-note">Musique d'ambiance originale, composée en direct par le terminal.</div>
</div>"""
secs["radio"] = RADIO_PLAYER + secs["radio"]
tabs_html = "".join(f'<button data-t="{t}">{t.upper()}</button>' for t in TABS)
panels = "".join(f'<section class="panel" id="p-{t}">{secs[t]}</section>' for t in TABS)

NOTE = ('<p class="note">Les cadres en pointillés remplacent les icônes, badges et cartes de stats, chargés depuis des services externes '
        "qui ne s'affichent que sur GitHub.</p>") if PREVIEW else ""
page = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tiretinium · Terminal de l'Abri 27</title>
<style>
body{{margin:0;background:#0d1117;color:#e6edf3;font:16px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}
.top{{background:#161b22;border-bottom:1px solid #30363d;padding:10px 20px;font-size:13px;color:#8b949e}}
.top b{{color:#3dff86}}
.wrap{{max-width:1012px;margin:24px auto;padding:0 16px}}
.box{{border:1px solid #30363d;border-radius:6px}}
.box h3{{margin:0;padding:8px 16px;font-size:14px;border-bottom:1px solid #30363d;color:#e6edf3}}
.md{{padding:32px}}
.md img{{max-width:100%;vertical-align:middle}}
.md a{{color:#4493f8;text-decoration:none}}
.md code{{background:#6e768133;padding:.2em .4em;border-radius:6px;font-size:85%}}
.md pre{{background:#151b23;padding:16px;border-radius:6px;overflow:auto}}
.md pre code{{background:none;padding:0;font-size:85%}}
.md summary{{cursor:pointer;color:#3dff86;margin:8px 0}} .md sub{{font-size:75%}}
.ph{{display:inline-flex;align-items:center;justify-content:center;border:1px dashed #1d7a43;color:#2fb866;
  font:12px 'Courier New',monospace;background:#06100a;border-radius:6px;margin:3px;padding:0 10px}}
.ph.wide{{height:48px;min-width:420px}} .ph.badge{{height:28px}} .ph.card{{height:150px;width:46%;min-width:280px}}
.switch{{display:flex;gap:8px;justify-content:center;margin:18px 0}}
.switch button{{font:600 13px 'Courier New',monospace;letter-spacing:2px;background:#06100a;color:#2fb866;border:1px solid #1d7a43;padding:8px 16px;border-radius:6px;cursor:pointer}}
.switch button.on{{background:#3dff86;color:#06100a;border-color:#3dff86}}
.dev{{max-width:1080px;margin:10px auto 30px;padding:26px 30px 22px;background:linear-gradient(160deg,#3a3d38,#22241f 55%,#1a1b17);
  border-radius:34px;box-shadow:inset 0 2px 0 #55594f,inset 0 -3px 0 #0e0f0c,0 20px 50px #000a;position:relative}}
.dev:before,.dev:after{{content:"";position:absolute;width:10px;height:10px;border-radius:50%;background:#14150f;box-shadow:inset 1px 1px 0 #5c6055;top:12px}}
.dev:before{{left:16px}} .dev:after{{right:16px}}
.plate{{display:flex;justify-content:space-between;align-items:center;font:700 12px 'Courier New',monospace;letter-spacing:4px;color:#8c907f;margin:0 6px 12px}}
.knobs{{display:flex;gap:10px}} .knob{{width:26px;height:26px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#6b6f62,#2a2c25 70%);box-shadow:0 2px 3px #000}}
.lamp{{width:10px;height:10px;border-radius:50%;background:#3dff86;box-shadow:0 0 10px #3dff86;animation:lamp 2s infinite}}
@keyframes lamp{{50%{{opacity:.35}}}}
.crt{{background:radial-gradient(ellipse at center,#0b2414,#06100a 70%,#020604);border-radius:22px;border:2px solid #0e0f0c;padding:18px 22px 22px;
  position:relative;overflow:hidden;min-height:560px;box-shadow:inset 0 0 60px #000}}
.crt:after{{content:"";position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,#0006 0 2px,transparent 2px 4px)}}
.tabs{{display:flex;justify-content:space-around;border-bottom:2px solid #3dff86;margin-bottom:18px}}
.tabs button{{background:none;border:2px solid transparent;border-bottom:none;color:#1d9a52;font:700 17px 'Courier New',monospace;letter-spacing:3px;padding:6px 18px 4px;cursor:pointer;margin-bottom:-2px;text-shadow:0 0 6px #3dff8655}}
.tabs button.on{{color:#3dff86;border-color:#3dff86;background:#06100a;text-shadow:0 0 8px #3dff86}}
.tabs button:hover{{color:#3dff86}}
.panel{{display:none;color:#9fe8b8;font-family:'Courier New',monospace;animation:on .35s ease-out}}
.panel.on{{display:block}}
@keyframes on{{from{{opacity:0;filter:brightness(2.5) blur(1px)}}to{{opacity:1}}}}
.panel img{{max-width:100%;vertical-align:middle}} .panel a{{color:#3dff86}}
.panel pre{{background:#03080599;border:1px solid #1d7a43;border-radius:6px;padding:14px;overflow:auto;color:#3dff86}}
.panel code{{color:#3dff86}} .panel strong{{color:#3dff86}} .panel summary{{cursor:pointer;color:#3dff86;margin:10px 0}}
.panel p{{margin:10px 0}}
.hint{{text-align:center;font:12px 'Courier New',monospace;color:#5c6055;margin-top:12px;letter-spacing:1px}}
.hud{{margin-top:16px}} .hud img{{width:100%;display:block}}
.console{{margin-top:12px;border-top:1px solid #1d7a43;padding-top:10px;font:15px/1.45 'Courier New',monospace;color:#3dff86;text-shadow:0 0 6px #3dff8666}}
#out{{max-height:190px;overflow:auto;white-space:pre-wrap}} #out .dim{{color:#2fb866}} #out .err{{color:#ffb641}}
.prompt{{display:flex;align-items:center;margin-top:4px}}
#cmd{{flex:1;background:none;border:none;outline:none;color:#3dff86;font:inherit;text-shadow:inherit;caret-color:#3dff86}}
#cmd::placeholder{{color:#1d7a43}}
#hack{{position:absolute;inset:0;background:#06100af2;z-index:5;padding:26px 30px;font:15px/1.5 'Courier New',monospace;color:#3dff86;text-shadow:0 0 6px #3dff8666;overflow:auto}}
#hack .grid{{display:flex;gap:40px;margin-top:14px}} #hack .col{{white-space:pre}} #hack .addr{{color:#1d9a52}}
#hack .w{{cursor:pointer}} #hack .w.hl{{background:#3dff86;color:#06100a}}
#hack .log{{flex:1;min-width:220px;display:flex;flex-direction:column;justify-content:flex-end;white-space:pre-wrap}}
#hack button{{background:none;border:1px solid #3dff86;color:#3dff86;font:inherit;padding:4px 12px;cursor:pointer;margin-top:12px}}
#hack button:hover{{background:#3dff86;color:#06100a}}
#boot{{position:absolute;inset:0;z-index:10;background:#020604;font:15px/1.55 'Courier New',monospace;color:#3dff86;text-shadow:0 0 8px #3dff8699;padding:30px 34px;cursor:pointer;overflow:hidden}}
#boot.off{{animation:bootoff .6s ease-in forwards}}
@keyframes bootoff{{0%{{opacity:1;filter:brightness(1)}}30%{{filter:brightness(3)}}100%{{opacity:0;visibility:hidden}}}}
#boot .beam{{position:absolute;left:0;right:0;top:50%;height:2px;background:#d9ffe6;box-shadow:0 0 30px 8px #3dff86;transform:scaleX(0);animation:beam .9s ease-out forwards}}
@keyframes beam{{0%{{transform:scaleX(0);opacity:1}}45%{{transform:scaleX(1);height:2px;top:50%;opacity:1}}100%{{transform:scaleX(1);height:100%;top:0;opacity:0}}}}
#bootlog{{white-space:pre-wrap;opacity:0;animation:fadein .1s .8s forwards}} @keyframes fadein{{to{{opacity:1}}}}
#bootlog .ok{{color:#3dff86}} #bootlog .dim{{color:#1d9a52}}
#boot .skip{{position:absolute;right:24px;bottom:16px;font-size:12px;color:#1d7a43;letter-spacing:2px}}
.radio-player{{border:1px solid #1d7a43;border-radius:10px;padding:14px 16px;margin-bottom:16px;background:#03080599}}
.rp-top{{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:10px}}
#radio-btn{{background:#3dff86;color:#06100a;border:none;font:700 15px 'Courier New',monospace;letter-spacing:2px;padding:8px 16px;cursor:pointer;border-radius:4px}}
#radio-btn:hover{{filter:brightness(1.15)}} #radio-now{{color:#3dff86;letter-spacing:2px;flex:1}}
.rp-vol{{color:#2fb866;font-size:13px;display:flex;align-items:center;gap:8px}} .rp-vol input{{accent-color:#3dff86}}
#osc{{width:100%;height:auto;display:block;border:1px solid #1d7a43;border-radius:6px}}
.rp-note{{font-size:12px;color:#1d9a52;margin-top:6px}}
.view{{display:none}} .view.on{{display:block}}
.note{{font-size:13px;color:#8b949e;margin:12px 0 0}}
</style></head><body>
<div class="top">Profil <b>Tiretinium</b> · terminal de l'Abri 27 · <a href='https://github.com/Tiretinium' style='color:#3dff86'>github.com/Tiretinium</a></div>
<div class="switch"><button data-v="dev" class="on">VUE TERMINAL</button><button data-v="gh">VUE GITHUB</button></div>
<div class="view on" id="v-dev"><div class="dev">
  <div class="plate"><span class="knobs"><span class="knob"></span><span class="knob"></span></span><span>TERMINAL PORTATIF T-27</span><span class="lamp"></span></div>
  <div class="crt"><nav class="tabs">{tabs_html}</nav>{panels}
    <div class="hud">{intro_xp}</div>
    <div class="console"><div id="out"></div><label class="prompt">&gt;&nbsp;<input id="cmd" autocomplete="off" spellcheck="false" placeholder="tape help puis Entrée"></label></div>
    <div id="hack" hidden></div>
    <div id="boot"><div class="beam"></div><div id="bootlog"></div><div class="skip">clique pour passer</div></div>
  </div>
  <div class="hint">Onglets cliquables · flèches ← → · tape <b>help</b> dans la console ou <b>hack</b> pour pirater le terminal</div>
</div></div>
<div class="view" id="v-gh"><div class="wrap">
<div class="box"><h3>Tiretinium / README.md</h3><div class="md">{body}</div></div>
{NOTE}
</div></div>
<script>
const T={TABS!r};
function show(t){{document.querySelectorAll('.tabs button').forEach(b=>b.classList.toggle('on',b.dataset.t===t));
 document.querySelectorAll('.panel').forEach(p=>{{const on=p.id==='p-'+t;p.classList.remove('on');if(on){{void p.offsetWidth;p.classList.add('on');
 p.querySelectorAll('img').forEach(i=>{{const s=i.src;i.src='';i.src=s;}});}}}});cur=t;}}
let cur='stat';
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>show(b.dataset.t));
document.addEventListener('keydown',e=>{{const i=T.indexOf(cur);if(e.key==='ArrowRight')show(T[(i+1)%T.length]);if(e.key==='ArrowLeft')show(T[(i+T.length-1)%T.length]);}});
document.querySelectorAll('.switch button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.switch button').forEach(x=>x.classList.toggle('on',x===b));
 document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on',v.id==='v-'+b.dataset.v));}});
document.querySelectorAll('.panel a[href^="#"]').forEach(a=>a.onclick=e=>{{e.preventDefault();show(a.getAttribute('href').slice(1));}});
show('stat');
JS_CONSOLE
</script></body></html>"""
page = page.replace("JS_CONSOLE", (HERE / "console.js").read_text(encoding="utf-8") + "\n" + (HERE / "radio.js").read_text(encoding="utf-8"))
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(page, encoding="utf-8")
print(out, len(page))
