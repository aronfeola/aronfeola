#!/usr/bin/env node
/*
 * Genera el PNG de un anuncio a partir de la plantilla de un estilo y un contenido.
 *
 *   node scripts/render_anuncio.js <estilo> <contenido.json> <salida.png> [--ratio 1:1]
 *
 * <estilo>  nombre de la carpeta en estilos/ (ej. "mi-estilo")
 * contenido.json:
 *   {
 *     "textos": { "titular": "Regalos con tu logo", "cta": "Pedí presupuesto" },
 *     "fotos":  { "producto": "fotos/soporte.jpg" },
 *     "variables": { "--color-acento": "#ff5a00" }      (opcional: pisa variables CSS)
 *   }
 *
 * En la plantilla.html: data-texto="titular" (texto), data-foto="producto" (imagen),
 * data-opcional (se saca si no hay contenido), data-fit (achica la letra hasta que entre).
 * <body data-ratio> vale 4x5, 1x1, 9x16 u otro, para reglas de CSS por proporción.
 * En los textos: salto de línea con \n y **palabra** para resaltar.
 *
 * Necesita Playwright con Chromium (npm i playwright && npx playwright install chromium).
 */
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

function cargarPlaywright() {
  for (const origen of ['playwright', '/opt/node-tools/node_modules/playwright']) {
    try { return require(origen); } catch (e) { /* probar el siguiente */ }
  }
  console.error('No encuentro Playwright. Instalalo con:\n  npm i playwright\n  npx playwright install chromium');
  process.exit(1);
}

