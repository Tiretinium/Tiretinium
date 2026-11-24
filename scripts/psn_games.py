"""Derniers jeux joués sur PlayStation (nom, plateforme, temps de jeu, dernière partie).

Usage : python scripts/psn_games.py <fichier_sortie.svg> [jeux.json]
Le jeton NPSSO est lu dans la variable d'environnement PSN_NPSSO (secret GitHub).
Bibliothèque non officielle : psnawp (pip install psnawp).
- Pas de jeton -> écran « en attente du signal ».
- Jeton expiré / erreur -> on garde l'ancien écran s'il existe (le workflow ne plante pas).
Seuls les noms des jeux et tes stats sont affichés, pas les jaquettes.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

OUT = Path(sys.argv[1])
G, G_MID, G_DIM, G_DARK, BG, BEZEL = "#3dff86", "#2fb866", "#1d7a43", "#0c2a17", "#06100a", "#151515"
FONT = "'Courier New', 'DejaVu Sans Mono', Menlo, Consolas, monospace"
LIMIT = 6
PLATFORMS = {"ps5_native_game": "PS5", "ps4_game": "PS4", "pspc_game": "PC"}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def short(s, n=34):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def frame(body, h, status):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{h}" viewBox="0 0 1200 {h}">
  <defs>
    <filter id="glow" x="-10%" y="-20%" width="120%" height="140%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <radialGradient id="glass" cx=".5" cy=".5" r=".75"><stop offset="0" stop-color="#0b2414"/><stop offset=".7" stop-color="{BG}"/><stop offset="1" stop-color="#020604"/></radialGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".35"/></pattern>
    <style>text {{ font-family: {FONT}; fill: {G}; }} .dim {{ fill: {G_MID}; }} .b {{ font-weight: 700; }}
      .blink {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0 }} }}</style>
  </defs>
  <rect width="1200" height="{h}" rx="16" fill="{BEZEL}"/>
  <rect x="20" y="20" width="1160" height="{h - 40}" rx="22" fill="url(#glass)"/>
  <g filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">DERNIERS JEUX</text>
    <text x="1148" y="58" font-size="14" text-anchor="end" class="dim">{esc(status)}</text>
    <line x1="52" y1="72" x2="1148" y2="72" stroke="{G_DIM}"/>
    {body}
  </g>
  <rect x="20" y="20" width="1160" height="{h - 40}" rx="22" fill="url(#scan)"/>
  <rect x="20" y="20" width="1160" height="{h - 40}" rx="22" fill="none" stroke="{G_DIM}" stroke-opacity=".5" stroke-width="1.5"/>
</svg>
'''


def waiting(msg):
    body = (f'<text x="56" y="124" font-size="17">{esc(msg)}<tspan class="blink">_</tspan></text>'
            f'<text x="56" y="154" font-size="13" class="dim">Le terminal réessaiera au prochain passage.</text>')
    return frame(body, 200, "SIGNAL PLAYSTATION")


def load_games():
    if len(sys.argv) > 2:                               # mode test : fichier JSON
        raw = json.load(open(sys.argv[2], encoding="utf-8"))
        return [(g["name"], g["category"], timedelta(minutes=g["minutes"]), datetime.fromisoformat(g["last"])) for g in raw]
    from psnawp_api import PSNAWP
    me = PSNAWP(os.environ["PSN_NPSSO"]).me()
    games = []
    for t in me.title_stats(limit=LIMIT * 2):
        games.append((t.name, t.category, t.play_duration or timedelta(0), t.last_played_date_time))
    games.sort(key=lambda g: g[3] or datetime.min.replace(tzinfo=ZoneInfo("UTC")), reverse=True)
    return games[:LIMIT]


if len(sys.argv) <= 2 and not os.environ.get("PSN_NPSSO"):
    OUT.write_text(waiting("EN ATTENTE DU SIGNAL PSN"), encoding="utf-8")
    print("PSN_NPSSO absent : écran d'attente écrit")
    sys.exit(0)

try:
    games = load_games()
except Exception as e:  # jeton expiré, API modifiée, réseau...
    print(f"PSN indisponible ({type(e).__name__}: {e})")
    if not OUT.exists() or "EN ATTENTE" in OUT.read_text(encoding="utf-8"):
        OUT.write_text(waiting("SIGNAL PSN PERDU · JETON À RENOUVELER"), encoding="utf-8")
    sys.exit(0)

hours = [g[2].total_seconds() / 3600 for g in games]
mx = max(hours) if hours and max(hours) > 0 else 1
rows = []
for i, ((name, cat, dur, last), h) in enumerate(zip(games, hours)):
    y = 122 + i * 44
    b = .3 + i * .25
    plat = PLATFORMS.get(str(cat).lower(), "PS")
    when = last.astimezone(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y") if last else "—"
    bw = 220 * h / mx
    rows.append(f'''<g opacity="0"><set attributeName="opacity" to="1" begin="{b:.2f}s" fill="freeze"/>
      <rect x="56" y="{y - 18}" width="26" height="22" rx="3" fill="none" stroke="{G}" stroke-width="1.6"/>
      <circle cx="69" cy="{y - 7}" r="5" fill="none" stroke="{G}" stroke-width="1.4"/>
      <text x="100" y="{y}" font-size="17">{esc(short(name))}</text>
      <rect x="520" y="{y - 17}" width="52" height="22" rx="3" fill="none" stroke="{G_DIM}"/>
      <text x="546" y="{y - 1}" font-size="13" text-anchor="middle" class="b">{plat}</text>
      <rect x="600" y="{y - 13}" width="0" height="12" fill="{G_MID}">
        <animate attributeName="width" from="0" to="{bw:.1f}" begin="{b:.2f}s" dur=".6s" fill="freeze"/></rect>
      <text x="{600 + 232}" y="{y}" font-size="15">{h:.0f} h</text>
      <text x="1148" y="{y}" font-size="14" text-anchor="end" class="dim">{when}</text></g>''')
if not rows:
    rows.append(f'<text x="56" y="124" font-size="17" class="dim">Aucun jeu trouvé sur ce compte.</text>')
header = (f'<text x="100" y="92" font-size="11" class="dim" letter-spacing="2">JEU</text>'
          f'<text x="546" y="92" font-size="11" text-anchor="middle" class="dim" letter-spacing="2">CONSOLE</text>'
          f'<text x="600" y="92" font-size="11" class="dim" letter-spacing="2">TEMPS DE JEU</text>'
          f'<text x="1148" y="92" font-size="11" text-anchor="end" class="dim" letter-spacing="2">DERNIÈRE PARTIE</text>')
h_svg = 122 + max(len(rows), 1) * 44 + 30
now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y")
OUT.write_text(frame(header + "".join(rows), h_svg, f"PLAYSTATION · MAJ {now}"), encoding="utf-8")
print(f"{OUT} : {len(games)} jeu(x)")
