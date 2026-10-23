// Registro de escenas, orquestas, sellos y cantantes de la salsa según El libro de la salsa de César Miguel Rondón. Cada fichero de capítulo (data/NN-*.js,
// escritos a mano leyendo el libro) llama a SALSA.chapter({...}) y SALSA.add([...], n).
// Los datos se fusionan por id: los arrays se unen y cada capítulo puede añadir
// discos, citas (refs) y una nota propia sobre una escena ya definida en otro.
window.SALSA = (function () {
  const genres = new Map();
  const chapters = [];

  const FAMILIES = {
    cuba:       { name: 'Cuba: son, danzón, conjunto, sonora y la matriz caribeña', color: '#e9b44c' },
    palladium:  { name: 'Nueva York de los cuarenta y cincuenta: Palladium, mambo, latin jazz', color: '#a78bfa' },
    boricua:    { name: 'Puerto Rico: plena, bomba, Cortijo y los combos de la isla', color: '#38bdf8' },
    sesenta:    { name: 'Los sesenta en Nueva York: pachanga, bugalú, latin soul', color: '#f472b6' },
    charanga:   { name: 'Charangas: flauta y violines', color: '#facc15' },
    fania:      { name: 'Fania y el sonido de Nueva York: el barrio, las Estrellas, el boom', color: '#ef4444' },
    tipico:     { name: 'Lo típico y los soneros: la vuelta al conjunto y a la tradición', color: '#d97706' },
    vanguardia: { name: 'Vanguardia y conciencia: experimentación, salsa con letra', color: '#22c55e' },
    venezuela:  { name: 'Venezuela y Colombia: la salsa del sur del Caribe', color: '#fb923c' },
    quisqueya:  { name: 'Quisqueya: el merengue y la República Dominicana', color: '#2dd4bf' },
    despues:    { name: 'Después del boom: salsa romántica, erótica, timba y nuevos caminos', color: '#e879f9' },
    medios:     { name: 'Industria, medios, cine y crítica: sellos, radio, el nombre «salsa»', color: '#94a3b8' },
  };


  const key = (t) => (t.a + '|' + t.t).toLowerCase();

  function mergeArr(a = [], b = [], k = (x) => (typeof x === 'string' ? x.toLowerCase() : JSON.stringify(x))) {
    const seen = new Set(a.map(k));
    const out = a.slice();
    for (const x of b) if (!seen.has(k(x))) { seen.add(k(x)); out.push(x); }
    return out;
  }

  // Anota en cada disco los capítulos que lo citan.
  function cite(tracks, t, ch) {
    const m = tracks.find((x) => key(x) === key(t));
    if (m && ch != null) m.chs = mergeArr(m.chs, [ch]);
  }

  function add(list, chapter) {
    for (const g of list) {
      let cur = genres.get(g.id);
      if (!cur) {
        cur = { id: g.id, aka: [], influences: [], artists: [], tracks: [], labels: [], refs: [], notes: [], chapters: [] };
        genres.set(g.id, cur);
      }
      for (const f of ['aka', 'influences', 'artists', 'labels']) cur[f] = mergeArr(cur[f], g[f]);
      cur.tracks = mergeArr(cur.tracks, (g.tracks || []).map((t) => ({ ...t })), key);
      for (const t of g.tracks || []) {
        if (t.ess) { const m = cur.tracks.find((x) => key(x) === key(t)); if (m) m.ess = 1; }
        cite(cur.tracks, t, chapter);
      }
      cur.refs = mergeArr(cur.refs, (g.refs || []).map((r) => ({ ch: chapter, ...r })), (r) => r.q);
      for (const f of ['name', 'family', 'start', 'end', 'place', 'desc']) if (g[f] != null && cur[f] == null) cur[f] = g[f];
      if (g.desc != null) cur.descCh = cur.descCh ?? chapter;
      if (g.note) cur.notes.push({ ch: chapter, text: g.note });
      if (chapter != null && !cur.chapters.includes(chapter)) cur.chapters.push(chapter);
    }
  }

  return {
    FAMILIES,
    chapters,
    genres,
    chapter(meta) { chapters.push(meta); },
    add,
  };
})();
