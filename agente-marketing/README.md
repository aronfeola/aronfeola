# Agente creativo y de marketing (Meta Ads, método Charley T)

Un agente que funciona como tu director creativo: arma conceptos de anuncios, guiones,
copys, estructura de campañas y lee resultados. Aprende de dos cosas:

1. **Tu negocio** → carpeta `negocio/` y `resultados/`
2. **El método** → carpeta `conocimiento/` (arranca con Charley T / @ctthedisrupter)

```
agente-marketing/
├── CLAUDE.md                  ← las instrucciones del agente (su "personalidad")
├── negocio/                   ← marca, cliente ideal, oferta, competencia
├── resultados/
│   └── registro-anuncios.md   ← qué probaste y qué funcionó
├── conocimiento/
│   ├── charley-t/
│   │   ├── marcos-principales.md   ← el método, resumido
│   │   ├── videos-ultimos-100.md   ← lista de los 100 videos con links
│   │   ├── transcripciones/        ← texto crudo de cada video
│   │   └── resumenes/              ← un resumen por video
│   └── otros/                 ← cualquier otra fuente que quieras sumar
└── scripts/descargar_transcripciones.py
```

## Cómo usarlo

**Opción A — Proyecto en claude.ai (lo más fácil).**
Creá un Proyecto, pegá el contenido de `CLAUDE.md` en "Instrucciones" y subí como
archivos del proyecto todo lo de `negocio/`, `resultados/` y `conocimiento/`.
Cada chat dentro de ese proyecto ya es el agente.

**Opción B — Claude Code.** Abrí Claude Code dentro de la carpeta `agente-marketing/`.
Lee `CLAUDE.md` solo, y puede leer y **actualizar** los archivos por vos.

## Cómo ir rellenándolo de información

1. **Primero, tu negocio (lo más importante).** Completá los `[COMPLETAR]` de
   `negocio/`. Si no sabés por dónde empezar, decile al agente:
   *"Entrevistame para completar marca.md y cliente-ideal.md"*.
2. **Cada semana, tus resultados.** Agregá una fila a
   `resultados/registro-anuncios.md`, o pegale las métricas al agente y pedile que
   escriba la fila. Esto es lo que más lo mejora con el tiempo.
3. **Los videos de Charley T.**
   - En tu compu: `pip install youtube-transcript-api` y
     `python scripts/descargar_transcripciones.py` → se llena `transcripciones/`.
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
