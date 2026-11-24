"""Génère les SVG animés du profil (thème terminal rétro / Fallout).

Usage : python scripts/vault_assets.py
Écrit dans assets/ : terminal.svg, special.svg, inventory.svg, quests.svg, holotapes.svg, map.svg, radio.svg, tab-*.svg
Modifie les textes / valeurs dans la section CONFIG puis relance le script.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

# ───────────────────────── CONFIG ─────────────────────────
G = "#3dff86"        # vert phosphore
G_DIM = "#1d7a43"
G_MID = "#2fb866"     # texte secondaire lisible
G_DARK = "#0c2a17"
BG = "#06100a"
BEZEL = "#151515"
FONT = "'Courier New', 'DejaVu Sans Mono', Menlo, Consolas, monospace"

TERMINAL_LINES = [
    # (texte, style, vitesse en s/caractère, pause après)
    ("TIRETINIUM INDUSTRIES · TERMINAL SÉCURISÉ", "b", 0.012, 0.35),
    ("ENTREZ LE MOT DE PASSE", "", 0.012, 0.2),
    ("> ********", "", 0.08, 0.3),
    ("ACCÈS AUTORISÉ. BIENVENUE, HABITANT DE L'ABRI 27.", "b", 0.012, 0.5),
    ("", "", 0, 0.1),
    ("> HABITANT ... Tiretinium", "", 0.012, 0.15),
    ("> CLASSE ..... BUT Informatique, 3e année", "", 0.012, 0.15),
    ("> AFFECTÉ .... Alternant chez Thales DMS", "", 0.012, 0.15),
    ("> SECTEUR .... Sophia Antipolis, Côte d'Azur", "", 0.012, 0.15),
    ("> MISSION .... Coder. Apprendre. Survivre.", "", 0.012, 0.0),
]

# Séquence de démarrage affichée avant le terminal : (texte, style)  style "b" = gras, "dim" = atténué
BOOT_LINES = [
    ("TIRET-OS BIOS v3.0 · TIRETINIUM INDUSTRIES", "b"),
    ("Test mémoire ........................ 65536 Ko  OK", ""),
    ("Détection du processeur ............. OK", ""),
    ("Montage du disque ABRI-27 ........... OK", ""),
    ("Synchronisation GitHub .............. OK", ""),
    ("Chargement du profil : Tiretinium", ""),
    ("  > S.P.E.C.I.A.L. · inventaire · quêtes · carte", "dim"),
    ("", ""),
    ("DÉMARRAGE DU TERMINAL...", "b"),
]
BOOT_STEP = 0.28      # secondes entre deux lignes

# S.P.E.C.I.A.L. : (lettre, nom, valeur /10)
SPECIAL = [
    ("S", "FORCE", 6),
    ("P", "PERCEPTION", 7),
    ("E", "ENDURANCE", 8),
    ("C", "CHARISME", 6),
    ("I", "INTELLIGENCE", 9),
    ("A", "AGILITÉ", 7),
    ("L", "CHANCE", 5),
]

# Inventaire style Fallout 4 : (objet, type, maîtrise /10, poids, valeur, équipé ?)
INVENTORY = [
    ("Java", "Langage", 8, 4, 320, True),
    ("Spring Boot", "Framework", 7, 6, 280, True),
    ("Python", "Langage", 7, 2, 250, True),
    ("C#", "Langage", 6, 4, 210, False),
    ("TypeScript", "Langage", 6, 3, 200, True),
    ("React", "Framework", 6, 5, 190, False),
    ("PostgreSQL", "Base de données", 7, 5, 230, True),
    ("Docker", "DevOps", 6, 7, 240, True),
    ("Kubernetes", "DevOps", 4, 9, 300, False),
    ("Git", "Outil", 8, 1, 150, True),
    ("Linux", "Système", 7, 3, 180, True),
    ("IntelliJ IDEA", "Outil", 8, 2, 120, True),
]

# Équipement porté par le personnage : (emplacement, objet, point sur le perso x,y)
APPAREL = [
    ("TÊTE", "Casque anti-bruit", (64, 62)),
    ("ARME", "Carabine de chasse à lunette", (6, 162)),
    ("TORSE", "Sweat de l'Abri 27", (40, 184)),
    ("JAMBES", "Cargo multipoches", (25, 270)),
    ("PIEDS", "Bottes tout-terrain", (44, 336)),
]

# Journal de quêtes : (titre, type, [(objectif, terminé ?)])
QUESTS = [
    ("Diplôme de l'Abri", "PRINCIPALE", [
        ("Entrer en BUT Informatique à l'IUT Nice Côte d'Azur", True),
        ("Valider la 1re année", True),
        ("Valider la 2e année", True),
        ("Réussir la 3e année", False),
        ("Obtenir le BUT Informatique (2027)", False),
    ]),
    ("Contrat chez Thales DMS", "PRINCIPALE", [
        ("Décrocher une alternance", True),
        ("Rejoindre l'équipe chez Thales DMS", True),
        ("Livrer des projets en entreprise", False),
        ("Terminer l'alternance", False),
    ]),
    ("Le terminal de l'habitant", "ANNEXE", [
        ("Créer le profil GitHub", True),
        ("Installer le terminal de l'Abri 27", True),
        ("Archiver mes projets sur holotapes", True),
    ]),
    ("Explorer les Terres désolées", "ANNEXE", [
        ("Maîtriser Docker", True),
        ("Déployer sur Kubernetes", False),
        ("Choisir la suite après le BUT", False),
    ]),
]

# Holotapes = projets : (nom, description, technos, lien) ; None = emplacement vide
HOLOTAPES = [
    ("Scubanion", "Animal virtuel boosté par tes pas", "Nuxt · Laravel · ESP32 · MariaDB", "github.com/Scubatana/scubanion"),
    ("ENIV", "ENT léger : devoirs partagés", "Node.js · Express · MariaDB · PWA", "github.com/ENIV-ENT/ENIV"),
    ("Tiretinium", "Profil GitHub façon terminal d'abri", "Python · SVG · GitHub Actions", "github.com/Tiretinium/Tiretinium"),
]

# Carte : (titre, sous-titre, longitude, latitude, type, décalage étiquette (dx, dy, ancre))
# types : home (ton abri), vault (abri), rad (abri irradié), ruin (ruines), crater, iut, work
# Numéros d'abri = chiffres du code postal (06400 -> Abri 40, 98000 -> Abri 98) ; l'Abri 27 est à 06000
MAP_PLACES = [
    ("ABRI 27", "06000 · CAPITALE", 7.262, 43.703, "vault", (-16, -16, "end")),
    ("ABRI 40", "06400 · SCELLÉ", 7.013, 43.553, "vault", (-14, -16, "end")),
    ("ABRI 60", "06600 · OUVERT", 7.125, 43.580, "vault", (44, 8, "start")),
    ("ABRI 13", "06130 · IRRADIÉ", 6.924, 43.659, "rad", (16, -16, "start")),
    ("ABRI 56", "06560 · RUINES", 7.009, 43.641, "ruin", (-16, -18, "end")),
    ("ABRI 14", "06140 · OUVERT", 7.112, 43.722, "vault", (-16, -14, "end")),
    ("ABRI 80", "06800 · COLONIE", 7.149, 43.664, "vault", (-16, -16, "end")),
    ("ABRI 51", "06510 · ZONE IRRADIÉE", 7.187, 43.789, "rad", (16, -4, "start")),
    ("ABRI 98", "98000 · FORTERESSE", 7.425, 43.738, "vault", (14, 62, "start")),
    ("ABRI 50", "06500 · SCELLÉ", 7.498, 43.775, "vault", (-6, 84, "middle")),
    ("CRATÈRE", "ZONE D'IMPACT", 7.216, 43.658, "crater", (22, 26, "start")),
    ("IUT NICE CÔTE D'AZUR", "CAMPUS SOPHIATECH", 7.0714, 43.6156, "iut", (16, 26, "start")),
    ("THALES DMS", "SOPHIA ANTIPOLIS", 7.047, 43.621, "work", (-16, -18, "end")),
]

# Stations radio (affichage seulement, les liens cliquables sont sous l'image)
RADIO_STATIONS = [
    "RADIO ABRI 27",
    "EMAIL · Thomasbanderas06@gmail.com",
    "DISCORD · canal ouvert",
    "TIKTOK · @tiretnium2703",
    "SIGNAL INCONNU",
]

TABS = ["STAT", "INV", "DATA", "MAP", "RADIO"]
# ──────────────────────────────────────────────────────────


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def crt_defs(w, h):
    """Dégradés, scanlines et animations communs aux écrans."""
    return f'''
    <radialGradient id="glass" cx=".5" cy=".5" r=".75">
      <stop offset="0" stop-color="#0b2414"/><stop offset=".7" stop-color="{BG}"/><stop offset="1" stop-color="#020604"/>
    </radialGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="#000" opacity=".35"/>
    </pattern>
    <linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".5" stop-color="{G}" stop-opacity=".07"/><stop offset="1" stop-color="{G}" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      text {{ font-family: {FONT}; fill: {G}; }}
      .dim {{ fill: {G_MID}; }}
      .b {{ font-weight: 700; }}
      .flick {{ animation: flick 6s infinite; }}
      @keyframes flick {{ 0%,100% {{opacity:1}} 47% {{opacity:1}} 48% {{opacity:.82}} 49% {{opacity:1}} 72% {{opacity:.93}} 73% {{opacity:1}} }}
      .roll {{ animation: roll 5s linear infinite; }}
      @keyframes roll {{ from {{ transform: translateY(-120px) }} to {{ transform: translateY({h}px) }} }}
      .blink {{ animation: blink 1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0 }} }}
    </style>'''


def screen(x, y, w, h, rx=26):
    return f'''
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#glass)"/>'''


def screen_overlay(x, y, w, h, rx=26):
    return f'''
  <g clip-path="url(#scr)" pointer-events="none">
    <rect class="roll" x="{x}" y="0" width="{w}" height="120" fill="url(#band)"/>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#scan)"/>
  </g>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{G_DIM}" stroke-opacity=".5" stroke-width="1.5"/>'''


def gear(cx, cy, r_out, r_in, teeth):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        r = r_out if i % 4 in (1, 2) else r_in
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


# ───────────────────────── terminal.svg ─────────────────────────
def terminal():
    W, H = 1200, 400
    fs, lh, x0, y0 = 19, 29, 72, 82
    cw = fs * 0.6
    # ── séquence de démarrage : trait CRT puis lignes de diagnostic
    b0 = 1.0
    boot_end = b0 + BOOT_STEP * len(BOOT_LINES) + 0.7
    boot_lines = "".join(
        f'<text x="64" y="{78 + i * 30}" font-size="18"{" class=\"b\"" if st == "b" else (" class=\"dim\"" if st == "dim" else "")} opacity="0" xml:space="preserve">'
        f'{esc(txt)}<set attributeName="opacity" to="1" begin="{b0 + i * BOOT_STEP:.2f}s" fill="freeze"/></text>'
        for i, (txt, st) in enumerate(BOOT_LINES)
    )
    boot = f'''<g>
      <rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="#020604"/>
      <rect x="{W / 2}" y="{H / 2 - 1}" width="0" height="2" fill="#d9ffe6">
        <animate attributeName="x" from="{W / 2}" to="20" dur=".45s" fill="freeze"/>
        <animate attributeName="width" from="0" to="{W - 40}" dur=".45s" fill="freeze"/>
        <animate attributeName="y" from="{H / 2 - 1}" to="20" begin=".45s" dur=".4s" fill="freeze"/>
        <animate attributeName="height" from="2" to="{H - 40}" begin=".45s" dur=".4s" fill="freeze"/>
        <animate attributeName="opacity" from="1" to="0" begin=".45s" dur=".45s" fill="freeze"/>
      </rect>
      <g filter="url(#glow)">{boot_lines}</g>
      <set attributeName="opacity" to="0" begin="{boot_end:.2f}s" fill="freeze"/>
    </g>'''
    t = boot_end + 0.4
    lines_svg, defs_clip = [], []
    for i, (txt, style, speed, pause) in enumerate(TERMINAL_LINES):
        y = y0 + i * lh
        n = len(txt)
        if n:
            vals = ";".join(f"{k * cw:.1f}" for k in range(n + 1))
            kt = ";".join(f"{k / n:.4f}" for k in range(n + 1))
            dur = max(n * speed, 0.05)
            defs_clip.append(
                f'<clipPath id="l{i}"><rect x="{x0 - 2}" y="{y - fs}" height="{lh}" width="0">'
                f'<animate attributeName="width" begin="{t:.2f}s" dur="{dur:.2f}s" values="{vals}" keyTimes="{kt}" '
                f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
            )
            cls = ' class="b"' if style == "b" else ""
            lines_svg.append(f'<text x="{x0}" y="{y}" font-size="{fs}"{cls} clip-path="url(#l{i})" xml:space="preserve">{esc(txt)}</text>')
            t += dur
        t += pause
    # curseur clignotant après la dernière ligne
    last = TERMINAL_LINES[-1][0]
    cy = y0 + (len(TERMINAL_LINES) - 1) * lh
    cursor = (f'<g class="blink"><rect x="{x0 + len(last) * cw + 6:.1f}" y="{cy - fs + 3}" width="{cw:.1f}" height="{fs}" fill="{G}" opacity="0">'
              f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></rect></g>')

    gx, gy = 985, 196
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{crt_defs(W, H)}
    <clipPath id="scr"><rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="26"/></clipPath>
    {"".join(defs_clip)}
  </defs>
  <rect width="{W}" height="{H}" rx="18" fill="{BEZEL}"/>
  {screen(20, 20, W - 40, H - 40)}
  <g class="flick" filter="url(#glow)" opacity="0">
    <animate attributeName="opacity" values="0;1.6;1" dur=".35s" begin="{boot_end:.2f}s" fill="freeze"/>
    <text x="{W - 52}" y="52" font-size="13" text-anchor="end" class="dim">TIRET-OS v3.0  //  ABRI 27</text>
    {"".join(lines_svg)}
    {cursor}

    <!-- porte d'abri : engrenage qui tourne -->
    <g opacity=".95">
      <circle cx="{gx}" cy="{gy}" r="132" fill="none" stroke="{G_DIM}" stroke-width="1" stroke-dasharray="3 9">
        <animateTransform attributeName="transform" type="rotate" from="360 {gx} {gy}" to="0 {gx} {gy}" dur="40s" repeatCount="indefinite"/>
      </circle>
      <path d="{gear(gx, gy, 118, 104, 14)}" fill="{G_DARK}" stroke="{G}" stroke-width="2">
        <animateTransform attributeName="transform" type="rotate" from="0 {gx} {gy}" to="360 {gx} {gy}" dur="24s" repeatCount="indefinite"/>
      </path>
      <circle cx="{gx}" cy="{gy}" r="88" fill="{BG}" stroke="{G}" stroke-width="1.5"/>
      <circle cx="{gx}" cy="{gy}" r="78" fill="none" stroke="{G_DIM}" stroke-width="1"/>
      <text x="{gx}" y="{gy + 6}" font-size="64" text-anchor="middle" dominant-baseline="middle" class="b">27</text>
      <text x="{gx}" y="{gy + 152}" font-size="14" text-anchor="middle" class="dim" letter-spacing="6">ABRI 27</text>
    </g>
  </g>
  <g clip-path="url(#scr)">{boot}</g>
  {screen_overlay(20, 20, W - 40, H - 40)}
</svg>
'''
    (OUT / "terminal.svg").write_text(svg, encoding="utf-8")


# ───────────────────────── special.svg ─────────────────────────
def special():
    W = 1200
    row_h, top = 50, 112
    H = top + len(SPECIAL) * row_h + 34
    rows = []
    t0 = 0.4
    for i, (letter, name, val) in enumerate(SPECIAL):
        y = top + i * row_h
        segs = []
        for k in range(10):
            sx = 400 + k * 66
            on = k < val
            if on:
                b = t0 + i * 0.25 + k * 0.07
                segs.append(f'<rect x="{sx}" y="{y - 18}" width="58" height="22" rx="2" fill="{G_DARK}" stroke="{G_DIM}">'
                            f'<set attributeName="fill" to="{G}" begin="{b:.2f}s" fill="freeze"/></rect>')
            else:
                segs.append(f'<rect x="{sx}" y="{y - 18}" width="58" height="22" rx="2" fill="none" stroke="{G_DARK}"/>')
        num_b = t0 + i * 0.25 + val * 0.07
        rows.append(f'''
    <g>
      <rect x="52" y="{y - 28}" width="40" height="40" rx="4" fill="none" stroke="{G}" stroke-width="1.5"/>
      <text x="72" y="{y}" font-size="26" text-anchor="middle" class="b">{letter}</text>
      <text x="112" y="{y - 1}" font-size="20" class="b">{esc(name)}</text>
      {"".join(segs)}
      <text x="1130" y="{y}" font-size="22" text-anchor="end" class="b" opacity="0">{val:02d}<set attributeName="opacity" to="1" begin="{num_b:.2f}s" fill="freeze"/></text>
    </g>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{crt_defs(W, H)}
    <clipPath id="scr"><rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22"/></clipPath>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  {screen(20, 20, W - 40, H - 40, 22)}
  <g class="flick" filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">S.P.E.C.I.A.L.</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">ABRI 27</text>
    <line x1="52" y1="70" x2="{W - 52}" y2="70" stroke="{G_DIM}"/>
    {"".join(rows)}
  </g>
  {screen_overlay(20, 20, W - 40, H - 40, 22)}
</svg>
'''
    (OUT / "special.svg").write_text(svg, encoding="utf-8")


# ───────────────────────── tab-*.svg ─────────────────────────
def tabs():
    W, H = 1200, 64
    step = (W - 120) / len(TABS)
    for active in TABS:
        parts = []
        ax = 0
        for j, name in enumerate(TABS):
            cx = 60 + step * (j + 0.5)
            if name == active:
                ax = cx
                parts.append(f'<text x="{cx}" y="30" font-size="22" text-anchor="middle" class="b" letter-spacing="3">{name}</text>')
            else:
                parts.append(f'<text x="{cx}" y="30" font-size="18" text-anchor="middle" class="dim" letter-spacing="3">{name}</text>')
        half = 78
        # ligne Pip-Boy : un trait avec une "encoche" autour de l'onglet actif
        line = (f'<path d="M24,48 L{ax - half},48 L{ax - half},8 L{ax + half},8 L{ax + half},48 L{W - 24},48" '
                f'fill="none" stroke="{G}" stroke-width="2"/>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <style>text {{ font-family: {FONT}; fill: {G}; }} .dim {{ fill: {G_DIM}; }} .b {{ font-weight: 700; }}</style>
  </defs>
  <g filter="url(#glow)">{line}{"".join(parts)}</g>
</svg>
'''
        (OUT / f"tab-{active.lower()}.svg").write_text(svg, encoding="utf-8")


# ───────────────────────── quests.svg ─────────────────────────
def quests():
    W, H = 1200, 430
    N = len(QUESTS)
    T = 4.0
    cyc, pct = N * T, 100 / N
    rows, sel, details = [], [], []
    for i, (title, kind, objs) in enumerate(QUESTS):
        y = 140 + i * 40
        done = all(d for _, d in objs)
        rows.append(f'<text x="64" y="{y}" font-size="18">{esc(title)}</text>'
                    f'<text x="470" y="{y}" font-size="12" text-anchor="end" class="dim" letter-spacing="2">{kind}</text>')
        delay = f"animation-delay:{i * T:.1f}s"
        sel.append(f'<g class="sel" style="{delay}"><rect x="52" y="{y - 24}" width="430" height="34" fill="{G}"/>'
                   f'<text x="64" y="{y}" font-size="18" class="b" style="fill:{BG}">{esc(title)}</text>'
                   f'<text x="470" y="{y}" font-size="12" text-anchor="end" style="fill:{BG}" letter-spacing="2">{kind}</text></g>')
        lines = []
        for k, (obj, ok) in enumerate(objs):
            oy = 176 + k * 38
            box = (f'<rect x="560" y="{oy - 15}" width="16" height="16" fill="{G if ok else "none"}" stroke="{G}"/>'
                   + (f'<path d="M563,{oy - 7} l4,4 l7,-8" stroke="{BG}" stroke-width="2.4" fill="none"/>' if ok else ""))
            style = ' class="dim"' if ok else ""
            lines.append(f'{box}<text x="592" y="{oy}" font-size="17"{style}>{esc(obj)}</text>')
        n_ok = sum(d for _, d in objs)
        details.append(f'''<g class="sel" style="{delay}">
        <text x="560" y="128" font-size="21" class="b">{esc(title.upper())}</text>
        <text x="1148" y="128" font-size="14" text-anchor="end" class="dim">{n_ok}/{len(objs)} OBJECTIFS</text>
        {"".join(lines)}</g>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{crt_defs(W, H)}
    <clipPath id="scr"><rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22"/></clipPath>
    <style>
      .sel {{ opacity: 0; animation: sel {cyc:.1f}s step-end infinite; }}
      @keyframes sel {{ 0% {{ opacity: 1 }} {pct:.3f}% {{ opacity: 0 }} 100% {{ opacity: 0 }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  {screen(20, 20, W - 40, H - 40, 22)}
  <g class="flick" filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">QUÊTES</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">JOURNAL DE L'HABITANT</text>
    <line x1="52" y1="70" x2="{W - 52}" y2="70" stroke="{G_DIM}"/>
    <line x1="520" y1="96" x2="520" y2="{H - 50}" stroke="{G_DARK}"/>
    {"".join(rows)}
    {"".join(sel)}
    {"".join(details)}
  </g>
  {screen_overlay(20, 20, W - 40, H - 40, 22)}
</svg>
'''
    (OUT / "quests.svg").write_text(svg, encoding="utf-8")


# ───────────────────────── holotapes.svg ─────────────────────────
def holotapes():
    W, H = 1200, 420
    cards = []
    n = len(HOLOTAPES)
    cw, gap = 340, 22
    x0 = (W - (n * cw + (n - 1) * gap)) / 2
    for i, tape in enumerate(HOLOTAPES):
        x = x0 + i * (cw + gap)
        y = 96
        empty = tape is None
        name, desc, tech, link = tape if tape else ("HOLOTAPE VIERGE", "Emplacement libre", "Projet à venir", "")
        op = ' opacity=".45"' if empty else ""
        reel = lambda cx: (f'<g><circle cx="{cx}" cy="{y + 104}" r="22" fill="{BG}" stroke="{G}" stroke-width="2"/>'
                           f'<circle cx="{cx}" cy="{y + 104}" r="7" fill="none" stroke="{G}" stroke-width="1.5"/>'
                           + "".join(f'<line x1="{cx}" y1="{y + 104}" x2="{cx + 17 * math.cos(a):.1f}" y2="{y + 104 + 17 * math.sin(a):.1f}" stroke="{G}" stroke-width="1.5"/>'
                                     for a in (0, 2.094, 4.189))
                           + ("" if empty else f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {y + 104}" to="360 {cx} {y + 104}" dur="3s" repeatCount="indefinite"/>')
                           + '</g>')
        cards.append(f'''<g{op}>
      <path d="M{x},{y + 14} Q{x},{y} {x + 14},{y} L{x + cw - 14},{y} Q{x + cw},{y} {x + cw},{y + 14} L{x + cw},{y + 178} L{x + cw - 24},{y + 200} L{x + 24},{y + 200} L{x},{y + 178} Z"
            fill="{G_DARK}" stroke="{G}" stroke-width="2"/>
      <rect x="{x + 20}" y="{y + 16}" width="{cw - 40}" height="40" rx="3" fill="{BG}" stroke="{G_DIM}"/>
      <text x="{x + cw / 2}" y="{y + 43}" font-size="18" text-anchor="middle" class="b">{esc(name)}</text>
      <rect x="{x + 60}" y="{y + 76}" width="{cw - 120}" height="56" rx="28" fill="none" stroke="{G_DIM}" stroke-width="1.5"/>
      {reel(x + 98)}{reel(x + cw - 98)}
      <rect x="{x + 70}" y="{y + 156}" width="{cw - 140}" height="24" rx="4" fill="none" stroke="{G_DIM}"/>
      <text x="{x + cw / 2}" y="{y + 173}" font-size="12" text-anchor="middle" class="dim" letter-spacing="2">HOLOTAPE {i + 1:02d}</text>
      <text x="{x + cw / 2}" y="{y + 236}" font-size="15" text-anchor="middle">{esc(desc)}</text>
      <text x="{x + cw / 2}" y="{y + 262}" font-size="13" text-anchor="middle" class="dim">{esc(tech)}</text>
      <text x="{x + cw / 2}" y="{y + 284}" font-size="12" text-anchor="middle" class="dim">{esc(link)}</text>
    </g>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{crt_defs(W, H)}
    <clipPath id="scr"><rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22"/></clipPath>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  {screen(20, 20, W - 40, H - 40, 22)}
  <g class="flick" filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">HOLOTAPES</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">PROJETS ARCHIVÉS</text>
    <line x1="52" y1="70" x2="{W - 52}" y2="70" stroke="{G_DIM}"/>
    {"".join(cards)}
  </g>
  {screen_overlay(20, 20, W - 40, H - 40, 22)}
</svg>
'''
    (OUT / "holotapes.svg").write_text(svg, encoding="utf-8")


# ───────────────────────── map.svg ─────────────────────────
def map_svg():
    import json
    data = json.loads((Path(__file__).resolve().parent / "data" / "cote_azur.json").read_text(encoding="utf-8"))
    L, Bm, R, Tm = 6.86, 43.50, 7.56, 43.81
    X0, Y0, X1 = 40, 80, 1160
    kx = (X1 - X0) / ((R - L) * math.cos(math.radians(43.65)))
    Y1 = Y0 + (Tm - Bm) * kx
    W, H = 1200, int(Y1 + 44)

    def pj(lon, lat):
        return X0 + (lon - L) * math.cos(math.radians(43.65)) * kx, Y0 + (Tm - lat) * kx

    def path(pts, close=False):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in (pj(a, b) for a, b in pts))
        return d + (" Z" if close else "")

    land = " ".join(path(r, True) for r in data["land"])
    communes = " ".join(path(l) for l in data["communes"])
    outside = " ".join(path(r, True) for r in data["outside"])
    borders = " ".join(path(l) for l in data["borders"])
    grid = "".join(f'<line x1="{x}" y1="{Y0}" x2="{x}" y2="{Y1:.0f}"/>' for x in range(X0, X1 + 1, 80)) + \
           "".join(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}"/>' for y in range(Y0, int(Y1) + 1, 80))

    def icon(kind, x, y):
        if kind == "home":
            return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="14" fill="none" stroke="{G}" stroke-width="2">'
                    f'<animate attributeName="r" values="14;60" dur="2.2s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="1;0" dur="2.2s" repeatCount="indefinite"/></circle>'
                    f'<path d="{gear(x, y, 21, 16, 10)}" fill="{G_DARK}" stroke="{G}" stroke-width="2.2">'
                    f'<animateTransform attributeName="transform" type="rotate" from="0 {x:.0f} {y:.0f}" to="360 {x:.0f} {y:.0f}" dur="12s" repeatCount="indefinite"/></path>'
                    f'<text x="{x:.0f}" y="{y + 5:.0f}" font-size="13" text-anchor="middle" class="b">27</text>')
        if kind in ("vault", "rad"):
            g = f'<path d="{gear(x, y, 10, 7, 8)}" fill="{BG}" stroke="{G}" stroke-width="1.6"/>'
            if kind == "rad":
                g += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="22" fill="{G}" opacity=".07"/>'
                      f'<circle cx="{x:.0f}" cy="{y:.0f}" r="22" fill="none" stroke="{G_DIM}" stroke-dasharray="3 4">'
                      f'<animate attributeName="opacity" values=".3;1;.3" dur="1.4s" repeatCount="indefinite"/></circle>')
            return g
        if kind == "ruin":
            return (f'<path d="M{x - 9:.0f},{y + 8:.0f} L{x - 9:.0f},{y - 4:.0f} L{x - 4:.0f},{y - 9:.0f} L{x - 1:.0f},{y - 3:.0f} '
                    f'L{x + 3:.0f},{y - 7:.0f} L{x + 9:.0f},{y - 1:.0f} L{x + 9:.0f},{y + 8:.0f} Z" fill="{BG}" stroke="{G}" stroke-width="1.6"/>')
        if kind == "crater":
            return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="none" stroke="{G}" stroke-width="1.6"/>'
                    f'<circle cx="{x:.0f}" cy="{y:.0f}" r="14" fill="none" stroke="{G_DIM}" stroke-dasharray="2 4"/>')
        if kind == "iut":
            return f'<rect x="{x - 8:.0f}" y="{y - 8:.0f}" width="16" height="16" fill="{BG}" stroke="{G}" stroke-width="2.2"/>'
        if kind == "work":
            return f'<path d="M{x:.0f},{y - 11:.0f} L{x + 11:.0f},{y:.0f} L{x:.0f},{y + 11:.0f} L{x - 11:.0f},{y:.0f} Z" fill="{BG}" stroke="{G}" stroke-width="2.2"/>'
        return ""

    marks = []
    for title, sub, lon, lat, kind, (dx, dy, anc) in MAP_PLACES:
        x, y = pj(lon, lat)
        big = kind in ("home", "iut", "work")
        fs = 17 if kind == "home" else (14 if big else 13)
        lead = (f'<line x1="{x:.0f}" y1="{y + 12:.0f}" x2="{x + dx:.0f}" y2="{y + dy - 16:.0f}" stroke="{G_DIM}" stroke-width="1"/>'
                if abs(dy) > 40 else "")
        marks.append(f'{lead}{icon(kind, x, y)}'
                     f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" font-size="{fs}" text-anchor="{anc}" class="b" letter-spacing="1">{esc(title)}</text>'
                     f'<text x="{x + dx:.0f}" y="{y + dy + 15:.0f}" font-size="11" text-anchor="{anc}" class="dim" letter-spacing="1">{esc(sub)}</text>')

    lx, ly = 836, Y1 - 166
    legend = f'''<g>
      <rect x="{lx}" y="{ly}" width="300" height="148" fill="{BG}" stroke="{G_DIM}"/>
      <path d="{gear(lx + 22, ly + 22, 10, 7, 8)}" fill="{G_DARK}" stroke="{G}" stroke-width="1.6"/><text x="{lx + 44}" y="{ly + 27}" font-size="13">Abri</text>
      <circle cx="{lx + 22}" cy="{ly + 50}" r="11" fill="none" stroke="{G_DIM}" stroke-dasharray="3 4"/><text x="{lx + 44}" y="{ly + 55}" font-size="13">Zone irradiée</text>
      <rect x="{lx + 14}" y="{ly + 70}" width="16" height="16" fill="none" stroke="{G}" stroke-width="2"/><text x="{lx + 44}" y="{ly + 83}" font-size="13">École</text>
      <path d="M{lx + 22},{ly + 96} L{lx + 32},{ly + 106} L{lx + 22},{ly + 116} L{lx + 12},{ly + 106} Z" fill="none" stroke="{G}" stroke-width="2"/><text x="{lx + 44}" y="{ly + 111}" font-size="13">Alternance</text>
      <path d="M{lx + 13},{ly + 142} L{lx + 13},{ly + 130} L{lx + 18},{ly + 125} L{lx + 21},{ly + 131} L{lx + 25},{ly + 127} L{lx + 31},{ly + 133} L{lx + 31},{ly + 142} Z" fill="none" stroke="{G}" stroke-width="1.6"/><text x="{lx + 44}" y="{ly + 139}" font-size="13">Ruines</text>
    </g>'''
    cmp_x, cmp_y = X0 + 50, Y1 - 52
    compass = f'''<g>
      <circle cx="{cmp_x}" cy="{cmp_y}" r="32" fill="{BG}" stroke="{G_DIM}"/>
      <path d="M{cmp_x},{cmp_y - 26} L{cmp_x + 7},{cmp_y} L{cmp_x},{cmp_y + 26} L{cmp_x - 7},{cmp_y} Z" fill="none" stroke="{G}" stroke-width="1.5"/>
      <path d="M{cmp_x},{cmp_y - 26} L{cmp_x + 7},{cmp_y} L{cmp_x - 7},{cmp_y} Z" fill="{G}"/>
      <text x="{cmp_x}" y="{cmp_y - 38}" font-size="13" text-anchor="middle" class="b">N</text>
    </g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{crt_defs(W, H)}
    <clipPath id="scr"><rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22"/></clipPath>
    <clipPath id="mapc"><rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0:.0f}"/></clipPath>
    <pattern id="waves" width="40" height="18" patternUnits="userSpaceOnUse">
      <path d="M0,9 Q10,4 20,9 T40,9" fill="none" stroke="{G_DARK}" stroke-width="1.2"/>
    </pattern>
    <pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="10" stroke="{G_DARK}" stroke-width="2"/>
    </pattern>
    <style>
      .route {{ animation: route 1.2s linear infinite; }}
      @keyframes route {{ to {{ stroke-dashoffset: -22; }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  {screen(20, 20, W - 40, H - 40, 22)}
  <g class="flick" filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">MAP</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">TERRES DÉSOLÉES DU 06 · CÔTE D'AZUR</text>
    <g clip-path="url(#mapc)">
      <rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0:.0f}" fill="url(#waves)">
        <animateTransform attributeName="transform" type="translate" values="0,0;40,0" dur="6s" repeatCount="indefinite"/>
      </rect>
      <path d="{outside}" fill="{BG}" stroke="{G}" stroke-width="2.2" stroke-linejoin="round"/>
      <path d="{outside}" fill="url(#hatch)" stroke="none"/>
      <path d="{land}" fill="{BG}" stroke="{G}" stroke-width="2.2" stroke-linejoin="round"/>
      <path d="{borders}" fill="none" stroke="{G_MID}" stroke-width="1.6" stroke-dasharray="8 4 2 4"/>
      <path d="{communes}" fill="none" stroke="{G_DARK}" stroke-width="1.1" stroke-dasharray="4 3"/>
      <g stroke="{G_DARK}" stroke-width=".6" opacity=".6">{grid}</g>
      <text x="{X0 + 500}" y="{Y1 - 40:.0f}" font-size="16" class="dim" letter-spacing="8">MER MÉDITERRANÉE</text>
      <text x="{pj(6.875, 43.585)[0]:.0f}" y="{pj(6.875, 43.585)[1]:.0f}" font-size="11" class="dim" letter-spacing="2">VAR</text>
      <text x="{pj(6.875, 43.585)[0]:.0f}" y="{pj(6.875, 43.585)[1] + 14:.0f}" font-size="10" class="dim" letter-spacing="1">HORS ZONE</text>
      <text x="{X1 - 8}" y="{pj(7.54, 43.81)[1]:.0f}" font-size="11" text-anchor="end" class="dim" letter-spacing="2">ITALIE</text>
    </g>
    <rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0:.0f}" fill="none" stroke="{G_DIM}"/>
    {"".join(marks)}
    {legend}
    {compass}
  </g>
  {screen_overlay(20, 20, W - 40, H - 40, 22)}
</svg>
'''
    (OUT / "map.svg").write_text(svg, encoding="utf-8")


# ───────────────────────── radio.svg ─────────────────────────
def radio():
    W, H = 1200, 400
    N = len(RADIO_STATIONS)
    T = 3.0
    cyc, pct = N * T, 100 / N
    rows, sel = [], []
    for i, st in enumerate(RADIO_STATIONS):
        y = 124 + i * 44
        rows.append(f'<text x="64" y="{y}" font-size="17">{esc(st)}</text>')
        sel.append(f'<g class="sel" style="animation-delay:{i * T:.1f}s"><rect x="52" y="{y - 24}" width="470" height="34" fill="{G}"/>'
                   f'<text x="64" y="{y}" font-size="17" class="b" style="fill:{BG}">{esc(st)}</text></g>')
    # oscilloscope
    ox, oy, ow, oh = 600, 96, 548, 250
    cy = oy + oh / 2
    grid = "".join(f'<line x1="{ox + k * ow / 10:.0f}" y1="{oy}" x2="{ox + k * ow / 10:.0f}" y2="{oy + oh}"/>' for k in range(11)) + \
           "".join(f'<line x1="{ox}" y1="{oy + k * oh / 6:.0f}" x2="{ox + ow}" y2="{oy + k * oh / 6:.0f}"/>' for k in range(7))

    def wave(amp, period, phase=0.0, mod=0.0):
        pts = []
        for k in range(0, int(ow * 2) + 1, 4):
            env = 1 + mod * math.sin(k / ow * 2 * math.pi * 2)
            pts.append(f"{ox + k:.0f},{cy + amp * env * math.sin(2 * math.pi * k / period + phase):.1f}")
        return "M" + " L".join(pts)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{crt_defs(W, H)}
    <clipPath id="scr"><rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22"/></clipPath>
    <clipPath id="osc"><rect x="{ox}" y="{oy}" width="{ow}" height="{oh}"/></clipPath>
    <style>
      .sel {{ opacity: 0; animation: sel {cyc:.1f}s step-end infinite; }}
      @keyframes sel {{ 0% {{ opacity: 1 }} {pct:.3f}% {{ opacity: 0 }} 100% {{ opacity: 0 }} }}
      .w1 {{ animation: w1 1.6s linear infinite; }} @keyframes w1 {{ to {{ transform: translateX(-{ow / 2:.0f}px) }} }}
      .w2 {{ animation: w2 2.6s linear infinite; }} @keyframes w2 {{ to {{ transform: translateX(-{ow / 2:.0f}px) }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  {screen(20, 20, W - 40, H - 40, 22)}
  <g class="flick" filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">RADIO</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">FRÉQUENCES DE L'ABRI 27</text>
    <line x1="52" y1="70" x2="{W - 52}" y2="70" stroke="{G_DIM}"/>
    {"".join(rows)}
    {"".join(sel)}
    <rect x="{ox}" y="{oy}" width="{ow}" height="{oh}" fill="none" stroke="{G_DIM}"/>
    <g stroke="{G_DARK}" stroke-width="1">{grid}</g>
    <g clip-path="url(#osc)" fill="none">
      <path class="w1" d="{wave(70, ow / 4, 0, .35)}" stroke="{G}" stroke-width="2.4"/>
      <path class="w2" d="{wave(38, ow / 7, 1.3, .5)}" stroke="{G_DIM}" stroke-width="1.6"/>
    </g>
    <text x="{ox}" y="{oy + oh + 28}" font-size="13" class="dim">SIGNAL</text>
    <text x="{ox + ow}" y="{oy + oh + 28}" font-size="13" text-anchor="end" class="dim">06.27 MHz</text>
  </g>
  {screen_overlay(20, 20, W - 40, H - 40, 22)}
</svg>
'''
    (OUT / "radio.svg").write_text(svg, encoding="utf-8")


# ───────────────────────── inventory.svg ─────────────────────────
def rifle(st, ln):
    """Carabine de chasse à verrou avec lunette (dessin original, canon vers la droite, crosse à x=0)."""
    return f"""
      <path d="M0,10 L36,4 L92,6 L112,10 L112,24 L96,26 L64,24 L34,34 L0,34 Z" {st}/>
      <line x1="10" y1="14" x2="10" y2="31" stroke="{G}" stroke-width="1.2"/>
      <rect x="112" y="8" width="66" height="15" rx="2" {st}/>
      <path d="M126,23 Q128,36 140,36 L146,36 Q140,30 140,23" {ln}/>
      <path d="M132,23 L134,32" {ln}/>
      <path d="M160,8 L166,0 M166,0 m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0" {ln}/>
      <path d="M150,23 L232,23 L236,18 L178,15 Z" {st}/>
      <rect x="176" y="11" width="134" height="6" rx="1.5" {st}/>
      <rect x="306" y="9" width="8" height="10" rx="1" {st}/>
      <rect x="138" y="-2" width="6" height="11" {st}/>
      <rect x="196" y="-2" width="6" height="11" {st}/>
      <path d="M118,-16 L132,-12 L208,-12 L222,-20 L222,4 L208,-4 L132,-4 L118,0 Z" {st}/>
      <rect x="164" y="-22" width="12" height="10" rx="2" {st}/>
      <line x1="222" y1="-20" x2="222" y2="4" stroke="{G}" stroke-width="2.4"/>
      <line x1="134" y1="-8" x2="206" y2="-8" stroke="{G}" stroke-width="1" opacity=".6"/>"""


def character():
    """Habitant original de l'Abri 27, style cartoon rétro (grosse tête, bras « tuyau »), centré en x=0, pieds à y≈348."""
    st = f'fill="{G_DARK}" stroke="{G}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"'
    ln = f'fill="none" stroke="{G}" stroke-width="1.8" stroke-linecap="round"'

    def tube(d):
        # bras cartoon : contour vert + intérieur sombre
        return (f'<path d="{d}" fill="none" stroke="{G}" stroke-width="20" stroke-linecap="round"/>'
                f'<path d="{d}" fill="none" stroke="{G_DARK}" stroke-width="15" stroke-linecap="round"/>')

    return f"""
      <!-- jambes -->
      <path d="M-38,226 L-12,226 L-12,316 L-36,316 Z" {st}/>
      <path d="M12,226 L38,226 L36,316 L12,316 Z" {st}/>
      <!-- grosses bottes -->
      <path d="M-40,310 L-8,310 L-6,348 L-58,348 Q-62,326 -40,310 Z" {st}/>
      <path d="M40,310 L8,310 L6,348 L58,348 Q62,326 40,310 Z" {st}/>
      <line x1="-56" y1="338" x2="-8" y2="338" stroke="{G}" stroke-width="1.4"/>
      <line x1="56" y1="338" x2="8" y2="338" stroke="{G}" stroke-width="1.4"/>
      <!-- bras gauche levé : salut de la main -->
      {tube("M-36,150 Q-66,150 -80,104")}
      <g>
        <circle cx="-84" cy="92" r="14" {st}/>
        <path d="M-96,86 Q-100,70 -94,68 Q-90,70 -90,84 M-88,80 Q-90,62 -84,60 Q-79,62 -80,80 M-79,82 Q-78,64 -72,64 Q-67,67 -71,84 M-70,90 Q-62,82 -58,86 Q-58,92 -68,98" {st}/>
        <animateTransform attributeName="transform" type="rotate" values="0 -80 104;-14 -80 104;0 -80 104;12 -80 104;0 -80 104" dur="1.6s" repeatCount="indefinite"/>
      </g>
      <!-- bras droit + laptop -->
      {tube("M36,150 Q60,170 62,212")}
      <g transform="rotate(-6 74 230)">
        <rect x="66" y="186" width="18" height="90" rx="3" {st}/>
        <line x1="72" y1="194" x2="72" y2="268" stroke="{G}" stroke-width="1"/>
      </g>
      <circle cx="63" cy="218" r="13" {st}/>
      <!-- corps : sweat à capuche -->
      <path d="M-42,136 Q-30,126 -14,126 L14,126 Q30,126 42,136 L46,232 L-46,232 Z" {st}/>
      <path d="M-28,128 Q0,152 28,128" {ln}/>
      <path d="M-8,140 L-10,168 M8,140 L10,168" {ln}/>
      <line x1="-46" y1="222" x2="46" y2="222" stroke="{G}" stroke-width="2"/>
      <rect x="-9" y="216" width="18" height="12" rx="2" fill="{BG}" stroke="{G}" stroke-width="1.6"/>
      <text x="26" y="206" font-size="17" text-anchor="middle" class="b">27</text>
      <!-- carabine en bandoulière -->
      <path d="M-40,140 Q-4,182 40,228" fill="none" stroke="{G}" stroke-width="3"/>
      <g transform="translate(-52 238) rotate(-50) scale(.56)">{rifle(st, ln)}</g>
      <!-- tête cartoon -->
      <rect x="-9" y="118" width="18" height="12" {st}/>
      <circle cx="0" cy="68" r="58" {st}/>
      <!-- cheveux sombres en épis -->
      <path d="M-56,58 Q-60,6 0,4 Q58,6 56,56 L48,38 L42,50 L32,28 L20,42 L8,22 L-4,40 L-18,20 L-28,40 L-42,28 L-46,48 Z" fill="{G_DIM}" stroke="{G}" stroke-width="2.4" stroke-linejoin="round"/>
      <!-- lunettes rondes + yeux -->
      <circle cx="-21" cy="70" r="15" fill="{BG}" stroke="{G}" stroke-width="2.4"/>
      <circle cx="21" cy="70" r="15" fill="{BG}" stroke="{G}" stroke-width="2.4"/>
      <line x1="-6" y1="70" x2="6" y2="70" stroke="{G}" stroke-width="2.4"/>
      <ellipse cx="-19" cy="72" rx="5" ry="7" fill="{G}"><animate attributeName="ry" values="7;7;1;7;7" keyTimes="0;.9;.93;.96;1" dur="4s" repeatCount="indefinite"/></ellipse>
      <ellipse cx="23" cy="72" rx="5" ry="7" fill="{G}"><animate attributeName="ry" values="7;7;1;7;7" keyTimes="0;.9;.93;.96;1" dur="4s" repeatCount="indefinite"/></ellipse>
      <path d="M-34,48 Q-22,42 -10,48 M10,48 Q22,42 34,48" {ln}/>
      <!-- nez, sourire, taches de rousseur -->
      <path d="M-2,86 Q3,92 -3,95" {ln}/>
      <path d="M-16,104 Q0,116 16,104" {ln}/>
      <g fill="{G}"><circle cx="-38" cy="92" r="1.6"/><circle cx="-33" cy="96" r="1.6"/><circle cx="-41" cy="98" r="1.6"/>
        <circle cx="38" cy="92" r="1.6"/><circle cx="33" cy="96" r="1.6"/><circle cx="41" cy="98" r="1.6"/></g>
      <!-- casque audio -->
      <path d="M-60,70 Q-64,-10 0,-12 Q64,-10 60,70" fill="none" stroke="{G}" stroke-width="5" stroke-linecap="round"/>
      <rect x="-72" y="52" width="16" height="36" rx="7" {st}/>
      <rect x="56" y="52" width="16" height="36" rx="7" {st}/>"""


