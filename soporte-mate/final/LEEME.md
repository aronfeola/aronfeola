# Set final: caja A + accesorios (CLEAMS)

Esta carpeta reemplaza a todas las versiones anteriores. Los ganchos y topes viejos (v2 a v5) NO sirven con esta caja: el riel cambió.

## Qué cambió en la revisión

1. **Riel en cuña a 45°.** El riel anterior era una ranura recta y nada impedía que la caja se saliera hacia adelante. Ahora el pie del gancho es una cuña: el peso traba la caja contra el gancho. Verificado en el modelo: asienta sin interferencia y no sale tirando ni levantando 5 mm. Solo sale deslizando de costado, y para eso están los topes. Ver `corte_encastre.png`.
2. **Gancho con cabeza cuadrada.** Apoya plano en la cama (la anilla redonda apoyaba en una línea) y tiene más material alrededor del poste.
3. **Peso bien calculado.** El estimador anterior contaba de más (un 15 %). Con el margen recuperado la caja pasa de 4 a 5 perímetros.
4. **Logo a 0,8 mm de relieve** en vez de 1,2: sale más limpio sin soportes.

## Piezas y ajustes (Creality Print, PETG Hyper, boquilla 0,4)

| Archivo | Cant. | Perímetros | Relleno | Peso estimado |
|---|---|---|---|---|
| `caja_A.stl` | 1 | 5 | 8 % gyroid | 658 g |
| `gancho_x2.stl` | 2 | 6 | 40 % gyroid | 107 g c/u |
| `tope_riel_x4.stl` | 4 | 4 | 40 % | 2 g c/u |
| `tapa_mate.stl` | 1 | 5 | 15 % gyroid | 97 g (174 g al 40 %) |
| `retenedor_mate.stl` | 1 | 4 | 15 % | 66 g |
| `adaptador_termo_chico.stl` | 1 | 4 | 15 % | 100 g |

Total: unos 1.145 g. La caja sola queda bajo los 700 g.
La tapa y el retenedor ocupan el mismo bolsillo: la tapa va cuando no llevás el mate puesto, el retenedor cuando sí.

Ajustes comunes:
- Capa 0,2 mm (primera 0,28). Temperaturas del perfil normal del PETG Hyper. Ventilador 10 % o menos, 0 % en las 3 primeras capas.
- Caja: 6 capas superiores y 5 inferiores. La sensación de solidez sale de los 5 perímetros y las tapas gruesas, no del relleno.
- Costura alineada atrás (en la caja queda en la espalda, lejos del logo).
- Pared exterior lenta (50 a 60 mm/s) para que el acanalado y el logo salgan limpios.
- Sin soportes en ninguna pieza. La cuña y los ganchos están a 45°.
- Para los hilos: filamento seco (6 h a 65 °C), retracción del perfil y "evitar cruzar perímetros" activado.
- Ganchos y topes: de canto como vienen en el archivo, con borde (brim) de 5 mm.

## Orden de impresión recomendado

1. `prueba_1_cuna_riel.stl` (un tramo de 30 mm del riel) y un tope. Probá que el tope entre a presión y que el gancho deslice. 20 minutos y pocos gramos, antes de arriesgar la caja entera.
2. `prueba_2_aro_bolsillo_mate.stl` (aro de 88 mm) si vas a imprimir la tapa: probá la tapa en el aro.
3. Ganchos y topes en una misma cama.
4. Caja. Mide 214 × 208 mm: necesita cama de 220 × 220 o más, sin falda ni borde.
5. Tapa, retenedor y adaptador.

Si el tope o la tapa quedan flojos o duros, se corrige la holgura en `generar_final.py` (topes) o `generar_tapa_nervada_v7.py` (tapa).

## Pendiente de verificar por vos

- Diámetro de tu termo (bolsillo de 96 mm), mate (88 mm) y yerbero (106 mm).
- Diámetro de los postes del apoyacabezas: el agujero del gancho es de 17 mm.
- Prueba de carga: 10 kg colgados de cada gancho durante 10 minutos antes de usar.
Los pesos son estimaciones; el laminador da el número real.
