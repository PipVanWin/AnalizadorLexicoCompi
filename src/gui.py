"""
gui.py
Interfaz grafica (Tkinter) para el Analizador Estatico de Codigo.
Proyecto Corto #1 - Compiladores - Universidad Mesoamericana
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import core


class AplicacionAnalizador(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador Estatico de Codigo - Kotlin")
        self.geometry("980x650")
        self.resultado = None

        self._construir_widgets()

    def _construir_widgets(self):
        barra_superior = tk.Frame(self, padx=10, pady=10)
        barra_superior.pack(fill="x")

        tk.Button(
            barra_superior,
            text="Abrir archivo Kotlin (.kt)",
            command=self.abrir_archivo,
        ).pack(side="left")

        self.etiqueta_archivo = tk.Label(
            barra_superior, text="Ningun archivo cargado", fg="gray"
        )
        self.etiqueta_archivo.pack(side="left", padx=15)

        barra_acciones = tk.Frame(self, padx=10, pady=5)
        barra_acciones.pack(fill="x")

        self.boton_pdf = tk.Button(
            barra_acciones,
            text="Generar Reportes PDF",
            command=self.generar_pdfs,
            state="disabled",
        )
        self.boton_pdf.pack(side="left")

        self.boton_mongo = tk.Button(
            barra_acciones,
            text="Guardar tabla de simbolos en MongoDB",
            command=self.guardar_mongo,
            state="disabled",
        )
        self.boton_mongo.pack(side="left", padx=10)

        # Notebook con pestanas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._crear_pestana_resumen()
        self._crear_pestana_detalle()
        self._crear_pestana_simbolos()

        self.barra_estado = tk.Label(
            self, text="Listo.", bd=1, relief="sunken", anchor="w"
        )
        self.barra_estado.pack(fill="x", side="bottom")

    def _crear_pestana_resumen(self):
        self.frame_resumen = tk.Frame(self.notebook, padx=15, pady=15)
        self.notebook.add(self.frame_resumen, text="Resumen (Reporte 1)")

        self.texto_resumen = tk.Text(
            self.frame_resumen,
            wrap="word",
            state="disabled",
            font=("Courier New", 10),
        )
        self.texto_resumen.pack(fill="both", expand=True)

    def _crear_pestana_detalle(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Detalle de lexemas (Reporte 2)")

        columnas = ("lexema", "linea", "token", "categoria")
        self.tabla_detalle = ttk.Treeview(
            frame, columns=columnas, show="headings"
        )
        for col, ancho in zip(columnas, (300, 80, 200, 150)):
            self.tabla_detalle.heading(col, text=col.capitalize())
            self.tabla_detalle.column(col, width=ancho)

        scroll = ttk.Scrollbar(
            frame, orient="vertical", command=self.tabla_detalle.yview
        )
        self.tabla_detalle.configure(yscrollcommand=scroll.set)
        self.tabla_detalle.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _crear_pestana_simbolos(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Tabla de simbolos")

        columnas = ("lexema", "tipo", "primera_linea", "ocurrencias")
        self.tabla_simbolos_ui = ttk.Treeview(
            frame, columns=columnas, show="headings"
        )
        for col, ancho in zip(columnas, (300, 150, 120, 120)):
            self.tabla_simbolos_ui.heading(
                col, text=col.replace("_", " ").capitalize()
            )
            self.tabla_simbolos_ui.column(col, width=ancho)

        scroll = ttk.Scrollbar(
            frame, orient="vertical", command=self.tabla_simbolos_ui.yview
        )
        self.tabla_simbolos_ui.configure(yscrollcommand=scroll.set)
        self.tabla_simbolos_ui.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def abrir_archivo(self):
        pass

    def _actualizar_resumen(self):
        pass

    def _actualizar_detalle(self):
        pass

    def _actualizar_simbolos(self):
        pass

    def generar_pdfs(self):
        pass

    def guardar_mongo(self):
        pass


if __name__ == "__main__":
    app = AplicacionAnalizador()
    app.mainloop()