"""Genera el informe final en PDF a partir de los resultados del notebook.

Lee lo que exporta la sección 17.2 de notebooks/01_ingesta.ipynb:
    reports/metricas_clave.json, reports/lista_revision_2022_2025.csv,
    reports/vigilancia_2026.csv y las figuras de figures/
y escribe reports/informe_final.pdf. Las cifras del texto salen de esos archivos,
no se copian a mano.

Uso, desde la raíz del repositorio y después de ejecutar el notebook:
    python src/generar_informe.py
"""
import json
from pathlib import Path

import matplotlib
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

RAIZ = Path(__file__).resolve().parents[1]
FIGURAS, INFORME = RAIZ / "figures", RAIZ / "reports"
REPOSITORIO = "https://github.com/jahenao28-jh/contratacion-publica-pereira"
NOTEBOOK = REPOSITORIO + "/blob/main/notebooks/01_ingesta.ipynb"
INTEGRANTES = "William Torres Valencia · Jhon Alexander Duque Buritica · Jorge Alberto Henao Vergel"

# ------------------------------------------------------------------ tipografía (DejaVu viene con matplotlib)
FUENTES = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
for nombre, archivo in [("DejaVu", "DejaVuSans.ttf"), ("DejaVu-Bold", "DejaVuSans-Bold.ttf"),
                        ("DejaVu-Oblique", "DejaVuSans-Oblique.ttf"), ("DejaVu-BoldOblique", "DejaVuSans-BoldOblique.ttf")]:
    pdfmetrics.registerFont(TTFont(nombre, str(FUENTES / archivo)))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu-Oblique",
                              boldItalic="DejaVu-BoldOblique")

AZUL, GRIS = colors.HexColor("#1f3b5c"), colors.HexColor("#5a6470")
E = {
    "titulo": ParagraphStyle("titulo", fontName="DejaVu-Bold", fontSize=17, leading=21, textColor=AZUL),
    "subtitulo": ParagraphStyle("subtitulo", fontName="DejaVu", fontSize=9, leading=12, textColor=GRIS),
    "h1": ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=13.5, leading=17, textColor=AZUL, spaceBefore=6, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=10.5, leading=14, textColor=AZUL, spaceBefore=8, spaceAfter=3),
    "texto": ParagraphStyle("texto", fontName="DejaVu", fontSize=9, leading=12.6, spaceAfter=4),
    "viñeta": ParagraphStyle("viñeta", fontName="DejaVu", fontSize=9, leading=12.6, leftIndent=12, bulletIndent=2, spaceAfter=2.5),
    "pie": ParagraphStyle("pie", fontName="DejaVu-Oblique", fontSize=7.5, leading=10, textColor=GRIS, alignment=TA_CENTER,
                          spaceAfter=6),
    "celda": ParagraphStyle("celda", fontName="DejaVu", fontSize=7.4, leading=9.4),
    "celda_n": ParagraphStyle("celda_n", fontName="DejaVu-Bold", fontSize=7.4, leading=9.4, textColor=colors.white),
}


def es(numero, decimales=0):
    """Número en formato español: punto para miles y coma para decimales."""
    return f"{numero:,.{decimales}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(numero, decimales=1):
    return f"{es(numero, decimales)} %"


def p(texto, estilo="texto"):
    return Paragraph(texto, E[estilo])


def viñetas(items):
    return [Paragraph(t, E["viñeta"], bulletText="•") for t in items]


def figura(archivo, ancho_cm, pie=None):
    ruta = FIGURAS / archivo
    from reportlab.lib.utils import ImageReader
    ancho_px, alto_px = ImageReader(str(ruta)).getSize()
    elementos = [Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * alto_px / ancho_px)]
    if pie:
        elementos.append(p(pie, "pie"))
    return elementos


def tabla(filas, anchos_cm, encabezado=True):
    datos = [[c if isinstance(c, Paragraph) else p(str(c), "celda_n" if encabezado and i == 0 else "celda")
              for c in fila] for i, fila in enumerate(filas)]
    t = Table(datos, colWidths=[a * cm for a in anchos_cm], repeatRows=1 if encabezado else 0)
    estilo = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c9d1db")),
              ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5f9")])]
    if encabezado:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), AZUL))
    t.setStyle(TableStyle(estilo))
    return t


