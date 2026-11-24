"""Dernières transmissions : les 5 dernières activités publiques GitHub, façon messages radio.

Usage : python scripts/transmissions.py <username> <fichier_sortie.svg> [events.json]
Utilise l'API publique https://api.github.com/users/<user>/events/public
(la variable GITHUB_TOKEN est utilisée si elle existe, pour éviter les limites de requêtes).
Lancé automatiquement par .github/workflows/contributions.yml
"""
import json
import os
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

USER, OUT = sys.argv[1], sys.argv[2]
G, G_MID, G_DIM, G_DARK, BG, BEZEL = "#3dff86", "#2fb866", "#1d7a43", "#0c2a17", "#06100a", "#151515"
FONT = "'Courier New', 'DejaVu Sans Mono', Menlo, Consolas, monospace"
MAX_LINES, MAX_CHARS = 5, 58

if len(sys.argv) > 3:
    events = json.load(open(sys.argv[3], encoding="utf-8"))
else:
    headers = {"User-Agent": "transmissions-script", "Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    req = urllib.request.Request(f"https://api.github.com/users/{USER}/events/public?per_page=40", headers=headers)
    events = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))


def short(s, n=MAX_CHARS):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def describe(e):
    t, p = e.get("type"), e.get("payload", {}) or {}
    repo = e.get("repo", {}).get("name", "").split("/")[-1]
    if t == "PushEvent":
        commits = p.get("commits") or []
        if commits:
            return "COMMIT", repo, commits[-1].get("message", "").splitlines()[0]
        n = p.get("size") or p.get("distinct_size")
        ref = (p.get("ref") or "").replace("refs/heads/", "")
        return "COMMIT", repo, f"{n} commit(s) sur {ref}" if n else f"push sur {ref or 'main'}"
    if t == "CreateEvent":
        kind = p.get("ref_type")
        if kind == "repository":
            return "NOUVEAU", repo, "nouveau dépôt créé"
        return "NOUVEAU", repo, f"{'branche' if kind == 'branch' else 'tag'} {p.get('ref', '')}"
    if t == "PullRequestEvent":
        pr = p.get("pull_request", {})
        act = "fusionnée" if p.get("action") == "closed" and pr.get("merged") else {"opened": "ouverte", "closed": "fermée", "reopened": "rouverte"}.get(p.get("action"), p.get("action"))
        return "PR", repo, f"#{pr.get('number', '?')} {act} : {pr.get('title', '')}"
    if t == "IssuesEvent":
        it = p.get("issue", {})
        act = {"opened": "ouverte", "closed": "fermée", "reopened": "rouverte"}.get(p.get("action"), p.get("action"))
        return "ISSUE", repo, f"#{it.get('number', '?')} {act} : {it.get('title', '')}"
    if t == "WatchEvent":
        return "ÉTOILE", repo, "étoile ajoutée"
    if t == "ForkEvent":
        return "FORK", repo, "dépôt forké"
    if t == "ReleaseEvent":
        return "RELEASE", repo, f"version {p.get('release', {}).get('tag_name', '')} publiée"
    if t == "PublicEvent":
        return "PUBLIC", repo, "dépôt rendu public"
    if t == "PullRequestReviewEvent":
        return "REVUE", repo, f"revue de la PR #{p.get('pull_request', {}).get('number', '?')}"
    return None


lines = []
for e in events:
    d = describe(e)
    if not d:
        continue
    when = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Paris"))
    lines.append((when.strftime("%d/%m %H:%M"), *d))
    if len(lines) == MAX_LINES:
        break


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


W = 1200
top, row = 120, 40
H = top + max(len(lines), 1) * row + 50
fs, cw = 16, 16 * 0.6
clips, rows = [], []
t = 0.4
for i, (when, kind, repo, text) in enumerate(lines):
    y = top + i * row
    body = short(f"{repo} · {text}")
    n = len(body)
    vals = ";".join(f"{k * cw:.1f}" for k in range(n + 1))
    kt = ";".join(f"{k / n:.4f}" for k in range(n + 1))
    dur = n * 0.012
    clips.append(f'<clipPath id="t{i}"><rect x="330" y="{y - 18}" height="26" width="0">'
                 f'<animate attributeName="width" begin="{t:.2f}s" dur="{dur:.2f}s" values="{vals}" keyTimes="{kt}" calcMode="discrete" fill="freeze"/></rect></clipPath>')
    rows.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
        f'<path d="M56,{y - 6} l6,-8 l6,14 l6,-12 l6,10 l6,-4" fill="none" stroke="{G}" stroke-width="1.6"/>'
        f'<text x="100" y="{y}" font-size="14" class="dim">{when}</text>'
        f'<rect x="222" y="{y - 16}" width="94" height="22" rx="3" fill="none" stroke="{G_DIM}"/>'
        f'<text x="269" y="{y}" font-size="13" text-anchor="middle" class="b">{esc(kind)}</text></g>'
        f'<text x="330" y="{y}" font-size="{fs}" clip-path="url(#t{i})" xml:space="preserve">{esc(body)}</text>'
    )
    t += dur + 0.25
if not lines:
    rows.append(f'<text x="56" y="{top}" font-size="16" class="dim">Aucune transmission captée pour le moment.</text>')

now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y %H:%M")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <filter id="glow" x="-10%" y="-20%" width="120%" height="140%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <radialGradient id="glass" cx=".5" cy=".5" r=".75"><stop offset="0" stop-color="#0b2414"/><stop offset=".7" stop-color="{BG}"/><stop offset="1" stop-color="#020604"/></radialGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".35"/></pattern>
    <style>text {{ font-family: {FONT}; fill: {G}; }} .dim {{ fill: {G_MID}; }} .b {{ font-weight: 700; }}
      .blink {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0 }} }}</style>
    {"".join(clips)}
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="url(#glass)"/>
  <g filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">DERNIÈRES TRANSMISSIONS</text>
    <circle cx="{W - 280}" cy="52" r="5" fill="{G}" class="blink"/>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">CAPTÉ LE {now}</text>
    <line x1="52" y1="72" x2="{W - 52}" y2="72" stroke="{G_DIM}"/>
    {"".join(rows)}
  </g>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="url(#scan)"/>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="none" stroke="{G_DIM}" stroke-opacity=".5" stroke-width="1.5"/>
</svg>
'''
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(f"{OUT} : {len(lines)} transmission(s)")
