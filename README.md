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
| 1 | [SECOP II - Contratos Electrónicos](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/about_data) (datos.gov.co) | `jbjy-vk9h` | **En uso.** Exportación de los contratos de la Alcaldía de Pereira 2020-2026, dividida en dos archivos por periodo (2020-2023 y 2024-2026) para comparar administraciones. |
| 2 | [SECOP II - Procesos de Contratación](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt/about_data) (datos.gov.co) | `p6dx-8zbt` | **Pendiente de cruce.** Se unirá con los contratos por `proceso_de_compra`. |

## Estructura del repositorio

- `/data/raw` — Datos originales sin modificar (no se versionan; ver "Cómo reproducir")
- `/data/processed` — Datos limpios y transformados
- `/notebooks` — Jupyter notebooks del análisis
  - `01_ingesta.ipynb` — Adquisición: lectura, cruce, verificación de filas y diccionario de datos
  - `02_eda.ipynb` — Análisis exploratorio (pendiente)
  - `03_anomalias.ipynb` — Concentración de proveedores y montos atípicos (pendiente)
  - `04_dashboard.ipynb` — Visualización de resultados (pendiente)
- `/src` — Scripts de Python reutilizables
- `/reports` — Reportes y documentación generada
- `/figures` — Gráficos y visualizaciones

## Estado actual

**Corte 1 — Adquisición**

- [x] Ficha del proyecto y estructura del repositorio
- [x] Lectura de las fuentes con pandas (`.shape`, `.head()`, `.info()`)
- [x] Cruce por `id_contrato` con verificación de filas antes y después
- [x] Diccionario de datos de las 15 columnas del dataset cruzado
- [x] Subconjunto de análisis 2022-2025 alineado con la Ficha
- [ ] Cruce con SECOP II - Procesos de Contratación (`p6dx-8zbt`)
- [ ] Limpieza y estandarización de categorías
- [ ] Análisis exploratorio
- [ ] Detección de concentración y montos atípicos
- [ ] Dashboard y conclusiones

### Resultados de la adquisición

| Concepto | Valor |
|---|---|
| Filas 2020-2023 | 22.522 |
| Filas 2024-2026 | 17.753 |
| Columnas por fuente | 14 |
| Contratos compartidos entre periodos | 0 |
| Filas antes / después del cruce | 40.275 / 40.275 |
| Dataset final | 40.275 filas × 15 columnas (sin nulos) |
| Subconjunto 2022-2025 | 24.779 filas |

La llave `id_contrato` no tiene nulos ni duplicados.

## Riesgos y hallazgos

- `estado_contrato` mezcla formatos (`Cerrado`, `terminado`, `cedido`) y contiene estados como `Borrador` y `Aprobado` que podrían no ser contratos formalizados.
- `modalidad_de_contratacion` tiene categorías casi duplicadas (p. ej. `Contratación directa` y `Contratación Directa (con ofertas)`).
- `tipo_de_contrato` incluye categorías ambiguas (`Otro`, `Decreto 092 de 2017`).
- Hay 2 contratos con fecha de inicio posterior a la fecha de consulta y 3 con fecha de fin anterior al inicio, que se revisarán en la limpieza.

## Cómo reproducir

1. Clonar el repositorio e instalar dependencias: `pip install -r requirements.txt`
2. Descargar los datos de contratos de la Alcaldía de Pereira desde el dataset [`jbjy-vk9h`](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h/about_data) y guardarlos en `data/raw/` como:
   - `Vista-_Contratos_Alcaldia_de_Pereira_2020-2023.xlsx`
   - `Vista-_Contratos_Alcaldia_de_Pereira_2024-2026.xlsx`
3. Ejecutar `notebooks/01_ingesta.ipynb`. En Google Colab basta con subir los dos archivos al panel de archivos.

Los datos crudos están excluidos del control de versiones (`.gitignore`).
