// ───────── Console de l'Abri 27 ─────────
const out = document.getElementById('out');
const cmd = document.getElementById('cmd');
const hist = []; let hi = 0;

function print(text, cls) {
  const d = document.createElement('div');
  if (cls) d.className = cls;
  d.textContent = text;
  out.appendChild(d);
  out.scrollTop = out.scrollHeight;
}

const COMMANDS = {
  help: () => [
    'COMMANDES DISPONIBLES',
    '  whoami      fiche de l\'habitant',
    '  quetes      parcours en cours',
    '  projets     holotapes archivées',
    '  contact     fréquences radio',
    '  stat · inv · data · map · radio   changer d\'onglet',
    '  hack        pirater le terminal',
    '  radio_on    allumer / couper la radio',
    '  date        horloge de l\'abri',
    '  clear       effacer l\'écran',
    '  reboot      redémarrer le terminal',
  ],
  whoami: () => [
    'HABITANT ....... Tiretinium',
    'FORMATION ...... BUT Informatique, 3e année · IUT Nice Côte d\'Azur',
    'AFFECTATION .... Alternant chez Thales DMS',
    'SECTEUR ........ Sophia Antipolis, Côte d\'Azur',
  ],
  quetes: () => [
    '[PRINCIPALE] Diplôme de l\'Abri ........ 3/5 objectifs',
    '[PRINCIPALE] Contrat chez Thales DMS ... 2/4 objectifs',
    '[ANNEXE]     Le terminal de l\'habitant . 3/3 objectifs',
    '[ANNEXE]     Explorer les Terres désolées 1/3 objectifs',
  ],
  projets: () => [
    'HOLOTAPE 01 · Scubanion : animal virtuel qui progresse quand tu marches',
    '              github.com/Scubatana/scubanion',
    'HOLOTAPE 02 · ENIV : ENT léger, devoirs de la classe partagés',
    '              github.com/ENIV-ENT/ENIV · eniv.fr',
    'HOLOTAPE 03 · Tiretinium : profil GitHub façon terminal d\'abri',
  ],
  contact: () => [
    'EMAIL ..... Thomasbanderas06@gmail.com',
    'DISCORD ... discord.gg/Ge7AShwQ',
    'TIKTOK .... @tiretnium2703',
  ],
  date: () => [new Date().toLocaleString('fr-FR', { dateStyle: 'full', timeStyle: 'short' })],
  clear: () => { out.innerHTML = ''; return []; },
  hack: () => { startHack(); return ['Connexion au module de sécurité...']; },
  sudo: () => ['Accès refusé : seul le responsable de l\'abri peut faire ça.'],
};
['stat', 'inv', 'data', 'map', 'radio'].forEach(t => COMMANDS[t] = () => { show(t); return ['Onglet ' + t.toUpperCase() + ' ouvert.']; });

function run(raw) {
  const c = raw.trim().toLowerCase();
  if (!c) return;
  print('> ' + raw, 'dim');
  const f = COMMANDS[c.split(/\s+/)[0]];
  if (!f) { print('Commande inconnue : ' + c + '. Tape help.', 'err'); return; }
  f().forEach(l => print(l));
}

cmd.addEventListener('keydown', e => {
  e.stopPropagation();
  if (e.key === 'Enter') { hist.push(cmd.value); hi = hist.length; run(cmd.value); cmd.value = ''; }
  else if (e.key === 'ArrowUp' && hi > 0) { cmd.value = hist[--hi]; e.preventDefault(); }
  else if (e.key === 'ArrowDown') { hi = Math.min(hist.length, hi + 1); cmd.value = hist[hi] || ''; }
});
print('TIRET-OS v3.0 · console de l\'Abri 27. Tape help pour la liste des commandes.', 'dim');

// ───────── Mini-jeu de piratage ─────────
const WORDS = ['COMMIT', 'DEPLOY', 'KERNEL', 'BINARY', 'SOCKET', 'PYTHON', 'SERVER', 'MODULE', 'OBJECT',
  'SYNTAX', 'LAMBDA', 'BUFFER', 'CURSOR', 'THREAD', 'VECTOR', 'PACKET', 'BRANCH', 'MEMORY', 'SCRIPT', 'DOCKER'];
const JUNK = '!@#$%^&*()-_=+[]{}<>/\\|;:\'",.?';
const hack = document.getElementById('hack');

function likeness(a, b) { let n = 0; for (let i = 0; i < a.length; i++) if (a[i] === b[i]) n++; return n; }

