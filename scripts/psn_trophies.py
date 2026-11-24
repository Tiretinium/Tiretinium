"""Trophées PlayStation : niveau + nombre de platines, or, argent, bronze.

Usage : python scripts/psn_trophies.py <fichier_sortie.svg> [trophees.json]
Le jeton NPSSO est lu dans PSN_NPSSO (même secret que psn_games.py).
- Pas de jeton -> écran « en attente du signal ».
- Erreur (jeton expiré...) -> on garde l'ancien écran s'il existe.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

OUT = Path(sys.argv[1])
G, G_MID, G_DIM, G_DARK, BG, BEZEL = "#3dff86", "#2fb866", "#1d7a43", "#0c2a17", "#06100a", "#151515"
FONT = "'Courier New', 'DejaVu Sans Mono', Menlo, Consolas, monospace"
W, H = 1200, 300


def frame(body, status):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <filter id="glow" x="-10%" y="-20%" width="120%" height="140%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <radialGradient id="glass" cx=".5" cy=".5" r=".75"><stop offset="0" stop-color="#0b2414"/><stop offset=".7" stop-color="{BG}"/><stop offset="1" stop-color="#020604"/></radialGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".35"/></pattern>
    <style>text {{ font-family: {FONT}; fill: {G}; }} .dim {{ fill: {G_MID}; }} .b {{ font-weight: 700; }}
      .blink {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0 }} }}</style>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="url(#glass)"/>
  <g filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">TROPHÉES</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">{status}</text>
    <line x1="52" y1="72" x2="{W - 52}" y2="72" stroke="{G_DIM}"/>
    {body}
  </g>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="url(#scan)"/>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="none" stroke="{G_DIM}" stroke-opacity=".5" stroke-width="1.5"/>
</svg>
'''


def waiting(msg):
    return frame(f'<text x="56" y="130" font-size="17">{msg}<tspan class="blink">_</tspan></text>'
                 f'<text x="56" y="160" font-size="13" class="dim">Le terminal réessaiera au prochain passage.</text>', "SIGNAL PLAYSTATION")


def cup(cx, cy, s, filled):
    """Coupe de trophée (dessin générique)."""
    f = G if filled else G_DARK
    return (f'<g transform="translate({cx} {cy}) scale({s})">'
            f'<path d="M-18,-26 L18,-26 L16,-4 Q14,10 0,12 Q-14,10 -16,-4 Z" fill="{f}" stroke="{G}" stroke-width="2.2" stroke-linejoin="round"/>'
            f'<path d="M-18,-20 Q-30,-20 -28,-8 Q-26,2 -15,2 M18,-20 Q30,-20 28,-8 Q26,2 15,2" fill="none" stroke="{G}" stroke-width="2.2"/>'
            f'<path d="M-4,12 L4,12 L5,22 L-5,22 Z" fill="{G_DARK}" stroke="{G}" stroke-width="2"/>'
            f'<rect x="-13" y="22" width="26" height="7" rx="1.5" fill="{G_DARK}" stroke="{G}" stroke-width="2"/></g>')


if len(sys.argv) > 2:
    data = json.load(open(sys.argv[2], encoding="utf-8"))
elif not os.environ.get("PSN_NPSSO"):
    OUT.write_text(waiting("EN ATTENTE DU SIGNAL PSN"), encoding="utf-8")
    print("PSN_NPSSO absent : écran d'attente écrit")
    sys.exit(0)
else:
    try:
        from psnawp_api import PSNAWP
        s = PSNAWP(os.environ["PSN_NPSSO"]).me().trophy_summary()
        e = s.earned_trophies
        data = {"level": s.trophy_level, "progress": s.progress, "platinum": e.platinum, "gold": e.gold, "silver": e.silver, "bronze": e.bronze}
    except Exception as ex:
        print(f"PSN indisponible ({type(ex).__name__}: {ex})")
        if not OUT.exists() or "EN ATTENTE" in OUT.read_text(encoding="utf-8"):
            OUT.write_text(waiting("SIGNAL PSN PERDU · JETON À RENOUVELER"), encoding="utf-8")
        sys.exit(0)

level, prog = int(data["level"]), int(data.get("progress") or 0)
tiers = [("PLATINE", data["platinum"], 1.25), ("OR", data["gold"], 1.05), ("ARGENT", data["silver"], .95), ("BRONZE", data["bronze"], .85)]
total = sum(t[1] for t in tiers)

# niveau : grand chiffre + jauge de progression vers le niveau suivant
segs = 20
on = round(prog / 100 * segs)
gauge = "".join(
    f'<rect x="{56 + k * 17}" y="214" width="13" height="16" fill="{G if k < on else "none"}" stroke="{G_DIM}" opacity="0">'
    f'<set attributeName="opacity" to="1" begin="{.4 + k * .04:.2f}s" fill="freeze"/></rect>'
    for k in range(segs)
)
left = (f'<text x="56" y="112" font-size="13" class="dim" letter-spacing="2">NIVEAU DE TROPHÉES</text>'
        f'<text x="56" y="186" font-size="72" class="b">{level}</text>'
        f'<text x="{56 + 46 * len(str(level)) + 16}" y="186" font-size="15" class="dim">{total} trophées</text>'
        f'{gauge}<text x="{56 + segs * 17 + 10}" y="228" font-size="14">{prog}%</text>')
cols = []
for i, (name, n, sc) in enumerate(tiers):
    x = 560 + i * 150
    b = .6 + i * .2
    cols.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{b:.2f}s" fill="freeze"/>'
                f'{cup(x, 150, sc, n > 0)}'
                f'<text x="{x}" y="222" font-size="30" text-anchor="middle" class="b">{n}</text>'
                f'<text x="{x}" y="248" font-size="12" text-anchor="middle" class="dim" letter-spacing="2">{name}</text></g>')
now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y")
OUT.write_text(frame(left + f'<line x1="500" y1="92" x2="500" y2="{H - 46}" stroke="{G_DARK}"/>' + "".join(cols),
                     f"PLAYSTATION · MAJ {now}"), encoding="utf-8")
print(f"{OUT} : niveau {level} ({prog}%), {total} trophées")
