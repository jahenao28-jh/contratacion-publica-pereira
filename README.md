# Proyecto de Minería de Datos — Contratación Pública Pereira

> **Entrega final:** [`reports/informe_final.pdf`](reports/informe_final.pdf) (resumen ejecutivo, producto analítico, recorrido de las 8 unidades y ficha de limitaciones y ética) y el [notebook completo](notebooks/01_ingesta.ipynb), ejecutado con todas sus salidas.

## Problema

¿Qué procesos de contratación de la Alcaldía de Pereira registrados en SECOP II entre 2022 y 2025 presentan señales de concentración en proveedores o montos atípicos, para que la Oficina de Control Interno priorice cuáles revisar primero?

## Integrantes

- William Torres Valencia
- Jhon Alexander Duque Buritica
- Jorge Alberto Henao Vergel

## Fuentes de datos

| # | Fuente | Identificador | Uso en el proyecto |
|---|---|---|---|
| 1 | [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/about_data) (datos.gov.co) | `jbjy-vk9h` | Contratos de la Alcaldía de Pereira 2020-2026: proveedor, valor, fechas y modalidad. Exportados en dos archivos por periodo (2020-2023 y 2024-2026) para comparar administraciones. |
| 2 | [SECOP II - Procesos de Contratación](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt/about_data) (datos.gov.co) | `p6dx-8zbt` | Procesos del Municipio de Pereira (NIT 891480030), descargados de la API de datos.gov.co con `src/descargar_procesos.py`: dependencia que contrata, precio base y número de oferentes. |

## Estructura del repositorio

- `/data/raw` — Datos originales sin modificar de las dos fuentes (ver "Cómo reproducir")
- `/data/processed` — Datos limpios y transformados
- `/notebooks` — Notebook único del proyecto
  - `01_ingesta.ipynb` — Corte 1 (secciones 1 a 10): lectura de las dos fuentes, cruce Contratos ↔ Procesos, verificación de filas y diccionario de datos. Checkpoint 1 (secciones 11 a 13): calidad de datos, análisis exploratorio, ingeniería de características y pipeline. Unidades 5 a 8 (secciones 14 a 17): segmentación, modelo predictivo, detección de anomalías e integración en una lista de revisión
- `/src` — Scripts de Python reutilizables
  - `descargar_procesos.py` — Descarga los procesos de Pereira desde la API de SECOP II
  - `generar_informe.py` — Genera `reports/informe_final.pdf` a partir de los resultados que exporta el notebook
- `/reports` — Informe final, lista de revisión 2022-2025, vigilancia de 2026 y cifras clave (`metricas_clave.json`)
- `/figures` — Tablero final y gráficos del informe

## Estado actual

**Corte 1 — Adquisición**

- [x] Ficha del proyecto y estructura del repositorio
- [x] Lectura de las fuentes con pandas (`.shape`, `.head()`, `.info()`)
- [x] Unión de los dos periodos de contratos (verificada por `id_contrato`)
- [x] Cruce Contratos ↔ Procesos por `proceso_de_compra` con verificación de filas antes y después
- [x] Diccionario de datos de las 30 columnas del dataset cruzado
- [x] Subconjunto de análisis 2022-2025 alineado con la Ficha

**Corte 2 — Checkpoint 1** (secciones 11 a 13 del notebook)

- [x] Calidad de datos: tipos corregidos y valores atípicos tratados, con la justificación de cada caso
- [x] Análisis exploratorio: estadísticas descriptivas, 6 gráficos e historia de 5 hallazgos
- [x] Ingeniería de características: 6 variables derivadas, codificación one-hot, escalado y las funciones reproducibles `preparar_dataset` y `proceso_completo`, que va de los archivos originales a la matriz final
- [x] Primera lista de contratos a revisar según sus señales de alerta

**Unidades 5 a 8 y proyecto final** (secciones 14 a 17 del notebook)

- [x] Segmentación con k-means: variables y número de grupos elegidos con el codo y la silueta; 4 segmentos
- [x] Modelo predictivo: regresión logística que anticipa qué contratos terminarán adicionados hasta el tope legal, validada en el tiempo y sin fuga de información
- [x] Técnica complementaria: detección de anomalías con Isolation Forest, comparada con las reglas
- [x] Integración: tablero final, lista de revisión 2022-2025, vigilancia de 2026 e informe final en PDF

### Resultados de la adquisición

| Concepto | Valor |
|---|---|
| Contratos 2020-2023 / 2024-2026 | 22.522 / 17.753 (14 columnas, 0 contratos repetidos entre periodos) |
| Contratos unidos | 40.275 |
| Procesos descargados / únicos tras depurar | 43.863 / 40.746 |
| Llave del cruce | `proceso_de_compra` (Contratos) = `id_del_portafolio` (Procesos) |
| Filas antes / después del cruce | 40.275 / 40.275 (`merge` left, `validate="many_to_one"`) |
| Contratos con proceso encontrado | 37.523 (93,2 %) |
| Validación de la llave | Modalidad y tipo de contrato coinciden al 100 % entre fuentes |
| Dataset final | 40.275 filas × 30 columnas |
| Subconjunto 2022-2025 | 24.779 filas |

### Hallazgos del análisis exploratorio (2022-2025)