(async () => {
  const args = process.argv.slice(2);
  const iRatio = args.indexOf('--ratio');
  const ratio = iRatio >= 0 ? args.splice(iRatio, 2)[1] : null;
  const [estilo, contenidoRuta, salida] = args;
  if (!estilo || !contenidoRuta || !salida) {
    console.error('Uso: node scripts/render_anuncio.js <estilo> <contenido.json> <salida.png> [--ratio 1:1]');
    process.exit(1);
  }

  const raiz = path.resolve(__dirname, '..');
  const carpeta = path.join(raiz, 'estilos', estilo);
  const plantilla = path.join(carpeta, 'plantilla.html');
  if (!fs.existsSync(plantilla)) {
    const hay = fs.readdirSync(path.join(raiz, 'estilos'), { withFileTypes: true })
      .filter((d) => d.isDirectory() && !d.name.startsWith('_')).map((d) => d.name);
    console.error(`No existe el estilo "${estilo}". Estilos guardados: ${hay.join(', ') || '(ninguno)'}`);
    process.exit(1);
  }
  const contenido = JSON.parse(fs.readFileSync(contenidoRuta, 'utf8'));
  const config = JSON.parse(fs.readFileSync(path.join(carpeta, 'estilo.json'), 'utf8'));

  let [W, H] = String(contenido.tamano || `${config.lienzo.ancho}x${config.lienzo.alto}`).split('x').map(Number);
  if (ratio) {
    const [a, b] = ratio.split(':').map(Number);
    H = Math.round((W * b) / a);
  }

  // Las fotos se pasan como rutas; las vuelvo URLs absolutas para que el navegador las encuentre.
  const fotos = {};
  for (const [k, v] of Object.entries(contenido.fotos || {})) {
    const abs = path.resolve(v);
    if (!fs.existsSync(abs)) { console.error(`No encuentro la foto "${k}": ${v}`); process.exit(1); }
    fotos[k] = pathToFileURL(abs).href;
  }

  const { chromium } = cargarPlaywright();
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const errores = [];
  pagina.on('pageerror', (e) => errores.push(e.message));
  await pagina.goto(pathToFileURL(plantilla).href);

  const avisos = await pagina.evaluate(({ W, H, ratio, textos, fotos, variables }) => {
    const avisos = [];
    const raiz = document.documentElement;
    raiz.style.setProperty('--w', W + 'px');
    raiz.style.setProperty('--h', H + 'px');
    const r = W / H;
    document.body.dataset.ratio = Math.abs(r - 0.8) < 0.02 ? '4x5' : Math.abs(r - 1) < 0.02 ? '1x1' : Math.abs(r - 0.5625) < 0.02 ? '9x16' : 'otro';
    for (const [k, v] of Object.entries(variables || {})) raiz.style.setProperty(k, v);

    const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    for (const el of document.querySelectorAll('[data-texto]')) {
      const k = el.dataset.texto;
      if (textos[k] !== undefined && textos[k] !== '') {
        el.innerHTML = esc(String(textos[k])).replace(/\*\*(.+?)\*\*/g, '<strong class="resaltado">$1</strong>').replace(/\n/g, '<br>');
      } else if (el.hasAttribute('data-opcional')) {
        el.remove();
      } else {
        avisos.push(`No cambié el texto "${k}" (no está en el contenido): quedó el de la plantilla.`);
      }
    }
    for (const el of document.querySelectorAll('[data-foto]')) {
      const k = el.dataset.foto;
      if (fotos[k]) {
        if (el.tagName === 'IMG') el.src = fotos[k]; else el.style.backgroundImage = `url("${fotos[k]}")`;
      } else if (el.hasAttribute('data-opcional')) {
        el.remove();
      } else {
        avisos.push(`No cambié la foto "${k}" (no está en el contenido): quedó la de la plantilla.`);
      }
    }
    return avisos;
  }, { W, H, ratio, textos: contenido.textos || {}, fotos, variables: contenido.variables || {} });

  await pagina.evaluate(() => document.fonts.ready);
  await pagina.evaluate(() => Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; })))));

  // Achicar la letra de los textos con data-fit hasta que entren en su caja.
  const ajustes = await pagina.evaluate(() => {
    const out = [];
    for (const el of document.querySelectorAll('[data-fit]')) {
      const inicial = parseFloat(getComputedStyle(el).fontSize);
      const minimo = inicial * parseFloat(el.dataset.fitMin || '0.45');
      let tam = inicial;
      // Se mide con alto automático: scrollHeight cuenta el trazo de la letra que sobresale de la línea
      // (en tipografías altas con interlineado chico daría siempre "no entra").
      const cabe = () => {
        const h0 = el.style.height, o0 = el.style.overflow;
        el.style.height = 'auto'; el.style.overflow = 'visible';
        const alto = el.offsetHeight, ancho = el.scrollWidth;
        el.style.height = h0; el.style.overflow = o0;
        return alto <= el.clientHeight + 1 && ancho <= el.clientWidth + 1;
      };
      while (!cabe() && tam > minimo) { tam *= 0.97; el.style.fontSize = tam + 'px'; }
      if (tam < inicial) out.push(`"${el.dataset.texto || el.dataset.fit}" se achicó de ${Math.round(inicial)} a ${Math.round(tam)} px para que entre.`);
      if (tam < inicial * 0.7) out.push(`ATENCIÓN: "${el.dataset.texto || el.dataset.fit}" quedó al ${Math.round((tam / inicial) * 100)}% de su tamaño: probablemente se lea mal en un celular. Acortá el texto.`);
      if (!cabe()) out.push(`ATENCIÓN: "${el.dataset.texto || el.dataset.fit}" no entra ni con la letra mínima: acortá el texto.`);
    }
    return out;
  });

  fs.mkdirSync(path.dirname(path.resolve(salida)), { recursive: true });
  await pagina.screenshot({ path: salida, clip: { x: 0, y: 0, width: W, height: H } });
  await navegador.close();

  [...avisos, ...ajustes, ...errores.map((e) => 'Error en la página: ' + e)].forEach((m) => console.error('• ' + m));
  console.log(`✓ ${salida} (${W} × ${H} px)`);
})();
