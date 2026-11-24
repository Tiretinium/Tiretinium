"""Météo des terres désolées : la vraie météo de Nice, mise en scène façon terminal d'abri.

Usage : python scripts/weather.py <fichier_sortie.svg> [meteo.json]
Source : API Open-Meteo (gratuite, sans clé) — https://open-meteo.com
Lancé automatiquement par .github/workflows/contributions.yml
"""
import json
import math
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

OUT = Path(sys.argv[1])
LAT, LON = 43.70, 7.27          # Nice (Abri 27)
G, G_MID, G_DIM, G_DARK, BG, BEZEL = "#3dff86", "#2fb866", "#1d7a43", "#0c2a17", "#06100a", "#151515"
FONT = "'Courier New', 'DejaVu Sans Mono', Menlo, Consolas, monospace"
URL = (f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
       "&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day"
       "&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=Europe%2FParis&forecast_days=4")

if len(sys.argv) > 2:
    data = json.load(open(sys.argv[2], encoding="utf-8"))
else:
    try:
        data = json.loads(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "weather-script"}), timeout=30).read())
    except Exception as e:
        print(f"Météo indisponible ({e}) : écran précédent conservé")
        if not OUT.exists():
            OUT.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="200" viewBox="0 0 1200 200">
  <rect width="1200" height="200" rx="16" fill="{BEZEL}"/><rect x="20" y="20" width="1160" height="160" rx="22" fill="{BG}" stroke="{G_DIM}"/>
  <style>text {{ font-family: {FONT}; fill: {G}; }}</style>
  <text x="52" y="58" font-size="22" font-weight="700" letter-spacing="3">MÉTÉO DES TERRES DÉSOLÉES</text>
  <text x="56" y="120" font-size="17">EN ATTENTE DU SIGNAL MÉTÉO_</text>