1. **La competencia casi no actúa como control.** El 95,9 % de los contratos fue por contratación directa, y donde hubo convocatoria, el 35,4 % de los procesos (210 de 594) recibió una sola oferta.
2. **En año electoral, la contratación directa se comprime en enero.** Enero de 2022 (3.297 contratos) y enero de 2026 (3.587) son los dos meses más altos de la serie; en los demás años el pico fue febrero de 2023, con 1.700. Entre marzo y mayo de 2022, con la Ley de Garantías vigente, iniciaron 16.
3. **Pocos proveedores reciben la mitad del dinero.** 16 de 8.600 proveedores reciben el 50 % del valor, y el 1 % de los proveedores, el 73,6 %.
4. **Una dependencia concentra casi todo en un contrato.** En la Secretaría Jurídica el índice HHI es 9.020: HERNÁNDEZ RODAS S.A.S recibe el 95,0 % de su valor con un contrato de 240.380 millones por servicios profesionales de apoyo a la defensa jurídica.
5. **Cientos de contratos crecieron hasta el tope legal.** 724 contratos terminaron valiendo exactamente 1,5 veces su precio base, el máximo de adiciones que permite la ley (50 %), frente a 241 entre 1,45 y 1,4999.

### Resultados de las unidades 5 a 8 (2022-2025)

| Etapa | Resultado |
|---|---|
| Segmentación (k-means, 4 grupos) | 136 «grandes contratos concentrados» (0,6 % de los contratos) reúnen el 56,2 % del dinero |
| Modelo predictivo (regresión logística) | Entrenado con 2022-2023 y probado con 2024: ROC-AUC de 0,852; revisando el 10 % de mayor riesgo encuentra el 43,0 % de los contratos que llegaron al tope, 4,3 veces más que al azar. Con un solo año de entrenamiento no funciona |
| Detección de anomalías (Isolation Forest) | 247 contratos (1 %) con el 67,6 % del valor; complementa las reglas en vez de repetirlas |
| Integración | 305 contratos a revisar (1,2 %) con el 68,1 % del dinero, y 486 contratos de 2026 a vigilar antes de aprobar adiciones |

## Riesgos y hallazgos

- **Procesos repetidos en la fuente 2.** SECOP publica el mismo proceso varias veces (2.450 filas idénticas y una fila por fase en 522 procesos). Cruzar sin depurar inflaba el resultado de 40.275 a 45.384 filas. Se resolvió dejando la última fase publicada de cada proceso y exigiendo `validate="many_to_one"` en el `merge`.
- **Contratos sin proceso publicado.** 2.752 contratos (6,8 %), casi todos de contratación directa y sobre todo desde 2024, no tienen proceso en el dataset `p6dx-8zbt`, ni siquiera buscándolos sin filtrar por entidad. Se conservan marcados con `tiene_proceso = False`.
- **Un valor imposible.** Un contrato cancelado figuraba por 9,1 × 10¹⁵ pesos: exactamente su precio base al cuadrado y 2.571 veces la suma de todos los demás. Sin corregirlo, los 10 mayores proveedores "concentraban" el 100 % del dinero. Se corrigió al precio base.
- **Identificadores y categorías escritos de varias formas.** 118 documentos de proveedor tenían puntos o asteriscos y 35 contratos no tenían documento; el estado mezclaba mayúsculas y minúsculas; las 11 modalidades son 6 y los 20 nombres de dependencia son 17. Todo se unificó en la sección 11.
- **Contratos sin valor real o sin ejecutar.** 154 contratos valen cero o un valor simbólico (0,01, 0,10 o 1 peso) y 10 son borradores o cancelados: quedan fuera del análisis de dinero, y los de servicios o consultoría se marcan como error.
- **Fechas incoherentes.** 3 contratos terminan antes de iniciar: se marcan y su duración queda vacía. Los 2 que inician después de la fecha de corte (29 de septiembre de 2026) son contratos programados, no errores.
- **Montos atípicos.** Se marcan sin borrarlos (509 altos y 664 bajos, comparados con contratos del mismo tipo), porque son justamente lo que Control Interno necesita revisar.

## Cómo reproducir

1. Clonar el repositorio e instalar dependencias: `pip install -r requirements.txt`
2. Los datos de las dos fuentes ya vienen en `data/raw/`, tal como se obtuvieron el 29 de septiembre de 2026:
   - `Vista-_Contratos_Alcaldia_de_Pereira_2020-2023.xlsx` y `Vista-_Contratos_Alcaldia_de_Pereira_2024-2026.xlsx`: contratos exportados del dataset [`jbjy-vk9h`](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/about_data).
   - `procesos_pereira_p6dx-8zbt.csv`: procesos descargados del dataset [`p6dx-8zbt`](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt/about_data) con `python src/descargar_procesos.py`.

   Se versionan porque SECOP se actualiza a diario y una descarga nueva no daría exactamente las mismas filas. Para trabajar con procesos más recientes basta con volver a correr el script, sabiendo que las cifras del cruce pueden cambiar.
3. Ejecutar `notebooks/01_ingesta.ipynb` (unos 4 minutos). Los datos procesados quedan en `data/processed/`, y las figuras y tablas del informe en `figures/` y `reports/`. En Google Colab hay que subir al panel de archivos los tres archivos de `data/raw/`; si solo se suben los dos Excel, el notebook descarga los procesos de la API.
4. Regenerar el informe: `python src/generar_informe.py`. Toma sus cifras de `reports/metricas_clave.json`, que escribe el notebook.

Los resultados de `data/processed/` no se versionan (`.gitignore`): se vuelven a generar al correr el notebook. Todos los algoritmos usan una semilla fija (`random_state=42`), así que cada ejecución da las mismas cifras.
