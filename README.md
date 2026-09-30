# Proyecto de Minería de Datos — Contratación Pública Pereira

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

- `/data/raw` — Datos originales sin modificar: los dos Excel de contratos (versionados) y el CSV de procesos (se descarga; ver "Cómo reproducir")
- `/data/processed` — Datos limpios y transformados
- `/notebooks` — Jupyter notebooks del análisis
  - `01_ingesta.ipynb` — Adquisición: lectura de las dos fuentes, cruce Contratos ↔ Procesos, verificación de filas y diccionario de datos
  - `02_eda.ipynb` — Análisis exploratorio (pendiente)
  - `03_anomalias.ipynb` — Concentración de proveedores y montos atípicos (pendiente)
  - `04_dashboard.ipynb` — Visualización de resultados (pendiente)
- `/src` — Scripts de Python reutilizables
  - `descargar_procesos.py` — Descarga los procesos de Pereira desde la API de SECOP II
- `/reports` — Reportes y documentación generada
- `/figures` — Gráficos y visualizaciones

## Estado actual

**Corte 1 — Adquisición**

- [x] Ficha del proyecto y estructura del repositorio
- [x] Lectura de las fuentes con pandas (`.shape`, `.head()`, `.info()`)
- [x] Unión de los dos periodos de contratos (verificada por `id_contrato`)
- [x] Cruce Contratos ↔ Procesos por `proceso_de_compra` con verificación de filas antes y después
- [x] Diccionario de datos de las 30 columnas del dataset cruzado
- [x] Subconjunto de análisis 2022-2025 alineado con la Ficha
- [ ] Limpieza y estandarización de categorías
- [ ] Análisis exploratorio
- [ ] Detección de concentración y montos atípicos
- [ ] Dashboard y conclusiones

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

## Riesgos y hallazgos

- **Procesos repetidos en la fuente 2.** SECOP publica el mismo proceso varias veces (2.450 filas idénticas y una fila por fase en 522 procesos). Cruzar sin depurar inflaba el resultado de 40.275 a 45.384 filas. Se resolvió dejando la última fase publicada de cada proceso y exigiendo `validate="many_to_one"` en el `merge`.
- **Contratos sin proceso publicado.** 2.752 contratos (6,8 %), casi todos de contratación directa y sobre todo desde 2024, no tienen proceso en el dataset `p6dx-8zbt`, ni siquiera buscándolos sin filtrar por entidad. Se conservan marcados con `tiene_proceso = False`.
- `estado_contrato` mezcla formatos (`Cerrado`, `terminado`, `cedido`) y contiene estados como `Borrador` y `Aprobado` que podrían no ser contratos formalizados.
- `modalidad_de_contratacion` tiene categorías casi duplicadas (p. ej. `Contratación directa` y `Contratación Directa (con ofertas)`).
- `tipo_de_contrato` incluye categorías ambiguas (`Otro`, `Decreto 092 de 2017`).
- Hay 2 contratos con fecha de inicio posterior a la fecha de consulta y 3 con fecha de fin anterior al inicio, que se revisarán en la limpieza.

## Cómo reproducir

1. Clonar el repositorio e instalar dependencias: `pip install -r requirements.txt`
2. Los contratos ya vienen en `data/raw/`, exportados del dataset [`jbjy-vk9h`](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/about_data) el 29 de septiembre de 2026:
   - `Vista-_Contratos_Alcaldia_de_Pereira_2020-2023.xlsx`
   - `Vista-_Contratos_Alcaldia_de_Pereira_2024-2026.xlsx`

   Se versionan porque SECOP se actualiza a diario y una descarga nueva no daría exactamente las mismas filas.
3. Descargar los procesos: `python src/descargar_procesos.py` (queda en `data/raw/procesos_pereira_p6dx-8zbt.csv`). Si se omite este paso, el notebook los descarga solo.
4. Ejecutar `notebooks/01_ingesta.ipynb`. Los resultados quedan en `data/processed/`. En Google Colab basta con subir al panel de archivos los dos Excel de `data/raw/`.

El CSV de procesos y los resultados de `data/processed/` no se versionan (`.gitignore`): se vuelven a generar con el script y el notebook.
