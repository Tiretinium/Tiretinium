"""Génère un graphe de contributions GitHub en 2D (fond noir, cases vertes).

Usage : python scripts/contrib_graph.py <username> <fichier_sortie.svg>
Les données viennent de la page publique https://github.com/users/<username>/contributions.
"""
import re
import sys
import urllib.request
from datetime import date

USER = sys.argv[1]
OUT = sys.argv[2]

BG = "#151515"
BORDER = "#2b2b2b"
TEXT = "#9e9e9e"
TITLE = "#e6e6e6"
LEVELS = ["#222222", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]

CELL, GAP = 12, 3
LEFT, TOP = 52, 62

req = urllib.request.Request(
    f"https://github.com/users/{USER}/contributions",
    headers={"User-Agent": "contrib-graph-script"},
)
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

days = {}
for tag in re.findall(r"<td[^>]*data-date=[^>]*>", html):
    d = re.search(r'data-date="([\d-]+)"', tag)
    lvl = re.search(r'data-level="(\d)"', tag)
    if d and lvl:
        days[date.fromisoformat(d.group(1))] = int(lvl.group(1))
if not days:
    sys.exit("Aucune donnée de contribution trouvée")

total = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
total = total.group(1).replace(",", "") if total else "?"

start = min(days)
offset = (start.weekday() + 1) % 7  # la grille commence un dimanche (comme sur GitHub)


def column(d):
    return ((d - start).days + offset) // 7


cells, months = [], []
for d, lvl in sorted(days.items()):
    col, row = column(d), (d.weekday() + 1) % 7
    x, y = LEFT + col * (CELL + GAP), TOP + row * (CELL + GAP)
    cells.append(
        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{LEVELS[lvl]}" '
        f'><title>{d.isoformat()}</title></rect>'
    )
    # étiquette du mois au-dessus de la première semaine qui commence dans ce mois
    if row == 0 and d.day <= 7 and col < column(max(days)) - 1:
        months.append(f'<text x="{x}" y="{TOP - 10}">{MONTHS[d.month - 1]}</text>')

ncols = column(max(days)) + 1
W = LEFT + ncols * (CELL + GAP) + 28
H = TOP + 7 * (CELL + GAP) + 44

legend_x = W - 28 - 5 * (CELL + GAP) - 70
legend = "".join(
    f'<rect x="{legend_x + 40 + i * (CELL + GAP)}" y="{H - 30}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
    for i, c in enumerate(LEVELS)
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    text {{ font-family: 'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif; font-size: 11px; fill: {TEXT}; }}
    .t {{ font-size: 15px; font-weight: 600; fill: {TITLE}; }}
  </style>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <text class="t" x="{LEFT}" y="28">{total} contributions sur les 12 derniers mois</text>
  {"".join(months)}
  <text x="{LEFT - 10}" y="{TOP + 1 * (CELL + GAP) + 10}" text-anchor="end">Lun</text>
  <text x="{LEFT - 10}" y="{TOP + 3 * (CELL + GAP) + 10}" text-anchor="end">Mer</text>
  <text x="{LEFT - 10}" y="{TOP + 5 * (CELL + GAP) + 10}" text-anchor="end">Ven</text>
  <g class="g">{"".join(cells)}</g>
  <text x="{legend_x + 32}" y="{H - 20}" text-anchor="end">Moins</text>
  {legend}
  <text x="{legend_x + 40 + 5 * (CELL + GAP) + 4}" y="{H - 20}">Plus</text>
</svg>
'''

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(f"{OUT} : {len(days)} jours, {total} contributions")
