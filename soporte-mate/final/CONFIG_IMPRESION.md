# Configuración de impresión por pieza (CLEAMS, PETG Hyper)

Pegá cada bloque en Claude Code. Son los mismos ajustes para todas las piezas salvo lo que está marcado.

## Ajustes comunes a todas
- Material: PETG Hyper. Temperatura de boquilla y cama: perfil normal del filamento, sin subir.
- Boquilla 0,4 mm. Altura de capa 0,2 mm (primera capa 0,28 mm).
- Ventilador de pieza: 10 % como máximo. 0 % en las primeras 3 capas.
- Sin soportes.
- Filamento seco: 6 horas a 65 °C antes de imprimir.
- Velocidad de perímetro exterior: 50 a 60 mm/s.

## 1. Caja sola (`set_CAJA_sola.stl`)
- Cama: 220 × 220 mm mínimo, sin falda ni borde. Peso aprox. 652 g.
- Perímetros: 5.
- Relleno: 8 % gyroid.
- Capas superiores: 6. Capas inferiores: 5.
- Orientación: la pieza tal como está en el archivo (piso sobre la cama, cuña atrás).
- Costura de inicio: en la espalda, lejos del logo.

## 2. Accesorios por separado (`set_ACCESORIOS_separados.stl`)
Esta hoja trae varias piezas. Configurá cada una según la tabla:

| Pieza | Cantidad | Perímetros | Relleno | Borde (brim) | Peso aprox. |
|---|---|---|---|---|---|
| Gancho para apoyacabezas | 2 | 6 | 40 % gyroid | 5 mm | 102 g c/u |
| Tope del riel | 4 | 4 | 40 % | 0 | 2 g c/u |
| Tapa del mate | 1 | 5 | 15 % gyroid | 0 | 97 g |
| Retenedor del mate | 1 | 4 | 15 % | 0 | 66 g |
| Adaptador de termo chico | 1 por termo chico | 4 | 15 % | 0 | 100 g c/u |

- Ganchos: de canto, como están en el archivo, con borde de 5 mm.
- Tapa: va con el tapón hacia abajo (como está en el archivo).

## 3. Todo junto (`set_TODO_JUNTO.stl`)
Este archivo tiene la caja y los accesorios sobre una misma hoja, con 730 mm de ancho.
La cama de la P2S es de 256 mm, así que no entra en una sola impresión.
Dividí en varias tandas: caja sola en una tanda, y los accesorios en otra. Usá el archivo solo para ver el conjunto.

## Orden recomendado
1. Piezas de prueba (riel y aro de 88 mm).
2. Ganchos y topes.
3. Tapa, retenedor y adaptador.
4. Caja.
