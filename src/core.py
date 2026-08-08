import os
import subprocess
from collections import Counter, OrderedDict
from datetime import datetime
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