function startHack() {
  const pool = [...WORDS].sort(() => Math.random() - .5).slice(0, 10);
  const answer = pool[Math.floor(Math.random() * pool.length)];
  const COLS = 2, ROWS = 15, W = 12, total = COLS * ROWS * W;
  const cells = Array.from({ length: total }, () => ({ ch: JUNK[Math.floor(Math.random() * JUNK.length)], w: -1 }));
  const slots = [];
  pool.forEach((word, wi) => {
    for (let tries = 0; tries < 200; tries++) {
      const start = Math.floor(Math.random() * (total - word.length));
      if (slots.some(([s, e]) => start < e + 2 && start + word.length + 2 > s)) continue;
      slots.push([start, start + word.length]);
      for (let k = 0; k < word.length; k++) cells[start + k] = { ch: word[k], w: wi };
      break;
    }
  });
  let tries = 4, over = false;
  const log = [];
  const base = 0xF4A0 + Math.floor(Math.random() * 0x200);
  const esc = c => c.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  function render() {
    let cols = '';
    for (let c = 0; c < COLS; c++) {
      let txt = '';
      for (let r = 0; r < ROWS; r++) {
        const line = c * ROWS + r;
        txt += `<span class="addr">0x${(base + line * W).toString(16).toUpperCase()}</span> `;
        for (let k = 0; k < W; k++) {
          const cell = cells[line * W + k];
          txt += cell.w >= 0 ? `<span class="w" data-w="${cell.w}">${esc(cell.ch)}</span>` : esc(cell.ch);
        }
        txt += '\n';
      }
      cols += `<div class="col">${txt}</div>`;
    }
    hack.innerHTML = `<div>TIRETINIUM INDUSTRIES · MODULE DE SÉCURITÉ</div>
      <div>${over ? '' : 'Trouve le mot de passe. Clique sur un mot.'}</div>
      <div>ESSAIS RESTANTS : ${'■ '.repeat(tries)}</div>
      <div class="grid">${cols}<div class="log">${log.map(esc).join('\n')}</div></div>
      <button id="hx">${over ? 'Fermer' : 'Abandonner'}</button>`;
    hack.querySelectorAll('.w').forEach(s => {
      const w = s.dataset.w;
      s.onmouseenter = () => hack.querySelectorAll(`.w[data-w="${w}"]`).forEach(x => x.classList.add('hl'));
      s.onmouseleave = () => hack.querySelectorAll(`.w[data-w="${w}"]`).forEach(x => x.classList.remove('hl'));
      s.onclick = () => guess(pool[w]);
    });
    document.getElementById('hx').onclick = close;
  }

  function guess(word) {
    if (over) return;
    log.push('> ' + word);
    if (word === answer) {
      log.push('> Mot de passe correct.', '> ACCÈS AUTORISÉ.', '> Bienvenue dans les archives de l\'Abri 27.');
      over = true;
      print('Piratage réussi : ' + answer + '. Accès autorisé.');
    } else {
      tries--;
      log.push('> Mot refusé.', `> Ressemblance : ${likeness(word, answer)}/6`);
      if (tries === 0) {
        log.push('> TERMINAL VERROUILLÉ.', `> Le mot était ${answer}.`);
        over = true;
        print('Piratage raté. Tape hack pour réessayer.', 'err');
      }
    }
    render();
  }

  function close() { hack.hidden = true; cmd.focus(); }
  hack.hidden = false;
  render();
}

// ───────── Séquence de démarrage ─────────
const BOOT = [
  ['TIRET-OS BIOS v3.0 · TIRETINIUM INDUSTRIES', ''],
  ['Test mémoire ........................ 65536 Ko', 'ok'],
  ['Détection du processeur ............. OK', 'ok'],
  ['Montage du disque ABRI-27 ........... OK', 'ok'],
  ['Synchronisation GitHub .............. OK', 'ok'],
  ['Chargement du profil : Tiretinium', ''],
  ['  > S.P.E.C.I.A.L. ..... chargé', 'dim'],
  ['  > Inventaire ......... 12 objets', 'dim'],
  ['  > Quêtes ............. 4 actives', 'dim'],
  ['  > Carte .............. Côte d\'Azur', 'dim'],
  ['', ''],
  ['BIENVENUE, HABITANT DE L\'ABRI 27.', 'ok'],
];
let bootTimer = null;
function boot() {
  const el = document.getElementById('boot'), log = document.getElementById('bootlog');
  el.classList.remove('off'); el.style.display = 'block';
  el.replaceWith(el.cloneNode(true));                 // relance les animations CSS
  const b = document.getElementById('boot'), bl = document.getElementById('bootlog');
  bl.innerHTML = '';
  let i = 0; clearTimeout(bootTimer);
  const finish = () => { clearTimeout(bootTimer); b.classList.add('off'); setTimeout(() => { b.style.display = 'none'; show(cur); }, 600); };
  b.onclick = finish;
  const step = () => {
    if (i >= BOOT.length) { bootTimer = setTimeout(finish, 700); return; }
    const [t, c] = BOOT[i++];
    const d = document.createElement('div'); if (c) d.className = c; d.textContent = t || ' ';
    bl.appendChild(d);
    bootTimer = setTimeout(step, i < 2 ? 900 : 170 + Math.random() * 140);
  };
  bootTimer = setTimeout(step, 250);
}
COMMANDS.reboot = () => { boot(); return ['Redémarrage du terminal...']; };
boot();
