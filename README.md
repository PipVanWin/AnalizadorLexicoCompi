# Proyecto Corto #1 – Analizador Estático de Código (Kotlin)
Compiladores – Universidad Mesoamericana, Campus Quetzaltenango

Analizador léxico construido con **flex**, envuelto en una interfaz gráfica
en **Python (Tkinter y CustomerTkinter)** que genera dos reportes en **PDF** y guarda la tabla
de símbolos en **MongoDB**. El lenguaje de entrada analizado es **Kotlin**.

## Estructura del proyecto

```

lexer.l          # Analizador léxico con flex
Makefile          # Compila lexer.l - ejecutable "analizador"
core.py           # Lógica: ejecuta el analizador, calcula stats, PDFs, Mongo
gui.py            # Interfaz gráfica Tkinter es el punto de entrada
requirements.txt  # Dependencias Python
ejemplo/
ejemplo.kt        # Código fuente Kotlin de prueba 
docs/
ejemplos_reportes/
reporte1_ejemplo.pdf
reporte2_ejemplo.pdf
.gitignore
README.md
```

## 1. Requisitos previos para Linux

```bash
sudo apt-get update
sudo apt-get install -y flex gcc python3 python3-pip python3-tk

# MongoDB 
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo docker run -d --name mongo-proyecto -p 27017:27017 mongo:latest

Instalar las dependencias de Python:

```bash
cd src
pip3 install -r requirements.txt --break-system-packages
```

## 2. Compilar el analizador léxico

```bash
cd src
make
```

Esto genera `lex.yy.c` el cual es codigo C producido por flex y luego el ejecutable
**`analizador`**. Se puede probar directamente desde la terminal

```bash
./analizador ../ejemplo/ejemplo.kt
```

Se verá una línea por cada lexema encontrado, con el formato interno
`LEXEMA<0x01>LINEA<0x01>TOKEN<0x01>CATEGORIA` el carácter `0x01` es
invisible en la terminal; es un separador de campos para evitar
conflictos con comillas u otros símbolos dentro del código analizado

Para limpiar los archivos generados:

```bash
make clean
```

## 3. Ejecutar la interfaz gráfica

Con MongoDB corriendo y el ejecutable ya compilado:

```bash
cd src
make
python3 gui.py
```

Flujo dentro de la aplicación:

1. **"Abrir archivo Kotlin (.kt)"** → selecciona `ejemplo/ejemplo.kt` o
   cualquier otro archivo `.kt` con al menos 75 líneas.
2. Revisar las pestañas **Resumen**, **Detalle de lexemas** y
   **Tabla de símbolos**.
3. **"Generar Reportes PDF"** → elegir una carpeta destino; se crean
   `reporte1.pdf` estadísticas generales y `reporte2.pdf` detalle de
   lexemas + tabla de símbolos
4. **"Guardar tabla de símbolos en MongoDB"**  inserta un documento en
   `compiladores_proyecto1.tabla_simbolos` con los identificadores
   únicos encontrados.

## 4. Cómo mapea el código a los requisitos del proyecto

 Analizador léxico con flex                                    `src/lexer.l`                                          
 Palabras reservadas                                    72 palabras clave de Kotlin, categoría `RESERVADA`     
 Identificadores con repetidos                                Categoría `IDENTIFICADOR`, se cuentan todas las ocurrencias 
 Enteros, Flotantes, Booleanos, Cadenas                     Categorías `ENTERO`, `FLOTANTE`, `BOOLEANO`, `CADENA`   
 Operadores mínimo 10, con token específico                 33 operadores, cada uno con su propio token (`OP_...`)
 GUI para abrir, procesar y mostrar resultados                  `src/gui.py`                                            
 Reporte 1 conteos + palabras reservadas descendente          `core.generar_reporte1_pdf`                             
 Reporte 2 lexema + línea + token, y tabla de símbolos         `core.generar_reporte2_pdf`                             
 Tabla de símbolos en MongoDB                                   `core.guardar_en_mongo`                                 


## 5. Notas y decisiones de diseño

- `true` y `false` se cuentan en la categoría **BOOLEANO**, no en
  **RESERVADA** aunque técnicamente en Kotlin son palabras clave.
- Los comentarios (`//` y `/* */`) se reconocen y se descartan, no
  cuentan como lexemas en ningún reporte.
- El conteo de **caracteres** se hace sobre el archivo completo es decir todo el
  contenido, incluyendo espacios y saltos de línea, y el conteo de
  **líneas** es el número de líneas del archivo fuente.
- La tabla de símbolos guarda identificadores **únicos**, con la línea
  de su primera aparición y el número total de ocurrencias.
- Los strings de una sola comilla se procesan con manejo de secuencias
  de escape (`\"`, `\n`, etc.) también hay soporte básico para los
  strings triples de Kotlin (`"""texto"""`).