def inventory():
    W, H = 1200, 640
    N = len(INVENTORY)
    T = 2.4                      # secondes par objet sélectionné
    cyc = N * T
    pct = 100 / N
    list_x, list_y, row = 52, 136, 34

    tabs_row = ["TOUT", "ARMES", "ÉQUIPEMENT", "OUTILS"]
    sub, x = [], 52
    for k, name in enumerate(tabs_row):
        cls = ' class="b"' if k == 0 else ' class="dim"'
        sub.append(f'<text x="{x:.0f}" y="98" font-size="16"{cls} letter-spacing="2">{esc(name)}</text>')
        x += len(name) * 11.6 + 34

    rows, sel, cards = [], [], []
    for i, (name, typ, lvl, wgt, val, eq) in enumerate(INVENTORY):
        y = list_y + i * row
        label = ("■ " if eq else "  ") + name
        rows.append(f'<text x="{list_x + 8}" y="{y}" font-size="17" xml:space="preserve">{esc(label)}</text>'
                    f'<text x="{list_x + 340}" y="{y}" font-size="15" text-anchor="end" class="dim">{val}</text>')
        delay = f"animation-delay:{i * T:.2f}s"
        sel.append(f'<g class="sel" style="{delay}"><rect x="{list_x}" y="{y - 22}" width="352" height="30" fill="{G}"/>'
                   f'<text x="{list_x + 8}" y="{y}" font-size="17" xml:space="preserve" style="fill:{BG}" class="b">{esc(label)}</text>'
                   f'<text x="{list_x + 340}" y="{y}" font-size="15" text-anchor="end" style="fill:{BG}">{val}</text></g>')
        bars = "".join(
            f'<rect x="{962 + k * 15}" y="452" width="11" height="16" fill="{G if k < lvl else "none"}" stroke="{G_DIM}"/>'
            for k in range(10)
        )
        cards.append(f"""<g class="sel" style="{delay}">
        <text x="860" y="420" font-size="20" class="b">{esc(name.upper())}</text>
        <text x="860" y="465" font-size="14" class="dim">MAÎTRISE</text>{bars}
        <text x="1148" y="465" font-size="14" text-anchor="end" class="b">{lvl}/10</text>
        <text x="860" y="495" font-size="14" class="dim">TYPE</text><text x="1148" y="495" font-size="14" text-anchor="end">{esc(typ)}</text>
        <text x="860" y="522" font-size="14" class="dim">POIDS</text><text x="1148" y="522" font-size="14" text-anchor="end">{wgt}</text>
        <text x="860" y="549" font-size="14" class="dim">VALEUR</text><text x="1148" y="549" font-size="14" text-anchor="end">{val}</text>
      </g>""")

    # personnage + annotations d'équipement
    cx, cy, sc = 590, 132, 0.98
    callouts = []
    for j, (slot, item, (ax, ay)) in enumerate(APPAREL):
        px, py = cx + ax * sc, cy + ay * sc
        lx, ly = 860, 128 + j * 50
        callouts.append(
            f'<circle cx="{px:.0f}" cy="{py:.0f}" r="3.5" fill="{G}"/>'
            f'<path d="M{px:.0f},{py:.0f} L{lx - 34},{ly + 2} L{lx - 8},{ly + 2}" fill="none" stroke="{G_DIM}" stroke-width="1.2"/>'
            f'<text x="{lx}" y="{ly - 6}" font-size="12" class="dim" letter-spacing="2">{slot}</text>'
            f'<text x="{lx}" y="{ly + 12}" font-size="15">{esc(item)}</text>'
        )
    total_w = sum(it[3] for it in INVENTORY)
    caps = sum(it[4] for it in INVENTORY)
    foot_y = cy + 350 * sc

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{crt_defs(W, H)}
    <clipPath id="scr"><rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="22"/></clipPath>
    <clipPath id="holo"><rect x="470" y="100" width="240" height="{foot_y - 90:.0f}"/></clipPath>
    <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".85" stop-color="{G}" stop-opacity=".06"/><stop offset="1" stop-color="{G}" stop-opacity=".22"/>
    </linearGradient>
    <style>
      .sel {{ opacity: 0; animation: sel {cyc:.2f}s step-end infinite; }}
      @keyframes sel {{ 0% {{ opacity: 1 }} {pct:.3f}% {{ opacity: 0 }} 100% {{ opacity: 0 }} }}
      .idle {{ animation: idle 3.2s ease-in-out infinite; }}
      @keyframes idle {{ 0%,100% {{ transform: translateY(0) }} 50% {{ transform: translateY(-3px) }} }}
      .sweep {{ animation: sweep 4s linear infinite; }}
      @keyframes sweep {{ from {{ transform: translateY(-70px) }} to {{ transform: translateY(400px) }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BEZEL}"/>
  {screen(20, 20, W - 40, H - 40, 22)}
  <g class="flick" filter="url(#glow)">
    <text x="52" y="58" font-size="22" class="b" letter-spacing="3">INV</text>
    <text x="{W - 52}" y="58" font-size="14" text-anchor="end" class="dim">INVENTAIRE DE L'HABITANT</text>
    <line x1="52" y1="70" x2="{W - 52}" y2="70" stroke="{G_DIM}"/>
    {"".join(sub)}

    <!-- liste d'objets, la sélection défile -->
    {"".join(rows)}
    {"".join(sel)}

    <!-- personnage -->
    <ellipse cx="{cx}" cy="{foot_y:.0f}" rx="92" ry="15" fill="none" stroke="{G_DIM}" stroke-width="1.4" stroke-dasharray="6 6">
      <animate attributeName="stroke-dashoffset" from="0" to="-48" dur="2s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="{cx}" cy="{foot_y:.0f}" rx="62" ry="9" fill="{G}" opacity=".08"/>
    <g class="idle"><g transform="translate({cx} {cy}) scale({sc})">{character()}</g></g>
    <g clip-path="url(#holo)"><rect class="sweep" x="470" y="100" width="240" height="60" fill="url(#sweep)"/></g>
    {"".join(callouts)}

    <!-- fiche de l'objet sélectionné -->
    <line x1="860" y1="388" x2="1148" y2="388" stroke="{G_DIM}"/>
    {"".join(cards)}

    <!-- barre du bas -->
    <line x1="52" y1="568" x2="{W - 52}" y2="568" stroke="{G_DIM}"/>
    <text x="52" y="597" font-size="16" class="b">PV 100/100</text>
    <text x="360" y="597" font-size="16">POIDS {total_w}/250</text>
    <text x="660" y="597" font-size="16">CAPSULES {caps}</text>
    <text x="{W - 52}" y="597" font-size="16" text-anchor="end" class="b">ABRI 27</text>
  </g>
  {screen_overlay(20, 20, W - 40, H - 40, 22)}
</svg>
"""
    (OUT / "inventory.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    terminal()
    special()
    inventory()
    tabs()
    quests()
    holotapes()
    map_svg()
    radio()
    print("SVG générés dans", OUT)
