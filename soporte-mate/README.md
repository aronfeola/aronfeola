# Soporte de kit de mate para el auto (impresión 3D)

Dos modelos listos para imprimir, inspirados en el organizador de apoyacabezas que pasaste.
Cuelgan de las varillas del apoyacabezas con dos ganchos que entran de costado en un riel
en la cara trasera del cuerpo (así se ajustan a cualquier distancia entre varillas).

| Archivo | Qué es |
|---|---|
| `modelo_A_1termo_1mate_1yerbero.stl` | Cuerpo A: 1 termo + 1 mate + 1 yerbero + bombilla |
| `modelo_B_2termos_1mate_1yerbero.stl` | Cuerpo B: 2 termos + 1 mate + 1 yerbero + bombilla |
| `gancho_apoyacabezas_imprimir_x2.stl` | Gancho para las varillas (imprimir 2 por soporte) |
| `*.png` | Vistas de cada pieza |
| `generar_modelos.py` | Script paramétrico (Python + manifold3d + shapely) para cambiar medidas |

## Medidas de los bolsillos

| Bolsillo | Diámetro | Profundidad | Para qué entra |
|---|---|---|---|
| Termo | 96 mm | 115 mm | Termo de 1 L (Stanley, Lumilagro, etc., cuerpo de 85 a 92 mm) |
| Mate | 88 mm | 70 mm | Mate calabaza, camionero o imperial de hasta 82 mm |
| Yerbero | 106 mm | 85 mm | Lata o yerbero redondo de hasta 100 mm (500 g) |
| Bombilla | ranura 16 × 34 mm | 95 mm | Cualquier bombilla, con agujero de desagote |

Todos los bolsillos tienen agujero de desagote de 8 mm en el fondo.

## Espesores (versión "bien espesa")

- Pared exterior: 3.5 mm, con acanalado vertical de 1 mm (mínimo 2.5 mm en el fondo del canal).
- Tabiques entre bolsillos: 3 a 4 mm. Piso: 4 mm. Placa trasera con riel: 12 mm.
- Cuerpo A: 213 × 206 × 119 mm. Cuerpo B: 219 × 224 × 119 mm. Caja rectangular maciza con esquinas redondeadas; los huecos se cortan desde arriba (el slicer rellena el bloque al 20 %). Ambos entran en cama de 256 × 256.

## Cómo imprimir (Bambu P2S / X1 / P1, boquilla 0.4)

- Material: **PETG** (el PLA se deforma con el calor del auto). ASA si querés lo mejor contra sol y calor.
- Capa 0.2 mm, **4 paredes**, 20 % gyroid, 5 capas arriba y 5 abajo.
- Sin soportes: el cuerpo va parado como está; el gancho va de canto como viene en el STL (usar brim de 5 mm).
- Textura: el acanalado ya está modelado. Si lo querés aún más rugoso, activar *fuzzy skin* 0.2 mm solo en pared exterior.
- Placa texturada PEI para que la base quede mate.

## Montaje

1. Imprimir el cuerpo y 2 ganchos.
2. Deslizar el pie en T de cada gancho dentro del riel trasero, entrando por los costados del cuerpo. Separarlos a la distancia de las varillas.
3. Sacar el apoyacabezas, pasar los anillos por las varillas (diámetro interno 16 mm) y volver a colocarlo.

## Costo y tiempo estimados (PETG, Noviembre 2026, Argentina)

| | Modelo A (1 termo) | Modelo B (2 termos) |
|---|---|---|
| Filamento cuerpo | ~1.60 kg | ~1.78 kg |
| Filamento 2 ganchos | ~55 g | ~55 g |
| **Filamento total** | **~1.65 kg** | **~1.85 kg** |
| Material (ARS 22.000 a 36.000 el kg) | ARS 36.000 a 60.000 | ARS 41.000 a 67.000 |
| Luz + margen de fallas (15 %) | ARS 6.000 a 9.000 | ARS 7.000 a 10.000 |
| **Costo total haciéndolo vos** | **ARS 42.000 a 69.000** | **ARS 48.000 a 77.000** |
| Precio aproximado en un servicio de impresión | ARS 120.000 a 180.000 | ARS 140.000 a 210.000 |
| Tiempo en Bambu P2S / X1 (0.2 mm) | 38 a 44 h | 43 a 50 h |
| Tiempo en impresora lenta (Ender 3) | 95 a 115 h | 110 a 130 h |

Peso cargado aproximado: Modelo A 3.1 kg, Modelo B 4.3 kg. Para el B conviene agregar una correa
inferior al asiento para que no se hamaque al frenar.

## Variante más liviana

Si querés bajar un 25 a 30 % de material y tiempo: paredes de 2.5 mm, 3 perímetros y 15 % de relleno
(cambiar `WALL`, y en el slicer las paredes). Sigue siendo rígido, pero se siente menos "macizo".
