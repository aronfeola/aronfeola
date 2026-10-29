# Agente creativo y de marketing (Meta Ads, método Charley T)

Un agente que funciona como tu director creativo, **solo para posteos estáticos**
(imágenes fijas para feed y anuncios): arma conceptos, textos, copys y briefs de foto, y
lee resultados. No hace video ni guiones. Aprende de dos cosas:

1. **Tu negocio** → carpetas `negocio/` y `resultados/` en la raíz del repo (las comparte
   con el resto del socio de negocios)
2. **El método** → carpeta `conocimiento/` (arranca con Charley T / @ctthedisrupter)

```
agente-marketing/
├── CLAUDE.md                  ← las instrucciones del agente (su "personalidad")
├── estilos/                   ← los estilos de anuncio guardados (ver estilos/README.md)
├── anuncios/                  ← los anuncios que se generan con esos estilos
├── herramientas/
│   └── editor-posteos.html    ← el editor: armás el posteo y descargás el PNG
├── conocimiento/
│   ├── charley-t/
│   │   ├── estaticos.md            ← lo del método que aplica a estáticos
│   │   ├── marcos-principales.md   ← el método completo, resumido
│   │   ├── top-50-aprendizaje.md   ← los 50 videos con más para aprender
│   │   ├── videos-ultimos-100.md   ← lista de los 100 videos con links
│   │   ├── transcripciones/        ← texto crudo de cada video
│   │   └── resumenes/              ← un resumen por video
│   └── otros/                 ← cualquier otra fuente que quieras sumar
└── scripts/                   ← analizar_anuncio, ajustar_fuente, bajar_fuente, render_anuncio,
                                  comparar y descargar_transcripciones
```

## Guardar un estilo y usarlo

Pasale a Claude un anuncio que te guste y un nombre:

> "Analizá este anuncio y guardalo como **estilo oro**."

Claude le saca la tipografía, los tamaños, los colores, la distribución, el tratamiento de las
fotos y la forma de escribir, y lo replica hasta que quede igual al original. Después:

> "Hacé un anuncio tipo **oro** para [producto]."

Lo arma con ese estilo y te deja el PNG en `anuncios/`. Detalles en `estilos/README.md`.

## El editor de posteos

Abrí `herramientas/editor-posteos.html` con doble clic (se abre en el navegador, no hace
falta instalar nada ni tener internet).

1. Elegí el tipo: **Foto + texto**, **Reseña** o **Texto grande**.
2. Escribí los textos, cargá tus fotos y elegí colores y tipografía.
3. Lo que ves es exactamente lo que se descarga. Apretá **Descargar PNG**.

El agente te dice qué textos y qué ajustes cargar para cada concepto.

## Cómo usarlo

**Opción A — Proyecto en claude.ai (lo más fácil).**
Creá un Proyecto, pegá el contenido de `CLAUDE.md` en "Instrucciones" y subí como
archivos del proyecto todo lo de `../negocio/`, `../resultados/` y `conocimiento/`.
Cada chat dentro de ese proyecto ya es el agente.

**Opción B — Claude Code.** Abrí Claude Code dentro de la carpeta `agente-marketing/`.
Lee `CLAUDE.md` solo, y puede leer y **actualizar** los archivos por vos.

## Cómo ir rellenándolo de información

1. **Primero, tu negocio (lo más importante).** Completá los `[COMPLETAR]` de
   `../negocio/`. Si no sabés por dónde empezar, decile al agente:
   *"Entrevistame para completar marca.md y cliente-ideal.md"*.
2. **Cada semana, tus resultados.** Agregá una fila a
   `../resultados/registro-anuncios.md`, o pegale las métricas al agente y pedile que
   escriba la fila. Esto es lo que más lo mejora con el tiempo.
3. **Los videos de Charley T.**
   - En Windows: doble clic en `descargar_transcripciones.bat`. En Mac/Linux:
     `pip install --upgrade youtube-transcript-api` y
     `python scripts/descargar_transcripciones.py` → baja los 50 de `top-50-aprendizaje.md`
     a `transcripciones/` (agregá `videos.csv` al final para los últimos 100). Si YouTube
     bloquea, pegá los links de `top-50-aprendizaje.md` en NotebookLM.
   - Después, en Claude Code: *"Resumí las transcripciones que no tengan resumen usando
     `resumenes/_plantilla.md`, marcalas con ✅ en `videos-ultimos-100.md` y actualizá
     `marcos-principales.md` con lo nuevo"*.
   - Para videos nuevos del canal: agregá la fila en `videos.csv` y repetí.
4. **Otras fuentes.** Cualquier curso, artículo o anuncio que te guste → un `.md` en
   `conocimiento/otros/`.
5. **Al final de cada charla**, el agente te propone qué guardar. Aceptalo (o copialo
   al archivo) y queda aprendido.

Regla de oro: si un dato no está en un archivo, el agente no lo recuerda la próxima vez.

## Pedidos de ejemplo

- "Dame 6 conceptos creativos distintos (anillos olímpicos) para el producto X."
- "Escribí un anuncio 3:2:2: 3 ideas de creativo, 2 textos y 2 titulares."
- "Guion de 30 segundos tipo UGC con gancho fuerte para la persona 1."
- "Te paso los números de la semana: ¿qué corto, qué escalo y qué pruebo?"
- "Armame la estructura de campañas para $20 por día."
