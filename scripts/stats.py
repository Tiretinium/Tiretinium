"""Écran STATISTIQUES : stats générales + activité par mois et par jour de la semaine.

Usage : python scripts/stats.py <username> <fichier_sortie.svg> [contributions.html] [user.json] [repos.json]
Sources : page publique des contributions + API publique GitHub (GITHUB_TOKEN utilisé s'il existe).
Lancé automatiquement par .github/workflows/contributions.yml
"""
import json
import os
import re
import sys
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

USER, OUT = sys.argv[1], sys.argv[2]
G, G_MID, G_DIM, G_DARK, BG, BEZEL = "#3dff86", "#2fb866", "#1d7a43", "#0c2a17", "#06100a", "#151515"
FONT = "'Courier New', 'DejaVu Sans Mono', Menlo, Consolas, monospace"
MOIS = ["JAN", "FÉV", "MAR", "AVR", "MAI", "JUIN", "JUIL", "AOÛT", "SEP", "OCT", "NOV", "DÉC"]
MOIS_LONG = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"]
JOURS_LONG = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def get(url, api=False):
    headers = {"User-Agent": "stats-script"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30).read().decode("utf-8")


args = sys.argv[3:]
html = open(args[0], encoding="utf-8").read() if len(args) > 0 else get(f"https://github.com/users/{USER}/contributions")
user = json.load(open(args[1], encoding="utf-8")) if len(args) > 1 else json.loads(get(f"https://api.github.com/users/{USER}", True))
repos = json.load(open(args[2], encoding="utf-8")) if len(args) > 2 else json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner", True))

# ── contributions par jour (nombre exact via les infobulles, sinon niveau 0-4)
tips = {m.group(1): m.group(2) for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html)}
days = {}
for tag in re.findall(r"<td[^>]*data-date=[^>]*>", html):
    d = re.search(r'data-date="([\d-]+)"', tag)
    lvl = re.search(r'data-level="(\d)"', tag)
    if not (d and lvl):
        continue
    n = int(lvl.group(1))
    tid = re.search(r'id="([^"]+)"', tag)
    if tid and tid.group(1) in tips:
        m = re.match(r"\s*(\d+|No)\s+contribution", tips[tid.group(1)])
        if m:
            n = 0 if m.group(1) == "No" else int(m.group(1))
    days[date.fromisoformat(d.group(1))] = n

m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
total = int(m.group(1).replace(",", "")) if m else sum(days.values())
today = datetime.now(ZoneInfo("Europe/Paris")).date()
active = sum(1 for v in days.values() if v > 0)

cur, d = 0, min(today, max(days) if days else today)
if days.get(d, 0) == 0:
    d -= timedelta(days=1)
while days.get(d, 0) > 0:
    cur += 1
    d -= timedelta(days=1)
best = run = 0
for d in sorted(days):
    run = run + 1 if days[d] > 0 else 0
    best = max(best, run)

by_wd = [0] * 7
for d, v in days.items():
    by_wd[d.weekday()] += v
months = []                                   # 12 derniers mois, du plus ancien au plus récent
y, mo = today.year, today.month
for _ in range(12):
    months.append((y, mo))
    y, mo = (y, mo - 1) if mo > 1 else (y - 1, 12)
months.reverse()
by_month = [sum(v for d, v in days.items() if (d.year, d.month) == ym) for ym in months]

created = datetime.fromisoformat(user.get("created_at", today.isoformat() + "T00:00:00Z").replace("Z", "+00:00")).date()
age = (today - created).days
langs = Counter(r.get("language") for r in repos if r.get("language") and not r.get("fork"))
top_lang = langs.most_common(1)[0][0] if langs else "—"

best_wd = JOURS_LONG[by_wd.index(max(by_wd))] if any(by_wd) else "—"
best_m = MOIS_LONG[months[by_month.index(max(by_month))][1] - 1] if any(by_month) else "—"

