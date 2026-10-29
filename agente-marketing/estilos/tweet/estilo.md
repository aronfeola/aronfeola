# Estilo «tweet»

> Posteo estilo captura de red social sobre fondo crema: título arriba, una o dos fotos con
> esquinas redondeadas, perfil (foto, nombre y usuario) y un texto corto en broma con emojis.

- **Guardado:** 2026-10-29 · **Referencia:** `referencia.png` (la tarjeta enderezada del video de
  TikTok que mandó el dueño). Capturas originales: `referencia-original-en.png` (el posteo en
  inglés) y `referencia-original-es.png` (la versión en español que arma la app del video).
- **Cuándo usarlo:** mostrar un producto con humor y con pinta de "contenido de redes", no de
  anuncio. Funciona para anillos 1–3 (público frío) del método de Charley T.
- **Parecido con la referencia:** las medidas coinciden a 1–4 px (título, fotos, perfil, texto).
  Queda ~12% de píxeles distintos por las fotos (la referencia es una foto de una pantalla, más
  borrosa) y el viñeteado del fondo. Ver `comparacion.png`.

## Lienzo
Pensado para 1080 × 1350 (4:5, el formato recomendado). La referencia mide 1080 × 1300. Funciona
también en 1:1 y 9:16: las fotos absorben la diferencia de alto.

## Colores
| Rol | Color | Dónde se usa |
|---|---|---|
| Fondo | `#ecead4` | todo el lienzo (crema algo verdoso) |
| Texto | `#0f0f0c` | título, nombre y texto de abajo (casi negro) |
| Apagado | `#77766a` | usuario (@…) |
| Avatar vacío | `#d9dccb` | círculo de perfil cuando no hay foto |
| Leyenda sobre foto | blanco con contorno negro | texto encima de la foto |

## Tipografía
Todo en **Inter**.

| Rol | Peso | Tamaño | Interlineado | Color |
|---|---|---|---|---|
| Título | 400 | 42 px | 1,2 | texto |
| Nombre | 700 | 38 px | 1,15 | texto |
| Usuario | 400 | 38 px | 1,15 | apagado |
| Texto de abajo | 500 | 42 px | 1,25 | texto |
| Leyenda sobre la foto | 800 | 42 px | 1,15 | blanco, contorno negro 9 px |

**Cómo se identificó:** la referencia es una foto de pantalla, borrosa. Con `ajustar_fuente.py`,
sumando las tres líneas de texto, varias sans quedaron casi empatadas (Inter, Manrope, Figtree,
DM Sans, Roboto). Se eligió Inter por ser la más estándar y de las mejores en el total. **No se
puede asegurar cuál es la original.** El peso (título 400, texto 500) se eligió comparando.

## Distribución (de arriba hacia abajo, 1080 de ancho)
1. Mucho aire arriba: el título arranca recién a ~145 px.
2. **Título**, pegado a la izquierda, 1 o 2 líneas.
3. **Fotos**: de margen a margen (19 px), a 60 px debajo del título. Una sola, o dos lado a lado con
   13 px de separación. Esquinas de 22 px. Ocupan todo el alto que sobra.
4. **Perfil**, 60 px debajo: círculo de 115 px, y al lado el nombre (negrita) y el usuario (gris).
5. **Texto de abajo**, 60 px debajo del perfil, 1 o 2 líneas, con 3 emojis repetidos al final.
6. Margen inferior de 28 px.

## Fotos
Esquinas redondeadas de 22 px, sin borde ni sombra. Fotos "de la vida real": ambiente cálido y
oscuro, producto en la mano o sobre una mesa. En la referencia, dos vistas del mismo objeto.

## Detalles
- **Leyenda sobre la foto** (opcional, la usa la versión de la app): texto blanco grueso centrado,
  abajo de la foto, con contorno oscuro, como el subtítulo de un video.
- **Perfil:** logo de la marca (círculo). Sin logo queda un círculo gris claro.
- Sin íconos, sin botones, sin números de likes.

## Cómo se escribe
Es una **fórmula de meme de redes**:
1. **Título** que afirma algo y se ve en la foto: "Así se ve el oro en 2026", "Así se ve un florero
   impreso en 3D". Una frase de 4 a 8 palabras.
2. **Prueba visual**: la foto.
3. **Texto de abajo** en broma: una cifra o dato exagerado con signos de pregunta, y un remate.
   "4TB??? Rich millionaire", "2TB??? Viejo millonario". Después, **3 emojis iguales** (😆😆😆).
- **Tono:** casual, de usuario, no de marca. **Idioma:** español rioplatense. **Mayúsculas:** como
  en una frase normal. **Nada de precios ni "oferta" en el título.**
- **Originales:** «This is what gold looks like in 2026» / «4TB??? Rich millionaire 😝😝😝» y, en la
  versión en español de la app, «Así se ve el oro en 2026» / «Hub + 2tb de alta velocidad 😍»
  (leyenda) / «2TB??? Viejo millonario 😝😝😝».

## Reglas
- No cambiar el fondo crema, la tipografía ni la disposición.
- Cambian en cada anuncio: título, fotos (1 o 2), leyenda (opcional), nombre, usuario, logo y texto.
- El perfil debe ser el de la marca del dueño, no el de otra cuenta.
- Emojis iguales y juntos (el script los mantiene en la misma línea).

## Huecos para el contenido
| Hueco | Qué va | Obligatorio | Largo recomendado |
|---|---|---|---|
| `titulo` | frase principal | sí | 1–2 líneas, ≤ 45 caracteres |
| `foto1` | primera foto | sí | vertical si hay 2 fotos; apaisada si hay 1 |
| `foto2` | segunda foto | no | vertical |
| `leyenda` | texto sobre la foto | no | ≤ 36 caracteres |
| `avatar` | logo de la marca | no | cuadrado |
| `nombre` | nombre de la marca | sí | ≤ 24 caracteres |
| `usuario` | @usuario | sí | ≤ 22 caracteres |
| `texto` | texto de abajo | sí | 1–2 líneas, ≤ 60 caracteres |

## Diferencias conocidas con la referencia
- La referencia es una **foto de una pantalla**: los colores pueden estar corridos (el crema se ve
  verdoso) y el texto se ve más pesado y borroso que el nuestro, que sale nítido.
- Los emojis salen con la tipografía de emojis del sistema donde se genere; no son idénticos a los
  de la captura original.
- La referencia tiene un borde claro finito alrededor de las fotos que no se replicó.
- La tipografía exacta no se pudo determinar (ver arriba).

## Cómo generar un anuncio
```
node scripts/render_anuncio.js tweet anuncios/mi-anuncio.json anuncios/mi-anuncio.png
```
(Desde la carpeta `agente-marketing`.) Ejemplos listos: `anuncios/2026-10-29-tweet-florero-2fotos.json`
y `…-1foto.json`.
