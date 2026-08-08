"""
gui.py
Interfaz gráfica (CustomTkinter) para el Analizador Lexico de Kotlin
"""

import os
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

import core

# Configuración del tema global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AplicacionAnalizador(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Analizador Estático de Código - Kotlin")
        self.geometry("1020x680")
        self.minsize(900, 600)
        self.resultado = None

        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construir_widgets()

    def _construir_widgets(self):
        # 1. Barra Superior - Selección de Archivo
        self.frame_superior = ctk.CTkFrame(self, corner_radius=10)
        self.frame_superior.grid(
            row=0, column=0, padx=15, pady=(15, 5), sticky="ew"
        )

        self.boton_abrir = ctk.CTkButton(
            self.frame_superior,
            text="Abrir archivo Kotlin (.kt)",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.abrir_archivo,
        )
        self.boton_abrir.pack(side="left", padx=15, pady=12)

        self.etiqueta_archivo = ctk.CTkLabel(
            self.frame_superior,
            text="Ningún archivo cargado",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="gray",
        )
        self.etiqueta_archivo.pack(side="left", padx=10)

        # 2. Barra de Acciones - Botones de Exportación
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.grid(
            row=1, column=0, padx=15, pady=(5, 5), sticky="ew"
        )

        self.boton_pdf = ctk.CTkButton(
            self.frame_acciones,
            text="Generar Reportes PDF",
            state="disabled",
            command=self.generar_pdfs,
        )
        self.boton_pdf.pack(side="left", padx=(0, 10))

        self.boton_mongo = ctk.CTkButton(
            self.frame_acciones,
            text="Guardar en MongoDB",
            fg_color="#27ae60",
            hover_color="#219150",
            state="disabled",
            command=self.guardar_mongo,
        )
        self.boton_mongo.pack(side="left")

        # 3. Vista de Pestañas (Tabview)
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")

        self.tab_resumen = self.tabview.add("Resumen (Reporte 1)")
        self.tab_detalle = self.tabview.add("Detalle de Lexemas (Reporte 2)")
        self.tab_simbolos = self.tabview.add("Tabla de Símbolos")

        self._crear_pestana_resumen()
        self._crear_pestana_detalle()
        self._crear_pestana_simbolos()

        # 4. Barra de Estado
        self.barra_estado = ctk.CTkLabel(
            self,
            text="Listo.",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color="gray70",
        )
        self.barra_estado.grid(
            row=3, column=0, padx=15, pady=(2, 8), sticky="ew"
        )

    def _crear_pestana_resumen(self):
        self.tab_resumen.grid_columnconfigure(0, weight=1)
        self.tab_resumen.grid_rowconfigure(0, weight=1)

        self.texto_resumen = ctk.CTkTextbox(
            self.tab_resumen, font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.texto_resumen.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.texto_resumen.configure(state="disabled")

    def _estilar_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="#ffffff",
            fieldbackground="#2b2b2b",
            rowheight=26,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#1f1f1f",
            foreground="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#1f538d")])

    def _crear_pestana_detalle(self):
        self._estilar_treeview()
        self.tab_detalle.grid_columnconfigure(0, weight=1)
        self.tab_detalle.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(self.tab_detalle, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        columnas = ("lexema", "linea", "token", "categoria")
        self.tabla_detalle = ttk.Treeview(
            frame, columns=columnas, show="headings"
        )
        for col, ancho in zip(columnas, (300, 80, 200, 150)):
            self.tabla_detalle.heading(col, text=col.capitalize())
            self.tabla_detalle.column(col, width=ancho)

        scroll = ctk.CTkScrollbar(
            frame, orientation="vertical", command=self.tabla_detalle.yview
        )
        self.tabla_detalle.configure(yscrollcommand=scroll.set)

        self.tabla_detalle.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

    def _crear_pestana_simbolos(self):
        self.tab_simbolos.grid_columnconfigure(0, weight=1)
        self.tab_simbolos.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(self.tab_simbolos, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        columnas = ("lexema", "tipo", "primera_linea", "ocurrencias")
        self.tabla_simbolos_ui = ttk.Treeview(
            frame, columns=columnas, show="headings"
        )
        for col, ancho in zip(columnas, (300, 150, 120, 120)):
            self.tabla_simbolos_ui.heading(
                col, text=col.replace("_", " ").capitalize()
            )
            self.tabla_simbolos_ui.column(col, width=ancho)

        scroll = ctk.CTkScrollbar(
            frame, orientation="vertical", command=self.tabla_simbolos_ui.yview
        )
        self.tabla_simbolos_ui.configure(yscrollcommand=scroll.set)

        self.tabla_simbolos_ui.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

    # -------------------------------------------------------------- #

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona un archivo Kotlin",
            filetypes=[
                ("Archivos Kotlin", "*.kt"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not ruta:
            return

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            lexemas, errores = core.ejecutar_analizador(ruta)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.resultado = core.ResultadoAnalisis(ruta, contenido, lexemas)
        self.etiqueta_archivo.configure(
            text=os.path.basename(ruta), text_color="white"
        )
        self.boton_pdf.configure(state="normal")
        self.boton_mongo.configure(
            state="normal" if core.MONGO_DISPONIBLE else "disabled"
        )

        self._actualizar_resumen()
        self._actualizar_detalle()
        self._actualizar_simbolos()

        mensaje_estado = (
            f"Análisis completado: {len(lexemas)} lexemas encontrados."
        )
        if errores:
            mensaje_estado += " (Hubo advertencias, ver consola)"
            print(errores)
        self.barra_estado.configure(text=mensaje_estado)

    def _actualizar_resumen(self):
        r = self.resultado
        self.texto_resumen.configure(state="normal")
        self.texto_resumen.delete("1.0", "end")
        lineas = [
            f"Archivo:                           {os.path.basename(r.archivo)}",
            f"Líneas de código:                  {r.lineas_codigo}",
            f"Caracteres encontrados:            {r.caracteres}",
            f"Números enteros encontrados:        {len(r.enteros)}",
            f"Números flotantes encontrados:      {len(r.flotantes)}",
            f"Identificadores encontrados:        {len(r.identificadores)}",
            f"Valores booleanos encontrados:      {len(r.booleanos)}",
            f"Operadores encontrados:             {len(r.operadores)}",
            f"Cadenas encontradas:                {len(r.cadenas)}",
            "",
            "Conteo de palabras reservadas (orden descendente):",
        ]
        for palabra, cantidad in r.conteo_reservadas:
            lineas.append(f"    {palabra:<20} {cantidad}")
        self.texto_resumen.insert("1.0", "\n".join(lineas))
        self.texto_resumen.configure(state="disabled")

    def _actualizar_detalle(self):
        self.tabla_detalle.delete(*self.tabla_detalle.get_children())
        for lexema, linea, token, categoria in self.resultado.lexemas:
            self.tabla_detalle.insert(
                "", "end", values=(lexema, linea, token, categoria)
            )

    def _actualizar_simbolos(self):
        self.tabla_simbolos_ui.delete(*self.tabla_simbolos_ui.get_children())
        for item in self.resultado.tabla_simbolos:
            self.tabla_simbolos_ui.insert(
                "",
                "end",
                values=(
                    item["lexema"],
                    item["tipo"],
                    item["primera_linea"],
                    item["ocurrencias"],
                ),
            )

    def generar_pdfs(self):
        if not self.resultado:
            return
        carpeta = filedialog.askdirectory(
            title="Selecciona carpeta destino de los reportes"
        )
        if not carpeta:
            return
        try:
            ruta1 = os.path.join(carpeta, "reporte1.pdf")
            ruta2 = os.path.join(carpeta, "reporte2.pdf")
            core.generar_reporte1_pdf(self.resultado, ruta1)
            core.generar_reporte2_pdf(self.resultado, ruta2)
        except Exception as exc:
            messagebox.showerror("Error al generar PDF", str(exc))
            return
        messagebox.showinfo(
            "Éxito", f"Reportes generados:\n{ruta1}\n{ruta2}"
        )
        self.barra_estado.configure(
            text="Reportes PDF generados correctamente."
        )

    def guardar_mongo(self):
        if not self.resultado:
            return
        try:
            id_insertado = core.guardar_en_mongo(self.resultado)
        except Exception as exc:
            messagebox.showerror("Error de MongoDB", str(exc))
            return
        messagebox.showinfo(
            "Éxito",
            f"Tabla de símbolos guardada en MongoDB.\nID: {id_insertado}",
        )
        self.barra_estado.configure(
            text="Tabla de símbolos guardada en MongoDB."
        )


if __name__ == "__main__":
    app = AplicacionAnalizador()
    app.mainloop()