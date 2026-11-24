// ───────── Radio Abri 27 : musique d'ambiance générée en direct (composition originale) ─────────
// Swing lent façon vieille radio : accords en nappes, basse qui marche, mélodie improvisée,
// balais sur les temps 2 et 4, filtre « poste AM » et craquements de vinyle.
(function () {
  const btn = document.getElementById('radio-btn');
  const vol = document.getElementById('radio-vol');
  const label = document.getElementById('radio-now');
  const cv = document.getElementById('osc');
  if (!btn || !cv) return;
  const g2 = cv.getContext('2d');
  let ctx = null, master, analyser, timer = null, playing = false, nextTime = 0, step = 0, noiseBuf;

  const BPM = 88, EIGHTH = 60 / BPM / 2;
  const N = n => 440 * Math.pow(2, (n - 69) / 12);          // note MIDI -> Hz
  // progression : 2 tours de 4 mesures (accords en notes MIDI, basse en premier)
  const PROG = [
    [48, 52, 55, 59], [45, 52, 55, 60], [50, 53, 57, 60], [43, 53, 55, 59],
    [52, 55, 59, 62], [45, 49, 52, 55], [50, 53, 57, 60], [43, 53, 55, 59],
  ];
  const SCALE = [72, 74, 76, 79, 81, 84, 86, 88];           // pentatonique de do, octave haute
  const TITLES = ['« Couvre-feu sur la baie »', '« Les néons de l\'Abri 27 »', '« Swing des retombées »', '« Valse du compteur »'];

  function setup() {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain(); master.gain.value = vol.value / 100;
    const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 1300; bp.Q.value = .55;
    const shaper = ctx.createWaveShaper();
    const curve = new Float32Array(1024);
    for (let i = 0; i < 1024; i++) { const x = i / 512 - 1; curve[i] = Math.tanh(1.6 * x); }
    shaper.curve = curve;
    analyser = ctx.createAnalyser(); analyser.fftSize = 2048;
    master.connect(bp); bp.connect(shaper); shaper.connect(analyser); analyser.connect(ctx.destination);
    noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
    const d = noiseBuf.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    // craquements de vinyle en continu
    const crack = ctx.createBufferSource(); crack.buffer = noiseBuf; crack.loop = true;
    const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 2500;
    const cg = ctx.createGain(); cg.gain.value = .018;
    crack.connect(hp); hp.connect(cg); cg.connect(master); crack.start();
  }

  function tone(freq, t, dur, type, gain, attack = .01) {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(gain, t + attack);
    g.gain.exponentialRampToValueAtTime(.0001, t + dur);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + .05);
  }

  function brush(t, gain) {
    const s = ctx.createBufferSource(); s.buffer = noiseBuf;
    const f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 5000; f.Q.value = 1.2;
    const g = ctx.createGain();
    g.gain.setValueAtTime(gain, t); g.gain.exponentialRampToValueAtTime(.0001, t + .12);
    s.connect(f); f.connect(g); g.connect(master); s.start(t, Math.random()); s.stop(t + .15);
  }

  function pop(t) {
    const s = ctx.createBufferSource(); s.buffer = noiseBuf;
    const g = ctx.createGain(); g.gain.setValueAtTime(.12, t); g.gain.exponentialRampToValueAtTime(.0001, t + .02);
    s.connect(g); g.connect(master); s.start(t, Math.random()); s.stop(t + .03);
  }

  let lastNote = 2;
  function schedule(t) {
    const bar = Math.floor(step / 8) % PROG.length, e = step % 8, chord = PROG[bar];
    const swing = (e % 2) ? EIGHTH * .32 : 0;                // croches swinguées
    const tt = t + swing;
    if (e === 0) chord.slice(1).forEach(n => tone(N(n), t, EIGHTH * 8, 'triangle', .045, .25));
    if (e % 2 === 0) {                                        // basse qui marche (noires)
      const q = e / 2, root = chord[0] - 12;
      const walk = [root, root + 4 - (chord[1] % 12 === (chord[0] + 3) % 12 ? 1 : 0), root + 7, PROG[(bar + 1) % PROG.length][0] - 13];
      tone(N(walk[q]), t, EIGHTH * 1.8, 'sine', .22, .005);
    }
    if (e === 2 || e === 6) brush(t, .05);
    if (e % 2 === 1) brush(tt, .018);
    if (Math.random() < .5) {                                 // mélodie improvisée par petits pas
      lastNote = Math.max(0, Math.min(SCALE.length - 1, lastNote + [-2, -1, -1, 0, 1, 1, 2][Math.floor(Math.random() * 7)]));
      tone(N(SCALE[lastNote]), tt, EIGHTH * (Math.random() < .3 ? 2.6 : 1.2), 'square', .028, .008);
    }
    if (Math.random() < .04) pop(t + Math.random() * EIGHTH);
    if (step % 64 === 0) label.textContent = 'EN ONDES : ' + TITLES[(step / 64) % TITLES.length];
    step++;
  }

  function tick() {
    while (nextTime < ctx.currentTime + .2) { schedule(nextTime); nextTime += EIGHTH; }
  }

  function draw() {
    const w = cv.width, h = cv.height;
    g2.fillStyle = '#06100a'; g2.fillRect(0, 0, w, h);
    g2.strokeStyle = '#0c2a17'; g2.lineWidth = 1;
    for (let x = 0; x <= w; x += w / 10) { g2.beginPath(); g2.moveTo(x, 0); g2.lineTo(x, h); g2.stroke(); }
    for (let y = 0; y <= h; y += h / 6) { g2.beginPath(); g2.moveTo(0, y); g2.lineTo(w, y); g2.stroke(); }
    g2.strokeStyle = '#3dff86'; g2.lineWidth = 2.4; g2.shadowColor = '#3dff86'; g2.shadowBlur = 10;
    g2.beginPath();
    if (playing && analyser) {
      const buf = new Uint8Array(analyser.fftSize); analyser.getByteTimeDomainData(buf);
      for (let i = 0; i < w; i++) {
        const v = buf[Math.floor(i / w * buf.length)] / 128 - 1;
        const y = h / 2 + v * h * 3.2;
        i ? g2.lineTo(i, y) : g2.moveTo(i, y);
      }
    } else {
      const t = performance.now() / 600;
      for (let i = 0; i < w; i++) { const y = h / 2 + Math.sin(i / 18 + t) * 3 + (Math.random() - .5) * 2; i ? g2.lineTo(i, y) : g2.moveTo(i, y); }
    }
    g2.stroke(); g2.shadowBlur = 0;
    requestAnimationFrame(draw);
  }

  btn.onclick = async () => {
    try {
      if (!ctx) setup();
      if (ctx.state === 'suspended') await ctx.resume();
      playing = !playing;
      if (playing) {
        nextTime = ctx.currentTime + .1; step = 0;
        timer = setInterval(tick, 25);
        btn.textContent = '■ COUPER';
      } else {
        clearInterval(timer);
        btn.textContent = '▶ ÉCOUTER';
        label.textContent = 'RADIO ABRI 27 · 06.27 MHz';
      }
    } catch (e) { label.textContent = 'Le son n\'est pas disponible ici.'; }
  };
  vol.oninput = () => { if (master) master.gain.value = vol.value / 100; };
  if (typeof COMMANDS !== 'undefined') COMMANDS.radio_on = () => { btn.click(); return ['Radio ' + (playing ? 'allumée.' : 'coupée.')]; };
  draw();
})();
