# Profil GitHub Tiretinium : terminal de l'Abri 27

Repo de profil GitHub (`Tiretinium/Tiretinium`). Le README est un terminal rétro façon Pip-Boy,
dans l'univers post-apocalyptique de Fallout, entièrement en SVG animés. Une page interactive
(console, mini-jeu, radio) est publiée sur GitHub Pages depuis `docs/`.

## Règles à respecter

- **Aucun élément officiel de Fallout / Bethesda** : pas de logo, pas de Vault Boy, pas de captures,
  pas d'icônes, pas de musiques ni de répliques du jeu, même retouchés ou redessinés. Tout est dessiné
  à la main en SVG, dans l'esprit du jeu mais original (personnage, carabine, abris, terminal...).
- **Pas l'adresse perso de l'auteur** sur la carte. L'Abri 27 est placé au centre de Nice (06000).
- **Secrets** : le jeton PlayStation est uniquement dans le secret GitHub `PSN_NPSSO`.
  Ne jamais l'écrire dans un fichier, un commit ou un log.
- Textes en **français**. Palette : `#3dff86` (vert), `#2fb866` (texte secondaire), `#1d7a43` (traits),
  `#0c2a17` (remplissage), `#06100a` (fond d'écran), `#151515` (cadre). Police : `'Courier New', monospace`.
- Les SVG doivent rester compatibles GitHub : pas de JavaScript, pas de police ni d'image externe,
  animations en CSS `@keyframes` ou SMIL (`<animate>`, `<set>`, `<animateTransform>`).

## Structure

```
README.md                      le profil (sections STAT / INV / DATA / MAP / RADIO)
assets/                        tous les SVG affichés
scripts/vault_assets.py        SVG statiques : terminal (+ séquence de démarrage), S.P.E.C.I.A.L.,
                               inventaire (personnage + carabine), quêtes, holotapes, carte, radio, onglets
scripts/data/cote_azur.json    contours de la côte et des communes pour la carte (IGN / Etalab)
scripts/contrib_graph.py       graphe de contributions          -> assets/contributions.svg
scripts/xp_bar.py              niveau + barre d'XP              -> assets/xp.svg
scripts/stats.py               écran STATISTIQUES               -> assets/stats.svg
scripts/transmissions.py       dernières activités GitHub       -> assets/transmissions.svg
scripts/psn_games.py           derniers jeux PlayStation        -> assets/psn.svg
scripts/psn_trophies.py        trophées PlayStation             -> assets/psn_trophies.svg
scripts/weather.py             météo de Nice (Open-Meteo)       -> assets/meteo.svg
scripts/site/build_site.py     page interactive                 -> docs/index.html
scripts/site/console.js        console (help, whoami, hack...), mini-jeu de piratage, séquence de démarrage
scripts/site/radio.js          radio : musique originale générée en Web Audio + oscilloscope
.github/workflows/contributions.yml   régénère les données toutes les 6 h et à chaque push concerné
```

## Commandes

```bash
# SVG statiques (après une modif de textes, quêtes, holotapes, inventaire, carte...)
python scripts/vault_assets.py

# Page interactive (dépendance : pip install markdown)
python scripts/site/build_site.py                      # -> docs/index.html (GitHub Pages)
python scripts/site/build_site.py --preview out.html   # aperçu autonome, images externes remplacées

# Les scripts de données ont besoin d'Internet ; ils tournent normalement dans GitHub Actions.
# Chacun accepte un fichier local en dernier argument pour tester sans réseau.
```

- Les contenus à modifier (lignes du terminal, S.P.E.C.I.A.L., inventaire, équipement du personnage,
  quêtes, holotapes, lieux de la carte, stations radio) sont dans la section **CONFIG** en haut de
  `scripts/vault_assets.py`. Relancer le script puis commiter les SVG générés.
- Les SVG de `assets/` produits par le workflow (contributions, xp, stats, transmissions, psn,
  psn_trophies, meteo) et `docs/index.html` sont réécrits par GitHub Actions : ne pas les éditer à la main.

## Mise en ligne

1. Pousser sur `main`.
2. **GitHub Pages** : Settings → Pages → Source « Deploy from a branch » → `main` / `/docs`.
   La page est alors sur https://tiretinium.github.io/Tiretinium/ (lien déjà présent dans le README).
3. **PlayStation** (facultatif) : se connecter sur playstation.com, ouvrir
   https://ca.account.sony.com/api/v1/ssocookie dans le même navigateur, copier la valeur `npsso`,
   puis Settings → Secrets and variables → Actions → New repository secret, nom `PSN_NPSSO`.
   Le jeton expire après environ 60 jours : remplacer le secret quand l'écran affiche « jeton à renouveler ».
4. Onglet Actions → workflow « Profile data » → Run workflow, pour un premier passage.
