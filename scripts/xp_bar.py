"""Barre d'XP de l'habitant, calculée à partir des contributions GitHub.

Usage : python scripts/xp_bar.py <username> <fichier_sortie.svg> [page_contributions.html]
- 1 contribution = 10 XP
- Passer du niveau n au niveau n+1 coûte 100 * n XP (niveau 1 au départ)
Lancé automatiquement par .github/workflows/contributions.yml
"""
import re
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

USER, OUT = sys.argv[1], sys.argv[2]
G, G_MID, G_DIM, G_DARK, BG, BEZEL = "#3dff86", "#2fb866", "#1d7a43", "#0c2a17", "#06100a", "#151515"
FONT = "'Courier New', 'DejaVu Sans Mono', Menlo, Consolas, monospace"
XP_PER_CONTRIB = 10

if len(sys.argv) > 3:
    html = open(sys.argv[3], encoding="utf-8").read()
else:
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"User-Agent": "xp-bar-script"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
contribs = int(m.group(1).replace(",", "")) if m else 0
xp = contribs * XP_PER_CONTRIB

level, need = 1, 100
rest = xp
while rest >= need:
    rest -= need
    level += 1
    need = 100 * level
ratio = rest / need

now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y %H:%M")
W, H = 1200, 96
bx, bw, segs = 230, 500, 25
sw = bw / segs
filled = round(ratio * segs)
bars = "".join(
    f'<rect x="{bx + k * sw + 1:.1f}" y="40" width="{sw - 4:.1f}" height="18" '
    f'fill="{G if k < filled else "none"}" stroke="{G_DIM}" opacity="{1 if k < filled else .7}">'
    + (f'<animate attributeName="opacity" values="0;1" dur=".05s" begin="{.3 + k * .04:.2f}s" fill="freeze"/>' if k < filled else "")
    + '</rect>'
    for k in range(segs)
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <filter id="glow" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".35"/></pattern>
    <style>text {{ font-family: {FONT}; fill: {G}; }} .dim {{ fill: {G_MID}; }} .b {{ font-weight: 700; }}</style>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  <rect x="14" y="12" width="{W - 28}" height="{H - 24}" rx="14" fill="{BG}" stroke="{G_DIM}" stroke-opacity=".6"/>
  <g filter="url(#glow)">
    <text x="48" y="58" font-size="26" class="b">NIV. {level}</text>
    {bars}
    <text x="{bx + bw + 24}" y="56" font-size="16">XP {rest}/{need}</text>
    <text x="{W - 48}" y="44" font-size="12" text-anchor="end" class="dim" letter-spacing="2">{contribs} CONTRIBUTIONS · 12 MOIS</text>
    <text x="{W - 48}" y="66" font-size="12" text-anchor="end" class="dim" letter-spacing="2">SYNCHRO {now}</text>
  </g>
  <rect x="14" y="12" width="{W - 28}" height="{H - 24}" rx="14" fill="url(#scan)"/>
</svg>
'''
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(f"{OUT} : {contribs} contributions, {xp} XP, niveau {level} ({rest}/{need})")
