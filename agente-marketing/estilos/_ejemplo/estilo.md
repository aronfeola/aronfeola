# Estilo «_ejemplo»

> Oscuro y de alto impacto: titular amarillo en mayúsculas condensadas, foto con esquinas
> redondeadas, sello circular y botón de ancho completo.

**⚠️ Este es un estilo de PRUEBA, hecho con un anuncio inventado para probar las herramientas.
No viene de un anuncio real tuyo.** Sirve para ver cómo queda un estilo terminado.

- **Guardado:** 2026-10-29 · **Referencia:** `referencia.png` (anuncio inventado)
- **Cuándo usarlo:** ofertas directas con un producto estrella y un dato fuerte (plazo, descuento, mínimo).
- **Parecido con la referencia:** 0,00% de píxeles distintos (ver `comparacion.png`).

## Lienzo
1080 × 1350 (4:5). Funciona también en 1:1 (queda menos foto y menos aire entre titular y foto) y en
9:16 (la foto se estira).

## Colores
| Rol | Color | Dónde se usa |
|---|---|---|
| Fondo | `#101012` | todo el lienzo |
| Acento | `#ffd400` | titular, sello, botón |
| Texto | `#f2f0ea` | subtítulo |
| Sobre acento | `#101012` | texto dentro del sello y del botón |

## Tipografía
| Rol | Familia | Peso | Tamaño | Mayúsculas | Interlineado | Espaciado | Color | Alineación |
|---|---|---|---|---|---|---|---|---|
| Titular | Anton | 400 | 148 px | sí | 0,95 | 1 px | acento | izquierda |
| Subtítulo | Inter | 500 | 38 px | no | 1,3 | 0 | texto | izquierda |
| Sello | Inter | 800 | 40 px | sí | 1,05 | 0 | sobre acento | centrada |
| Botón | Anton | 400 | 56 px | sí | — | 2 px | sobre acento | centrada |

**Cómo se identificó:** `ajustar_fuente.py` dio Anton con 0,8% de error en el titular (Bebas Neue
quedó segunda, con 3,1%: es muy parecida). Inter 500 para el subtítulo (2,6%).

## Distribución (de arriba hacia abajo, 4:5)
1. Titular en 2 líneas, margen izquierdo 72 px, desde y = 64.
2. Foto de 936 px de ancho (de margen a margen), desde y = 534, esquinas de 36 px. Ocupa todo el
   alto que sobra.
3. Sello circular de 210 px, pegado arriba a la derecha de la foto, sobresaliendo 72 px por arriba.
4. Subtítulo de una línea, a 30 px debajo de la foto.
5. Botón de ancho completo (936 × 112 px), esquinas de 20 px, a 36 px debajo del subtítulo.
6. Margen inferior: 68 px.

## Fotos
Esquinas de 36 px, sin borde ni sombra ni filtro. Producto centrado sobre fondo de color. Recorte
con `cover`.

## Detalles
Sello circular amarillo superpuesto a la foto (dato corto en 2 líneas, mayúsculas).

## Cómo se escribe
- **Titular:** 2 líneas de 2 a 4 palabras ("Regalos con / tu logo en 3D"). Mayúsculas automáticas.
- **Tono:** directo, de oferta. **Idioma:** español rioplatense. **Emojis:** no.
- **Sello:** dato de 2 líneas cortas ("10 días / hábiles").
- **Botón:** verbo + beneficio ("Pedí tu presupuesto").

## Reglas
- No cambiar los colores ni la tipografía.
- Cambian en cada anuncio: titular, foto, sello (opcional), subtítulo (opcional) y botón.
- Si el titular pasa de ~3 líneas la letra se achica y se lee peor: acortarlo.

## Huecos para el contenido
| Hueco | Qué va | Obligatorio | Largo recomendado |
|---|---|---|---|
| `titular` | frase principal | sí | 2 líneas, ≤ 28 caracteres por línea |
| `foto` → `producto` | foto del producto | sí | horizontal, producto centrado |
| `sello` | dato corto | no | 2 líneas, ≤ 10 caracteres cada una |
| `subtitulo` | aclaración | no | 1 línea, ≤ 40 caracteres |
| `cta` | llamado a la acción | sí | ≤ 22 caracteres |

## Diferencias conocidas con la referencia
Ninguna visible (0,00% de píxeles distintos).

## Cómo generar un anuncio
```
node scripts/render_anuncio.js _ejemplo estilos/_ejemplo/contenido-nuevo.json anuncios/mi-anuncio.png
```
(Se corre desde la carpeta `agente-marketing`.) Agregá `--ratio 1:1` o `--ratio 9:16` para otros formatos.