ROWS = [
    ("Jours dans les terres désolées", f"{age}"),
    ("Contributions sur 12 mois", f"{total}"),
    ("Jours actifs sur 12 mois", f"{active}"),
    ("Série en cours", f"{cur} j"),
    ("Plus longue série", f"{best} j"),
    ("Jour le plus actif", best_wd),
    ("Mois le plus actif", best_m),
    ("Dépôts publics", f"{user.get('public_repos', len(repos))}"),
    ("Langage principal", top_lang),
]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


W, H = 1200, 520
rows = []
for i, (label, val) in enumerate(ROWS):
    yy = 128 + i * 40
    rows.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{.3 + i * .12:.2f}s" fill="freeze"/>'
        f'<text x="56" y="{yy}" font-size="16">{esc(label)}</text>'
        f'<line x1="{60 + len(label) * 9.6:.0f}" y1="{yy - 4}" x2="{548 - len(str(val)) * 9.6 - 10:.0f}" y2="{yy - 4}" stroke="{G_DIM}" stroke-dasharray="2 5"/>'
        f'<text x="548" y="{yy}" font-size="16" text-anchor="end" class="b">{esc(val)}</text></g>'
    )


def bars(x0, y_base, w, h, values, labels, delay):
    mx = max(values) or 1
    n = len(values)
    step = w / n
    bw = step * .62
    out = []
    for k, (v, lab) in enumerate(zip(values, labels)):
        bh = max(2, h * v / mx)
        x = x0 + k * step + (step - bw) / 2
        b = delay + k * .06
        hl = v == mx and v > 0
        out.append(
            f'<rect x="{x:.1f}" y="{y_base}" width="{bw:.1f}" height="0" fill="{G if hl else G_MID}" opacity="{1 if hl else .85}">'
            f'<animate attributeName="height" from="0" to="{bh:.1f}" begin="{b:.2f}s" dur=".5s" fill="freeze"/>'
            f'<animate attributeName="y" from="{y_base}" to="{y_base - bh:.1f}" begin="{b:.2f}s" dur=".5s" fill="freeze"/></rect>'
            f'<text x="{x + bw / 2:.1f}" y="{y_base + 18}" font-size="11" text-anchor="middle" class="dim">{lab}</text>'
            f'<text x="{x + bw / 2:.1f}" y="{y_base - bh - 6:.1f}" font-size="11" text-anchor="middle" opacity="0">{v}'
            f'<set attributeName="opacity" to="1" begin="{b + .5:.2f}s" fill="freeze"/></text>'
        )
    return "".join(out) + f'<line x1="{x0}" y1="{y_base}" x2="{x0 + w}" y2="{y_base}" stroke="{G_DIM}"/>'


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <filter id="glow" x="-10%" y="-20%" width="120%" height="140%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <radialGradient id="glass" cx=".5" cy=".5" r=".75"><stop offset="0" stop-color="#0b2414"/><stop offset=".7" stop-color="{BG}"/><stop offset="1" stop-color="#020604"/></radialGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".35"/></pattern>
    <style>text {{ font-family: {FONT}; fill: {G}; }} .dim {{ fill: {G_MID}; }} .b {{ font-weight: 700; }}</style>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="url(#glass)"/>
  <g filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">STATISTIQUES</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">MAJ {today.strftime("%d/%m/%Y")}</text>
    <line x1="52" y1="72" x2="{W - 52}" y2="72" stroke="{G_DIM}"/>
    <line x1="590" y1="92" x2="590" y2="{H - 50}" stroke="{G_DARK}"/>
    {"".join(rows)}
    <text x="626" y="104" font-size="13" class="dim" letter-spacing="2">CONTRIBUTIONS PAR MOIS</text>
    {bars(626, 260, 522, 120, by_month, [MOIS[m - 1] for _, m in months], .4)}
    <text x="626" y="318" font-size="13" class="dim" letter-spacing="2">PAR JOUR DE LA SEMAINE</text>
    {bars(626, 450, 522, 100, by_wd, JOURS, 1.2)}
  </g>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="url(#scan)"/>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="none" stroke="{G_DIM}" stroke-opacity=".5" stroke-width="1.5"/>
</svg>
'''
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(f"{OUT} : {total} contributions, {active} jours actifs, série {cur}/{best}, langage {top_lang}")
