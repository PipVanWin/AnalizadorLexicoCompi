"""
Logica de negocio del Analizador Estatico de Codigo independiente de la GUI.

Funcionalidades:
Ejecutar el analizador lexico generado con flex (./analizador)
Calcular las estadisticas del Reporte 1 y Reporte 2
Generar ambos reportes en PDF
Guardar la tabla de simbolos en MongoDB
"""

import os
import subprocess
from collections import Counter, OrderedDict
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

try:
    from pymongo import MongoClient
    MONGO_DISPONIBLE = True
except ImportError:
    MONGO_DISPONIBLE = False

FS = "\x01"  # separador de campos usado por el analizador flex
RUTA_EJECUTABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analizador")

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "compiladores_proyecto1"
MONGO_COLECCION = "tabla_simbolos"


class ResultadoAnalisis:
    """Contiene todo lo calculado a partir de la salida del analizador."""

    def __init__(self, archivo, contenido, lexemas):
        self.archivo = archivo
        self.contenido = contenido

        # lexemas: lista de tuplas lexema, linea, token, categoria
        self.lexemas = lexemas
        self._calcular()

    def _calcular(self):
        if self.contenido == "":
            self.lineas_codigo = 0
        else:
            self.lineas_codigo = self.contenido.count("\n") + (
                1 if not self.contenido.endswith("\n") else 0
            )
        self.caracteres = len(self.contenido)

        self.enteros = [l for l in self.lexemas if l[3] == "ENTERO"]
        self.flotantes = [l for l in self.lexemas if l[3] == "FLOTANTE"]
        self.identificadores = [l for l in self.lexemas if l[3] == "IDENTIFICADOR"]
        self.booleanos = [l for l in self.lexemas if l[3] == "BOOLEANO"]
        self.operadores = [l for l in self.lexemas if l[3] == "OPERADOR"]
        self.cadenas = [l for l in self.lexemas if l[3] == "CADENA"]
        self.reservadas = [l for l in self.lexemas if l[3] == "RESERVADA"]

        # Conteo de cada palabra reservada en orden descendente
        contador = Counter(l[0] for l in self.reservadas)
        self.conteo_reservadas = contador.most_common()

        # Tabla de simbolos identificadores unicos con su primera linea y numero de ocurrencias independientemente de si se repiten
        tabla = OrderedDict()
        for lexema, linea, token, categoria in self.identificadores:
            if lexema not in tabla:
                tabla[lexema] = {
                    "lexema": lexema,
                    "tipo": "IDENTIFICADOR",
                    "primera_linea": linea,
                    "ocurrencias": 0,
                }
            tabla[lexema]["ocurrencias"] += 1
        self.tabla_simbolos = list(tabla.values())


def ejecutar_analizador(ruta_archivo):
    """Ejecuta el binario generado por flex y devuelve la lista de lexemas."""
    if not os.path.exists(RUTA_EJECUTABLE):
        raise FileNotFoundError(
            "No se encontro el ejecutable 'analizador'. "
            "Compilar primero con 'make' dentro de la carpeta src/."
        )
    proceso = subprocess.run(
        [RUTA_EJECUTABLE, ruta_archivo],
        capture_output=True, text=True
    )
    lexemas = []
    for linea_salida in proceso.stdout.split("\n"):
        if not linea_salida:
            continue
        partes = linea_salida.split(FS)
        if len(partes) != 4:
            continue
        lexema, linea, token, categoria = partes
        lexemas.append((lexema, int(linea), token, categoria))
    return lexemas, proceso.stderr

# Generacion de PDFs #

