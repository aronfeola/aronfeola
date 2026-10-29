# Biblioteca de estilos de anuncio

Acá se guardan los estilos que Claude le saca a anuncios de referencia. Un estilo guarda
**todo lo visual** (tipografía, tamaños, colores, distribución, tratamiento de fotos,
detalles) y cómo está escrito el texto, para repetirlo con otro contenido.

## Cómo se usa

**1. Guardar un estilo.** Pasale a Claude el anuncio (adjuntá la imagen) y decile el
nombre:

> "Analizá este anuncio y guardalo como **estilo oro**."

Claude lo mide, baja las tipografías parecidas, arma una plantilla que lo replica, la
compara con el original hasta que quede igual, y te muestra las dos imágenes. Si
algo no coincide, se lo decís y lo corrige.

**2. Usar un estilo.**

> "Hacé un anuncio tipo **oro** para [producto]. Titular: …"

Si no le das el texto o la foto, Claude los propone (con los datos del negocio y
`conocimiento/charley-t/estaticos.md`) y te pregunta. El PNG queda en `anuncios/`.

**3. Ver los estilos guardados:** pedile "mostrame los estilos".

**4. Corregir un estilo:** "en el estilo oro el titular va más grande". Lo ajusta y vuelve a compararlo
con la referencia.

Los anuncios que se generan quedan en `anuncios/`, con el archivo de texto que se usó, para poder repetirlos.

**Una regla:** el estilo es el diseño, no la marca. Claude no copia logos, nombres de marca ni
textos de otras marcas.

## Qué necesita

Las sesiones de Claude en la nube ya traen todo. Si lo corrés en tu compu:
`pip install pillow numpy` y `npm i playwright && npx playwright install chromium`. Los
comandos se corren desde la carpeta `agente-marketing/`.

## Qué hay en cada carpeta

```
estilos/
├── README.md
├── _plantilla/        ← punto de partida para estilos nuevos (no es un estilo)
├── _fuentes/          ← tipografías descargadas (las comparten todos los estilos)
└── <nombre>/
    ├── estilo.md      ← el estilo explicado: qué es, medidas, reglas, cómo escribe
    ├── estilo.json    ← los mismos valores, ordenados
    ├── plantilla.html ← la réplica exacta; es lo que genera los anuncios
    ├── referencia.png ← el anuncio original
    ├── analisis.png   ← el original con una grilla y cada elemento marcado
    ├── replica.png    ← la plantilla generada con el texto del original
    └── comparacion.png← referencia | réplica | diferencias
```

## Estilos guardados

| Nombre | Qué es | Tamaño | Referencia |
|---|---|---|---|
| `tweet` | Posteo estilo captura de red social: fondo crema, título, 1 o 2 fotos redondeadas, perfil y texto en broma con emojis. Sacado del video que mandó el dueño. | 4:5 (también 1:1 y 9:16) | `tweet/referencia.png` |
| `_ejemplo` | **De prueba, con un anuncio inventado.** Sirve para ver cómo queda un estilo terminado (titular amarillo condensado, foto redondeada, sello y botón). | 4:5 (también 1:1 y 9:16) | `_ejemplo/referencia.png` |

*(Claude agrega una fila acá cada vez que guarda un estilo nuevo.)*

## Tipografías

Claude no puede "leer" el nombre de una tipografía de una imagen: elige la de Google
Fonts que más se le parece (se compara a ojo y con `comparar.py`). Las más usadas en
anuncios: Inter, Montserrat, Poppins, Archivo Black, Anton, Bebas Neue, Oswald,
League Spartan, Barlow Condensed, Playfair Display, DM Serif Display, Lora, Caveat. Si
conocés el nombre real de la tipografía del anuncio, decíselo.
