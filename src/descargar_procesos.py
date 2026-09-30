"""Descarga los procesos de contratación del Municipio de Pereira desde SECOP II.

Fuente: SECOP II - Procesos de Contratación (datos.gov.co, dataset p6dx-8zbt),
consultada por la API pública de Socrata. Se filtra por el NIT de la entidad
(891480030, "MUNICIPIO DE PEREIRA- OFICIAL") y se guardan solo las columnas
que usa el proyecto.

Uso, desde la raíz del repositorio:
    python src/descargar_procesos.py
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

URL = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
NIT_ENTIDAD = "891480030"
COLUMNAS = [
    "id_del_portafolio",            # llave del cruce = proceso_de_compra en Contratos
    "id_del_proceso",
    "referencia_del_proceso",
    "entidad",
    "nit_entidad",
    "nombre_de_la_unidad_de",       # secretaría o dependencia que contrata
    "nombre_del_procedimiento",
    "modalidad_de_contratacion",
    "justificaci_n_modalidad_de",
    "tipo_de_contrato",
    "fase",
    "estado_del_procedimiento",
    "fecha_de_publicacion_del",
    "precio_base",
    "duracion",
    "unidad_de_duracion",
    "proveedores_invitados",
    "proveedores_que_manifestaron",
    "respuestas_al_procedimiento",
    "proveedores_unicos_con",
    "adjudicado",
    "valor_total_adjudicacion",
]
TAMANO_PAGINA = 50_000
SALIDA = Path("data/raw/procesos_pereira_p6dx-8zbt.csv")


def descargar():
    filas, offset = [], 0
    while True:
        params = {
            "$select": ",".join(COLUMNAS),
            "$where": f"nit_entidad='{NIT_ENTIDAD}'",
            "$order": "id_del_proceso",
            "$limit": TAMANO_PAGINA,
            "$offset": offset,
        }
        with urllib.request.urlopen(f"{URL}?{urllib.parse.urlencode(params)}", timeout=300) as r:
            pagina = json.load(r)
        filas.extend(pagina)
        if len(pagina) < TAMANO_PAGINA:
            break
        offset += TAMANO_PAGINA
    return pd.DataFrame(filas, columns=COLUMNAS)


if __name__ == "__main__":
    df = descargar()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False)
    print(f"{len(df)} procesos guardados en {SALIDA}")