DEPENDENCIAS = {
    "SECRETARIA DE CULTURA": "Cultura", "SECRETARIA DE DEPORTES Y RECREACION": "Deportes y Recreación",
    "SECRETARIA DE DESARROLLO ECONOMICO Y COMPETITIVIDAD": "Desarrollo Económico", "SECRETARIA DE DESARROLLO RURAL": "Desarrollo Rural",
    "SECRETARIA DE EDUCACION": "Educación", "SECRETARIA DE GESTION ADMINISTRATIVA": "Gestión Administrativa",
    "SECRETARIA DE GOBIERNO": "Gobierno", "SECRETARIA DE HACIENDA Y FINANZAS PUBLICAS": "Hacienda",
    "SECRETARIA DE INFRAESTRUCTURA": "Infraestructura", "SECRETARIA DE PLANEACION": "Planeación", "SECRETARIA DE SALUD": "Salud",
    "SECRETARIA DE TECNOLOGIAS DE LA INFORMACION Y LA COMUNICACION": "TIC", "SECRETARIA DE VIVIENDA SOCIAL": "Vivienda Social",
    "SECRETARIA DESARROLLO SOCIAL Y POLITICO": "Desarrollo Social", "SECRETARIA JURIDICA": "Jurídica", "SECRETARIA PRIVADA": "Privada",
}
MOTIVOS = {"monto atípico alto": "monto atípico", "adicionado hasta el tope legal (1,5 o más)": "tope legal",
           "proveedor con 10 % o más de su dependencia": "≥ 10 % de su dependencia",
           "directo en enero electoral": "enero electoral", "un solo oferente": "un oferente",
           "anomalía (Isolation Forest)": "anomalía"}


def corto(texto, largo=40):
    texto = str(texto)
    return texto if len(texto) <= largo else texto[:largo - 1] + "…"