def generar_reporte1_pdf(resultado: ResultadoAnalisis, ruta_salida: str):
    doc = SimpleDocTemplate(ruta_salida, pagesize=letter,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    estilos = getSampleStyleSheet()
    titulo_estilo = ParagraphStyle(
        "TituloReporte", parent=estilos["Heading1"], alignment=1
    )
    elementos = []

    elementos.append(Paragraph("Reporte 1 - Estadisticas Generales", titulo_estilo))
    elementos.append(Paragraph(f"Archivo analizado: {os.path.basename(resultado.archivo)}",
                                estilos["Normal"]))
    elementos.append(Paragraph(f"Fecha de analisis: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                                estilos["Normal"]))
    elementos.append(Spacer(1, 0.6 * cm))

    datos_generales = [
        ["Metrica", "Cantidad"],
        ["Lineas de codigo", str(resultado.lineas_codigo)],
        ["Caracteres encontrados", str(resultado.caracteres)],
        ["Numeros enteros encontrados", str(len(resultado.enteros))],
        ["Numeros flotantes encontrados", str(len(resultado.flotantes))],
        ["Identificadores encontrados", str(len(resultado.identificadores))],
        ["Valores booleanos encontrados", str(len(resultado.booleanos))],
        ["Operadores encontrados", str(len(resultado.operadores))],
        ["Cadenas encontradas", str(len(resultado.cadenas))],
    ]
    tabla_general = Table(datos_generales, colWidths=[9 * cm, 5 * cm])
    tabla_general.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tabla_general)
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph("Conteo de palabras reservadas (orden descendente)",
                                estilos["Heading2"]))
    datos_reservadas = [["Palabra reservada", "Ocurrencias"]]
    for palabra, cantidad in resultado.conteo_reservadas:
        datos_reservadas.append([palabra, str(cantidad)])
    if len(datos_reservadas) == 1:
        datos_reservadas.append(["(ninguna encontrada)", "0"])

    tabla_reservadas = Table(datos_reservadas, colWidths=[9 * cm, 5 * cm], repeatRows=1)
    tabla_reservadas.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabla_reservadas)

    doc.build(elementos)


def generar_reporte2_pdf(resultado: ResultadoAnalisis, ruta_salida: str):
    doc = SimpleDocTemplate(ruta_salida, pagesize=letter,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    estilos = getSampleStyleSheet()
    titulo_estilo = ParagraphStyle(
        "TituloReporte", parent=estilos["Heading1"], alignment=1
    )
    elementos = []

    elementos.append(Paragraph("Reporte 2 - Detalle de Lexemas y Tabla de Simbolos",
                                titulo_estilo))
    elementos.append(Paragraph(f"Archivo analizado: {os.path.basename(resultado.archivo)}",
                                estilos["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph("Lexemas encontrados", estilos["Heading2"]))
    datos_lexemas = [["Lexema", "Linea", "Token"]]
    for lexema, linea, token, categoria in resultado.lexemas:
        texto_lexema = lexema if len(lexema) <= 40 else lexema[:37] + "..."
        datos_lexemas.append([texto_lexema, str(linea), token])

    tabla_lexemas = Table(datos_lexemas, colWidths=[8 * cm, 2 * cm, 5 * cm], repeatRows=1)
    tabla_lexemas.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))
    elementos.append(tabla_lexemas)
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph("Tabla de simbolos (identificadores unicos)",
                                estilos["Heading2"]))
    datos_simbolos = [["Identificador", "Tipo", "1a Linea", "Ocurrencias"]]
    for item in resultado.tabla_simbolos:
        datos_simbolos.append([
            item["lexema"], item["tipo"],
            str(item["primera_linea"]), str(item["ocurrencias"])
        ])
    if len(datos_simbolos) == 1:
        datos_simbolos.append(["(ninguno encontrado)", "-", "-", "-"])

    tabla_simbolos = Table(datos_simbolos, colWidths=[6 * cm, 4 * cm, 2.5 * cm, 2.5 * cm],
                            repeatRows=1)
    tabla_simbolos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabla_simbolos)

    doc.build(elementos)

# MongoDB
def guardar_en_mongo(resultado: ResultadoAnalisis):
    if not MONGO_DISPONIBLE:
        raise RuntimeError("pymongo no esta instalado. Ejecuta: pip install pymongo")
    cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    cliente.admin.command("ping")  # fuerza la conexion, lanza error si no hay servidor
    db = cliente[MONGO_DB]
    coleccion = db[MONGO_COLECCION]

    documento = {
        "archivo": os.path.basename(resultado.archivo),
        "fecha_analisis": datetime.now(),
        "total_identificadores_unicos": len(resultado.tabla_simbolos),
        "tabla_simbolos": resultado.tabla_simbolos,
    }
    resultado_insercion = coleccion.insert_one(documento)
    cliente.close()
    return resultado_insercion.inserted_id