</svg>
''', encoding="utf-8")
        sys.exit(0)

# code météo WMO -> (description réelle, version terres désolées, icône, niveau de radiation 0-4)
def describe(code):
    if code == 0:
        return "Ciel dégagé", "Ciel dégagé · radiations faibles", "sun", 1
    if code in (1, 2):
        return "Éclaircies", "Éclaircies · retombées légères", "partly", 1
    if code == 3:
        return "Couvert", "Ciel de cendres", "cloud", 2
    if code in (45, 48):
        return "Brouillard", "Brume toxique", "fog", 2
    if code in (51, 53, 55, 56, 57):
        return "Bruine", "Bruine acide", "rain", 2
    if code in (61, 63, 80, 81):
        return "Pluie", "Pluie radioactive", "rain", 3
    if code in (65, 66, 67, 82):
        return "Forte pluie", "Tempête radioactive", "rain", 4
    if code in (71, 73, 75, 77, 85, 86):
        return "Neige", "Neige nucléaire", "snow", 3
    if code in (95, 96, 99):
        return "Orage", "Orage radioactif", "storm", 4
    return "Inconnu", "Signal météo brouillé", "cloud", 2


RAD = ["NULLES", "FAIBLES", "MODÉRÉES", "ÉLEVÉES", "CRITIQUES"]
JOURS = ["LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"]


def icon(kind, cx, cy, s=1.0, anim=True):
    stk = f'stroke="{G}" stroke-width="{2.4 / s:.2f}" stroke-linecap="round" stroke-linejoin="round"'
    st = f'fill="none" {stk}'
    cloud = (f'<path d="M-30,14 Q-44,14 -44,0 Q-44,-14 -28,-14 Q-24,-32 -4,-32 Q14,-32 20,-16 Q38,-18 40,0 Q40,14 26,14 Z" '
             f'fill="{G_DARK}" {stk}/>')
    spin = f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="18s" repeatCount="indefinite"/>' if anim else ""
    sun = (f'<g><circle r="16" fill="{G_DARK}" {stk}/><g {st}>' +
           "".join(f'<line x1="{24 * math.cos(a):.1f}" y1="{24 * math.sin(a):.1f}" x2="{32 * math.cos(a):.1f}" y2="{32 * math.sin(a):.1f}"/>'
                   for a in [k * math.pi / 4 for k in range(8)]) + f'</g>{spin}</g>')
    drops = "".join(
        f'<line x1="{x}" y1="22" x2="{x - 5}" y2="34" stroke="{G}" stroke-width="2.2" stroke-linecap="round">'
        + (f'<animate attributeName="opacity" values="1;0;1" dur="1s" begin="{k * .25:.2f}s" repeatCount="indefinite"/>' if anim else "")
        + '</line>' for k, x in enumerate([-22, -8, 6, 20]))
    flakes = "".join(f'<text x="{x}" y="36" font-size="14" text-anchor="middle">*</text>' for x in [-20, 0, 20])
    bolt = f'<path d="M-2,16 L-10,32 L0,30 L-6,46 L10,26 L0,28 L6,16 Z" fill="{G}"/>'
    fog = "".join(f'<line x1="-40" y1="{y}" x2="36" y2="{y}" {st}/>' for y in (22, 30))
    body = {
        "sun": sun,
        "partly": f'<g transform="translate(14 -12) scale(.8)">{sun}</g>{cloud}',
        "cloud": cloud,
        "fog": cloud + fog,
        "rain": cloud + drops,
        "snow": cloud + flakes,
        "storm": cloud + bolt,
    }[kind]
    return f'<g transform="translate({cx} {cy}) scale({s})">{body}</g>'


cur = data["current"]
real, wasteland, kind, rad = describe(int(cur["weather_code"]))
temp, feel = round(cur["temperature_2m"]), round(cur["apparent_temperature"])
hum, wind = round(cur["relative_humidity_2m"]), round(cur["wind_speed_10m"])
if wind >= 50:
    rad = min(4, rad + 1)

W, H = 1200, 330
rad_bar = "".join(
    f'<rect x="{560 + k * 44}" y="218" width="38" height="14" fill="{G if k <= rad else "none"}" stroke="{G_DIM}"/>' for k in range(5))
days = []
d = data["daily"]
for i in range(1, min(4, len(d["time"]))):
    x = 920 + (i - 1) * 100
    day = datetime.fromisoformat(d["time"][i])
    _, _, k, _ = describe(int(d["weather_code"][i]))
    days.append(f'<text x="{x}" y="112" font-size="13" text-anchor="middle" class="dim" letter-spacing="2">{JOURS[day.weekday()]}</text>'
                f'{icon(k, x, 158, .62, anim=False)}'
                f'<text x="{x}" y="216" font-size="15" text-anchor="middle">{round(d["temperature_2m_max"][i])}°</text>'
                f'<text x="{x}" y="236" font-size="13" text-anchor="middle" class="dim">{round(d["temperature_2m_min"][i])}°</text>')

now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m %H:%M")
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
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">MÉTÉO DES TERRES DÉSOLÉES</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">ABRI 27 · RELEVÉ {now}</text>
    <line x1="52" y1="72" x2="{W - 52}" y2="72" stroke="{G_DIM}"/>
    {icon(kind, 150, 170, 1.7)}
    <text x="300" y="168" font-size="64" class="b">{temp}°</text>
    <text x="300" y="200" font-size="14" class="dim">ressenti {feel}°</text>
    <text x="560" y="118" font-size="22" class="b">{wasteland.upper()}</text>
    <text x="560" y="146" font-size="14" class="dim">Relevé réel : {real.lower()}</text>
    <text x="560" y="168" font-size="14" class="dim">Vent {wind} km/h · humidité {hum} %</text>
    <text x="560" y="206" font-size="13" class="dim" letter-spacing="2">RADIATIONS {RAD[rad]}</text>
    {rad_bar}
    <line x1="860" y1="92" x2="860" y2="{H - 46}" stroke="{G_DARK}"/>
    {"".join(days)}
    <text x="56" y="{H - 44}" font-size="11" class="dim">Données : Open-Meteo</text>
  </g>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="url(#scan)"/>
  <rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22" fill="none" stroke="{G_DIM}" stroke-opacity=".5" stroke-width="1.5"/>
</svg>
'''
OUT.write_text(svg, encoding="utf-8")
print(f"{OUT} : {temp}°C, {real} -> {wasteland}, radiations {RAD[rad]}")
