# Accesorios v3: ganchos, tapa del mate, adaptador de termo y topes

| Archivo | Cantidad | Peso impreso | Para qué |
|---|---|---|---|
| `gancho_v3_imprimir_x2.stl` | 2 | 34 g c/u | Gancho reforzado, con refuerzo triangular de 16 mm en la unión tira-brazo |
| `tapa_mate.stl` | 1 | 25 g | Tapa que entra en el bolsillo del mate y evita que se derrame la yerba |
| `adaptador_termo_chico.stl` | 1 por termo chico | 101 g | Manga que entra en el bolsillo de 96 mm y centra un termo de Ø 70 a 72 mm |
| `tope_riel_imprimir_x4.stl` | 4 | 1 g c/u | Topes en los extremos del riel para que el gancho no se salga |

Todas las piezas son watertight y de una sola pieza. Se generan con `generar_v3_accesorios.py`.

## Perfil de impresión
Mismo perfil que la versión 2: PETG Hyper a temperatura normal, ventilador de pieza al 10 % o menos, 4 perímetros, relleno gyroid 10 %, sin soportes.
El gancho va de canto, con la tira a lo largo de X, para que la carga caiga en el sentido de las capas.

## Cómo se usa
1. Deslizá cada gancho por el riel desde un extremo, con la anilla hacia afuera.
2. Insertá un tope en cada extremo del riel, al lado de cada gancho. Entra a presión y no se mueve en marcha.
3. Colocá el adaptador en el bolsillo del termo grande si el termo es chico.
4. Cuando no hay mate en el bolsillo, poné la tapa para que la yerba no se salga.

## Notas
- La tapa tiene 0,6 mm de holgura por lado en un bolsillo de 88 mm. Si la tapa queda muy ajustada, reducí la holgura en el script.
- El adaptador deja el termo chico centrado con costillas de 3 mm. Si tu termo chico tiene más de 72 mm de diámetro, no entra.