def construir():
    m = json.loads((INFORME / "metricas_clave.json").read_text(encoding="utf-8"))
    revision = pd.read_csv(INFORME / "lista_revision_2022_2025.csv")
    vigilancia = pd.read_csv(INFORME / "vigilancia_2026.csv")
    seg = m["segmentos"]
    grandes = seg["Grandes contratos concentrados"]
    servicios_c = seg["Servicios cortos"]["% de los contratos"] + seg["Servicios de año completo"]["% de los contratos"]
    servicios_v = seg["Servicios cortos"]["% del valor"] + seg["Servicios de año completo"]["% del valor"]
    v24 = m["modelo_validacion"]["2022-2023|2024|regresión logística"]
    v23 = m["modelo_validacion"]["2022|2023|regresión logística"]
    t24, t25 = m["tope_por_anio"]["2024"], m["tope_por_anio"]["2025"]
    pct_revision = m["revision_contratos"] / m["contratos_dinero"] * 100
    pct_un_oferente = m["procesos_un_oferente"] / m["procesos_con_convocatoria"] * 100
    hr = revision[revision["proveedor_adjudicado"].str.contains("HERNÁNDEZ RODAS", na=False)]
    valor_hr = hr["valor_del_contrato"].max() / 1e6
    pico_mes = {"01": "enero", "02": "febrero", "03": "marzo", "04": "abril", "05": "mayo", "06": "junio", "07": "julio",
                "08": "agosto", "09": "septiembre", "10": "octubre", "11": "noviembre", "12": "diciembre"}
    anio_pico, mes_pico = m["pico_no_electoral_mes"].split("-")
    historia = []

    # ---------------------------------------------------------- portada y resumen ejecutivo
    historia += [
        p("Contratación pública de la Alcaldía de Pereira: dónde mirar primero", "titulo"),
        p(f"Proyecto final · Minería de Datos · CIAF · 24 de noviembre de 2026<br/>{INTEGRANTES}<br/>"
          f'Repositorio: <a href="{REPOSITORIO}" color="#1f5fa8">{REPOSITORIO}</a>', "subtitulo"),
        Spacer(1, 8),
        p("1. Resumen ejecutivo", "h1"),
        p(f"<b>El problema.</b> La Alcaldía de Pereira registra en SECOP II miles de contratos al año: {es(m['contratos_total'])} "
          f"entre 2020 y 2026. Entre 2022 y 2025, el {pct(m['pct_directa'])} se firmó por contratación directa, sin competencia. "
          "La Oficina de Control Interno no puede revisarlos todos y necesita saber por dónde empezar."),
        p("<b>La pregunta con la que arrancamos (Unidad 1).</b> «¿Qué procesos de contratación de la Alcaldía de Pereira "
          "registrados en SECOP II entre 2022 y 2025 presentan señales de concentración en proveedores o montos atípicos, para "
          "que la Oficina de Control Interno priorice cuáles revisar primero?»"),
        p(f"<b>Los datos (Unidad 2).</b> Dos fuentes públicas de datos.gov.co: <i>SECOP II – Contratos Electrónicos</i> "
          f"({es(m['contratos_total'])} contratos de la Alcaldía) y <i>SECOP II – Procesos de Contratación</i> "
          f"({es(m['procesos_descargados'])} publicaciones del Municipio, NIT 891480030). Se cruzaron por el código del proceso de "
          f"compra, y el {pct(m['pct_con_proceso'])} de los contratos encontró su proceso. Los datos tienen corte al 29 de "
          f"septiembre de 2026, y el análisis se centra en los {es(m['contratos_alcance'])} contratos que iniciaron entre 2022 y 2025."),
        p("<b>Lo que encontramos.</b>"),
        *viñetas([
            f"<b>Pocos contratos concentran el dinero.</b> {es(m['revision_contratos'])} contratos (el {pct(pct_revision)}) reúnen "
            f"el {pct(m['revision_pct_valor'])} del valor y forman la lista de revisión prioritaria. Su núcleo son "
            f"{es(grandes['contratos'])} «grandes contratos concentrados» ({pct(grandes['% de los contratos'])} de los contratos) "
            f"con el {pct(grandes['% del valor'])} del dinero.",
            f"<b>La competencia casi no actúa como control.</b> Además del {pct(m['pct_directa'])} de contratación directa, el "
            f"{pct(pct_un_oferente)} de los procesos con convocatoria recibió una sola oferta.",
            f"<b>{es(m['tope_exacto'])} contratos crecieron exactamente hasta el tope legal</b>: terminaron valiendo 1,5 veces su "
            f"precio base, el máximo de adiciones que permite la ley. Un modelo los anticipa al firmar: revisando el 10 % de mayor "
            f"riesgo encontró el {pct(m['modelo_captura_2024'])} de los casos de 2024, {es(m['modelo_lift_2024'], 1)} veces más "
            "que al azar.",
            f"<b>La contratación directa sigue el calendario electoral.</b> {es(m['enero_2022'])} contratos directos iniciaron en "
            f"enero de 2022 y {es(m['enero_2026'])} en enero de 2026, justo antes de la Ley de Garantías; ningún mes de los demás "
            f"años pasó de {es(m['pico_no_electoral'])}.",
        ]),
        p(f"<b>Qué recomendamos.</b> Empezar por la lista de {es(m['revision_contratos'])} contratos; vigilar las adiciones de los "
          f"{es(m['vigilancia_2026_top10pct'])} contratos de 2026 con mayor puntaje de riesgo; y usar todo esto como guía para "
          "priorizar, nunca como prueba de irregularidades (ver la sección 4)."),
        PageBreak(),
    ]

    # ---------------------------------------------------------- producto analítico
    historia += [
        p("2. Producto analítico: los hallazgos juntos", "h1"),
        p("El tablero reúne en una sola vista lo que encontraron las distintas etapas del proyecto: el análisis exploratorio "
          "(calendario, concentración, adiciones), la segmentación, el modelo predictivo y la detección de anomalías. Debajo se "
          "explica qué significa cada parte para la pregunta y cómo se combinan en una sola lista de revisión."),
        *figura("tablero_final.png", 17, "Tablero final (sección 17.2 del notebook). Contratos de la Alcaldía de Pereira que "
                                         "iniciaron entre 2022 y 2025; el primer panel muestra 2020-2026 para comparar dos años electorales."),
        PageBreak(),
        p("2.1 Dónde está el dinero · exploración y segmentación (unidades 3 y 5)", "h2"),
        p(f"La segmentación con k-means agrupó los {es(m['contratos_dinero'])} contratos con valor en cuatro segmentos, usando el "
          "valor, el valor mensual, la duración, la participación del proveedor en su dependencia y dos señales de 0/1. Los "
          f"servicios cortos y los de año completo son el {pct(servicios_c)} de los contratos, pero apenas el {pct(servicios_v)} "
          f"del dinero: casi todos son prestación de servicios por contratación directa. En el otro extremo, los <b>grandes "
          f"contratos concentrados</b> son {es(grandes['contratos'])} y reúnen el {pct(grandes['% del valor'])} del valor; en ellos "
          f"el proveedor se lleva en promedio el {pct(grandes['participación media del proveedor (%)'])} de lo que contrata su "
          f"dependencia en el año. La concentración también se ve por proveedor: {es(m['proveedores_mitad_valor'])} de los "
          f"{es(m['proveedores'])} proveedores reciben la mitad del dinero, y en la Secretaría Jurídica (índice de concentración "
          f"HHI de {es(m['hhi_juridica'])}, frente a una mediana de {es(m['hhi_mediana'])}) un solo contrato de "
          f"{es(valor_hr)} millones, a HERNÁNDEZ RODAS S.A.S, es el {pct(m['pct_mayor_proveedor_juridica'])} de lo que contrató."),
        *figura("tablero_4_segmentos.png", 13.5),
        p("2.2 Qué se sale de lo normal · calidad y anomalías (unidades 3 y 7)", "h2"),
        p(f"Antes de buscar lo atípico hubo que limpiar: un contrato figuraba por {es(m['valor_imposible'] / 1e15, 1)} × 10<super>15</super> "
          "pesos (su precio base elevado al cuadrado), y por sí solo hacía parecer que 10 proveedores se llevaban todo el dinero; se "
          "corrigió al precio base. Después, dos miradas que se complementan. Las reglas marcan lo raro <i>para su tipo de "
          f"contrato</i> ({es(m['atipicos_altos'])} montos altos y {es(m['atipicos_bajos'])} bajos en 2020-2026, con el método IQR "
          "sobre el logaritmo del valor) y cinco señales de alerta por contrato. Isolation Forest mira todas las variables juntas: "
          f"marcó {es(m['anomalias'])} contratos (1 %) que reúnen el {pct(m['anomalias_pct_valor'])} del valor. "
          f"{es(m['anomalias_sin_senal'])} de ellos no tienen ninguna señal de las reglas (obras y suministros enormes, pero "
          f"normales para su tipo), y el bosque deja pasar {es(m['atipicos_no_bosque'])} de los {es(m['atipicos_alcance'])} montos "
          "atípicos por tipo (servicios caros, pero pequeños frente al conjunto). Por eso la lista de revisión usa las dos."),
        *figura("tablero_6_anomalias.png", 12.5),
        PageBreak(),
        p("2.3 Qué se puede anticipar · modelo predictivo (unidad 6)", "h2"),
        p(f"El hallazgo más llamativo de la exploración fue un pico: {es(m['tope_exacto'])} contratos terminaron valiendo "
          f"exactamente 1,5 veces su precio base, frente a {es(m['tope_vecinos'])} entre 1,45 y 1,4999. Es el tope de adiciones que "
          "permite la ley (50 % del valor inicial, Ley 80 de 1993, art. 40). Una regresión logística que solo usa datos conocidos al "
          "firmar (precio base, duración planeada, modalidad, tipo, dependencia, mes de inicio, entre otros) ordena los contratos por "
          "riesgo de terminar así. Entrenada con 2022-2023 y probada con 2024, al revisar el 10 % de mayor riesgo encuentra el "
          f"{pct(m['modelo_captura_2024'])} de los contratos que llegaron al tope (ROC-AUC de {es(m['modelo_auc_2024'], 3)}): "
          f"{es(m['modelo_lift_2024'], 1)} veces más que una revisión al azar. Lo que más pesa es el mes de inicio: los contratos que "
          "arrancan en febrero o marzo son los que más se estiran."),
        Table([[figura("tablero_5_modelo.png", 8.4)[0], figura("tablero_7_meses.png", 8.4)[0]]],
              colWidths=[8.6 * cm, 8.6 * cm]),
        p("Izquierda: contratos de 2024 encontrados según la parte revisada, frente a una revisión al azar. Derecha: porcentaje de "
          "contratos que llegan al tope según el mes en que iniciaron.", "pie"),
        p(f"Dos advertencias. Con un solo año de entrenamiento (2022 → 2023) el modelo no funcionó (ROC-AUC de "
          f"{es(v23['ROC-AUC'], 3)}), porque la Ley de Garantías deformó el calendario de 2022. Y en 2025 la proporción de "
          f"contratos en el tope cayó a {pct(t25['pct'])}, frente a {pct(t24['pct'])} en 2024, sin que los datos permitan saber "
          "si cambió la práctica o si faltan registros."),
        p("2.4 Cuándo mirar · el calendario (unidad 3)", "h2"),
        p(f"La contratación directa sigue el calendario político. En enero de 2022 iniciaron {es(m['enero_2022'])} contratos "
          f"directos, y en enero de 2026, {es(m['enero_2026'])}: los dos meses más altos de la serie, justo antes de que la Ley de "
          "Garantías prohíba la contratación directa (desde cuatro meses antes de la elección presidencial). Entre marzo y mayo de "
          f"2022 iniciaron solo {es(m['marzo_mayo_2022'])}. En los demás años, el mes más alto fue {pico_mes[mes_pico]} de "
          f"{anio_pico}, con {es(m['pico_no_electoral'])}. Esas semanas concentran miles de contratos y son una ventana natural de "
          "revisión."),
        *figura("tablero_1_serie_directa.png", 13),
        PageBreak(),
    ]

    # ---------------------------------------------------------- listas
    filas_revision = [["#", "Proveedor", "Dependencia", "Segmento", "Millones", "Motivos"]]
    for i, (_, r) in enumerate(revision.head(10).iterrows(), start=1):
        motivos = ", ".join(MOTIVOS.get(x.strip(), x.strip()) for x in str(r["detalle"]).split(";"))
        filas_revision.append([i, corto(r["proveedor_adjudicado"], 70), DEPENDENCIAS.get(r["dependencia"], r["dependencia"]),
                               r["segmento"], es(r["valor_del_contrato"] / 1e6), motivos])
    filas_vigilancia = [["#", "Proveedor", "Dependencia", "Modalidad", "Tipo", "Inicio", "Precio base (millones)"]]
    for i, (_, r) in enumerate(vigilancia.head(5).iterrows(), start=1):
        filas_vigilancia.append([i, corto(r["proveedor_adjudicado"], 70), DEPENDENCIAS.get(r["dependencia"], r["dependencia"]),
                                 r["modalidad_grupo"], r["tipo_de_contrato"], str(r["fecha_de_inicio_del_contrato"])[:10],
                                 es(r["precio_base"] / 1e6)])
    historia += [
        p("2.5 La respuesta: lista de revisión y vigilancia de 2026 (unidad 8)", "h2"),
        p("Al juntar las cuatro miradas, entra a la lista de revisión todo contrato que Isolation Forest marca como anomalía o que "
          f"acumula dos o más señales: {es(m['revision_contratos'])} contratos ({pct(pct_revision)}) con el "
          f"{pct(m['revision_pct_valor'])} del dinero; {es(m['revision_grandes'])} de ellos son grandes contratos concentrados. Se "
          "ordenan por número de motivos y, a igualdad, por valor. Estos son los diez primeros; la lista completa está en "
          "<i>reports/lista_revision_2022_2025.csv</i>."),
        tabla(filas_revision, [0.9, 4.4, 2.5, 3.2, 1.8, 4.2]),
        Spacer(1, 8),
        p(f"Hacia adelante, el modelo ordena los {es(m['vigilancia_2026_contratos'])} contratos de 2026 que todavía no llegan al "
          f"tope. Los {es(m['vigilancia_2026_top10pct'])} de mayor puntaje (el 10 %) están en <i>reports/vigilancia_2026.csv</i>: "
          "conviene revisarlos cuando se pida una adición, antes de aprobarla. Estos son los cinco primeros. El puntaje solo sirve "
          "para ordenar: no es una probabilidad ni una acusación."),
        tabla(filas_vigilancia, [0.9, 4.0, 2.5, 2.4, 2.6, 2.2, 2.4]),
        PageBreak(),
    ]

    # ---------------------------------------------------------- recorrido de las unidades
    unidades = [
        ["Unidad", "Qué se hizo", "Resultado clave", "Dónde está"],
        ["1 · Problema", "Pregunta de negocio y alcance (2022-2025)", "Priorizar la revisión de Control Interno",
         "README y encabezado del notebook (Ficha del proyecto)"],
        ["2 · Adquisición", "Lectura de dos fuentes de SECOP II y cruce por el código del proceso, con filas verificadas antes y después",
         f"{es(m['contratos_total'])} contratos; {pct(m['pct_con_proceso'])} con su proceso", "Secciones 1 a 10 (entrega de Corte 1)"],
        ["3 · Calidad y exploración", "Tipos corregidos, atípicos tratados con su justificación, estadísticas y 6 gráficos",
         "11 casos de calidad decididos; 5 hallazgos", "Secciones 11 y 12 (Checkpoint 1)"],
        ["4 · Características", "6 variables derivadas, one-hot, escalado y funciones reproducibles",
         "preparar_dataset y proceso_completo dan lo mismo dos veces", "Sección 13 (Checkpoint 1)"],
        ["5 · Segmentación", "k-means; variables y número de grupos elegidos con codo y silueta",
         f"4 segmentos; {es(grandes['contratos'])} contratos con el {pct(grandes['% del valor'])} del dinero", "Sección 14"],
        ["6 · Modelo predictivo", "Regresión logística validada en el tiempo, sin fuga de información",
         f"{pct(m['modelo_captura_2024'])} de captura en el 10 % de mayor riesgo (2024)", "Sección 15"],
        ["7 · Técnica complementaria", "Detección de anomalías con Isolation Forest, comparada con las reglas",
         f"{es(m['anomalias'])} anomalías con el {pct(m['anomalias_pct_valor'])} del valor", "Sección 16"],
        ["8 · Producto final", "Tablero, lista de revisión, vigilancia de 2026 y este informe",
         f"{es(m['revision_contratos'])} contratos a revisar; {es(m['vigilancia_2026_top10pct'])} a vigilar",
         "Sección 17, carpetas figures/ y reports/"],
    ]
    historia += [
        p("3. Recorrido del proceso: las 8 unidades", "h1"),
        p("Todo el proceso está en un único notebook, ejecutado y versionado en GitHub junto con los datos originales, para que "
          "cualquiera obtenga las mismas cifras. Cada unidad quedó en una sección numerada:"),
        tabla(unidades, [3.0, 5.6, 4.6, 4.1]),
        Spacer(1, 6),
        p("Cómo verificarlo y reproducirlo", "h2"),
        *viñetas([
            f'Notebook con todas las salidas y gráficos: <a href="{NOTEBOOK}" color="#1f5fa8">{NOTEBOOK}</a>',
            "En Google Colab: subir el notebook y los tres archivos de <i>data/raw/</i>, y ejecutar todo (unos 4 minutos). En un "
            "computador: <i>pip install -r requirements.txt</i> y ejecutar <i>notebooks/01_ingesta.ipynb</i>.",
            "Este informe se regenera con <i>python src/generar_informe.py</i>: toma sus cifras de <i>reports/metricas_clave.json</i>, "
            "que escribe el notebook, en lugar de copiarlas a mano.",
            "Los resultados son reproducibles: todos los algoritmos usan una semilla fija (random_state = 42), y la función "
            "<i>proceso_completo()</i>, que va de los archivos originales a la matriz final, se ejecuta dos veces en el notebook "
            "con resultado idéntico.",
        ]),
        PageBreak(),
    ]

    # ---------------------------------------------------------- limitaciones y ética
    historia += [
        p("4. Limitaciones, riesgos y consideraciones éticas", "h1"),
        p("4.1 Decisiones que NO deben tomarse solo con este análisis", "h2"),
        *viñetas([
            "<b>Sancionar, denunciar o señalar en público a un contratista o a un funcionario.</b> Las listas dicen dónde mirar, no "
            "prueban nada: un contrato grande, adicionado o con un solo oferente puede ser perfectamente legítimo (obras, "
            "suministros grandes, servicios públicos).",
            "<b>Negar o aprobar una adición por el puntaje del modelo.</b> El puntaje ordena contratos según su parecido con los que "
            "se adicionaron antes; no es una probabilidad ni conoce las razones de cada adición.",
            "<b>Vetar proveedores o comparar dependencias o administraciones con estas cifras.</b> Los patrones dependen del "
            "calendario legal (Ley de Garantías), del cambio de gobierno en 2024 y de la calidad del registro en SECOP.",
        ]),
        p("4.2 Sesgos y huecos del dataset", "h2"),
        *viñetas([
            f"<b>Solo vemos lo que se publica en SECOP II.</b> {es(m['sin_proceso'])} contratos ({pct(100 - m['pct_con_proceso'])}) "
            "no tienen proceso publicado, casi todos de contratación directa y sobre todo desde 2024: para ellos no hay precio base, "
            "dependencia ni número de oferentes.",
            f"<b>El registro tiene errores.</b> Corregimos lo demostrable (el valor imposible, {es(m['documentos_corregidos'])} "
            f"documentos con símbolos, {es(m['sin_documento'])} contratos sin documento, fechas incoherentes), pero un valor mal "
            "digitado que parezca razonable no se puede detectar.",
            "<b>Medimos con aproximaciones.</b> SECOP da el valor actual del contrato, no el inicial: usamos el precio base del "
            "proceso como aproximación, así que la razón de 1,5 es aproximada.",
            "<b>La concentración puede estar subestimada.</b> Cada consorcio o unión temporal tiene su propio documento, así que no "
            "vemos qué empresas hay detrás: una misma empresa puede aparecer en varios.",
            f"<b>Los patrones cambian.</b> Con un solo año de entrenamiento el modelo no funcionó, y en 2025 la proporción de "
            f"contratos en el tope cayó de {pct(t24['pct'])} a {pct(t25['pct'])} sin que sepamos si cambió la práctica o si faltan "
            "registros. El modelo debe reentrenarse y revisarse cada año.",
            "<b>Los umbrales son decisiones nuestras</b> (1,5 veces el rango intercuartílico, 10 % de participación, 1 % de "
            "anomalías, 4 segmentos). Con otros umbrales, las listas cambian.",
        ]),
        p("4.3 Qué pasaría si alguien usara estos resultados sin revisión humana", "h2"),
        *viñetas([
            "<b>Falsos positivos con nombre propio.</b> Muchos contratistas son personas naturales (contratos de prestación de "
            "servicios). Aunque sus datos son públicos en SECOP, aparecer en una «lista de riesgo» sin revisión puede dañar su "
            "reputación injustamente.",
            f"<b>Falsos negativos.</b> El modelo encuentra el {pct(m['modelo_captura_2024'])} de los casos en su 10 % de mayor "
            "riesgo: el resto pasa. Y lo que no deja rastro en los datos (un sobrecosto dentro de rangos normales, un contrato "
            "partido en varios) no aparece en ninguna lista.",
            "<b>Un círculo que se alimenta solo.</b> Si solo se revisa lo que el modelo marca, los datos futuros reflejarán esas "
            "revisiones y el modelo seguirá viendo lo mismo.",
            "<b>Evasión.</b> Si los criterios se conocen (por ejemplo, adicionar hasta 1,49 veces en lugar de 1,5), se pueden esquivar.",
            "<b>Uso político.</b> En época electoral, las listas podrían usarse para atacar a una administración, cuando parte de "
            "los patrones (como el pico de enero) la explica la propia ley.",
        ]),
        p("4.4 Cómo usarlo bien", "h2"),
        *viñetas([
            "Revisión humana de cada contrato, con su expediente completo, antes de cualquier conclusión.",
            "Uso interno de Control Interno: no publicar listas con nombres.",
            "Reentrenar el modelo y recalcular las listas cada año, y registrar qué se revisó y qué se encontró para mejorar los "
            "criterios.",
        ]),
    ]
    return historia


def pie_de_pagina(lienzo, documento):
    lienzo.saveState()
    lienzo.setFont("DejaVu", 7.5)
    lienzo.setFillColor(GRIS)
    lienzo.drawString(2 * cm, 1.2 * cm, "Minería de Datos · Contratación pública de la Alcaldía de Pereira · Proyecto final")
    lienzo.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {documento.page}")
    lienzo.restoreState()


if __name__ == "__main__":
    salida = INFORME / "informe_final.pdf"
    documento = SimpleDocTemplate(str(salida), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                                  bottomMargin=1.8 * cm, title="Contratación pública de la Alcaldía de Pereira: dónde mirar primero",
                                  author="William Torres Valencia, Jhon Alexander Duque Buritica, Jorge Alberto Henao Vergel",
                                  subject="Proyecto final de Minería de Datos")
    documento.build(construir(), onFirstPage=pie_de_pagina, onLaterPages=pie_de_pagina)
    print("Informe generado:", salida)
