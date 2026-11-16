# Soporte de kit de mate para el auto, versión 2 (CLEAMS)

## Archivos

| Archivo | Qué es |
|---|---|
| `rectangular_A_1termo_1mate_1yerbero.stl` | Caja rectangular, 1 termo, 1 mate, 1 yerbero, bombilla |
| `rectangular_B_2termos_1mate_1yerbero.stl` | Caja rectangular, 2 termos, 1 mate, 1 yerbero, bombilla |
| `redondeado_A_1termo_1mate_1yerbero.stl` | Misma A con esquinas redondeadas (R 40 mm) |
| `redondeado_B_2termos_1mate_1yerbero.stl` | Misma B con esquinas redondeadas (R 40 mm) |
| `gancho_v2_imprimir_x2.stl` | Gancho para el apoyacabezas, imprimir 2 unidades |
| `generar_v2.py` | Generador paramétrico de todas las piezas |

Todas las piezas son una sola pieza, cerradas (watertight), listas para laminar.

## Peso y medidas

| Pieza | Peso impreso | Medidas (mm) | Profundidad de bolsillos |
|---|---|---|---|
| Caja A rectangular | 699 g | 214 × 208 × 83 | termo 78, yerbero 58, mate 48 |
| Caja B rectangular | 692 g | 220 × 226 × 73 | termo 68, yerbero 50, mate 41 |
| Caja A redondeada | 675 g | 214 × 208 × 83 | igual que A |
| Caja B redondeada | 671 g | 220 × 226 × 73 | igual que B |
| Gancho (cada uno) | 34 g | 130 × 70 × 30 | |

Paredes exteriores de 4 mm sólidas, piso de 5 mm bajo cada bolsillo, placa trasera de 12 mm con el riel en T.
Los bolsillos están dimensionados para un termo de hasta 96 mm de diámetro, un mate de 88 mm y un yerbero de 106 mm.
Hay que medir los tuyos antes de imprimir.

## Logo

El logo CLEAMS va en relieve de 1,2 mm en el frente, abajo a la derecha, visto de frente. Tiene 12 mm de alto y usa el mismo material que la pieza.

## Perfil de impresión (PETG Hyper)

- Temperatura de boquilla y de cama: la del perfil normal de tu PETG Hyper, sin subir nada.
- Ventilador de pieza: 10 % como máximo. En la primera capa, 0 %.
- Altura de capa 0,2 mm. 4 perímetros. Relleno gyroid 10 %.
- Capas superiores e inferiores: 5 de cada una.
- Sin soportes en la caja. El gancho se imprime de canto, sin soportes.
- Retracción y velocidad de viaje ajustadas para PETG, para que no se formen hilos.
- Secar el filamento antes: 6 horas a 65 °C si el rollo estuvo expuesto.

## Costo y tiempo (estimación)

| Concepto | Modelo A | Modelo B |
|---|---|---|
| Filamento total (caja + 2 ganchos) | 767 g | 760 g |
| Costo de filamento a ARS 22.000 a 36.000 por kg | ARS 17.000 a 28.000 | ARS 17.000 a 27.000 |
| Tiempo en P2S (estimación) | 17 a 21 h | 17 a 21 h |

El costo de filamento es un rango de precio de PETG en Argentina. Los tiempos son una estimación a partir del volumen y pueden variar según el perfil.

## Los ganchos: la preocupación real

El punto débil no es la caja. Es la unión entre el gancho y el riel, y el momento que genera el peso al tirar hacia atrás.

Estimación con dos termos llenos, un mate con yerba y agua, y un yerbero con yerba:

- Peso del contenido: unos 4,3 kg para la B y unos 2,7 kg para la A, sumando la caja.
- Frenada fuerte o pozo, con 5 g de aceleración: unos 105 N por gancho en B.
- Momento en la base de la tira (tira de 30 × 12 mm): unos 7 MPa.
- Límite de PETG a tracción: unos 50 MPa. El factor de seguridad queda en torno a 5 o más.

Con esos números la tira no debería romperse. Los riesgos reales son otros:

- **Capas (interlaminar):** si el gancho se imprime en otra orientación, las capas quedan en la dirección de la carga. Por eso se imprime de canto, con la tira a lo largo de X.
- **Que el pie se salga del riel:** un tope en el extremo del riel evita que la caja se deslice.
- **Inclinación:** el peso tiende a inclinar la caja hacia afuera del respaldo. El riel lo resiste, pero si los postes del apoyacabezas no son paralelos, la carga se concentra en un gancho.

Recomendación para que llegue sobrado:

1. Usar la versión B solo si el auto tiene postes de apoyacabezas de al menos 10 mm de diámetro.
2. Antes de usarlo, probar cada gancho con 10 kg colgados durante 10 minutos. Si no se deforma, va bien.
3. Si quieres más margen, agregar una correa inferior que una la base de la caja con el asiento. Puedo hacerla en una versión 3.

Estos cálculos son estimaciones. El PETG impreso varía según el perfil y la humedad del filamento. La prueba de carga es la única verificación confiable.
