
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter import messagebox, ttk
import numpy as np
from scipy.integrate import odeint
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

import os
import tempfile
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Ecuaciones diferenciales del Modelo Ross-Macdonald
def RossMacdonald(y, t, a, c, M, N, p, g, v):
    P, V = y
    dPdt = (((a/N)*p)*(N-P)*V) - (g*P)
    dVdt = (((a/N)*c)*(M-V)*P) - (v*V)
    return [dPdt, dVdt]

# Calcular R0
def calcular_R0(a, c, M, N, p, g, v):
    return ((M/N) * (a**2) * c * p) / (v * g)

# Calcular Determinante
def calcular_Det(a, c, M, N, p, g, v):
    return (1/N) * (((a**2) * c * p * M) - (N * v * g))


class AplicacionSimulacionDengue:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Software de Simulación de Dengue")
        self.raiz.geometry("1366x769")
        
        self.crear_pantalla_bienvenida()

        #datos históricos por año
        self.datos_historicos = {
            "2020": {
                'M': 15871556, 'N': 3967889, 'a': 0.33333, 'p': 0.22687,
                'c': 0.08058, 'g': 0.14285, 'v': 0.06666,
                'P0': 80, 'V0': 1000
            },
            "2021": {
                'M': 16000000, 'N': 4000000, 'a': 0.35, 'p': 0.23,
                'c': 0.082, 'g': 0.145, 'v': 0.067,
                'P0': 100, 'V0': 1200
            },
            "2022": {
                'M': 16200000, 'N': 4100000, 'a': 0.34, 'p': 0.225,
                'c': 0.081, 'g': 0.144, 'v': 0.0665,
                'P0': 90, 'V0': 1100
            },
            "2023": {
                'M': 16400000, 'N': 4200000, 'a': 0.36, 'p': 0.228,
                'c': 0.083, 'g': 0.146, 'v': 0.068,
                'P0': 110, 'V0': 1300
            },
          "2024": {
                'M': 19000000, 'N': 4300000, 'a': 0.35, 'p': 0.22688, 
                'c': 0.084, 'g': 0.146, 'v': 0.069, 
                'P0': 86, 'V0': 1000
                }
           
        }
        
        # Colores para las gráficas de cada año
        self.colores_anos = {
            "2020": "orange",
            "2021": "red",
            "2022": "green",
            "2023": "purple",
            "2024": "orange"
        }
        
    def crear_pantalla_bienvenida(self):
        # Limpiar widgets existentes
        for widget in self.raiz.winfo_children():
            widget.destroy()
        
        # Título
        titulo = tk.Label(
            self.raiz,
            text="SOFTWARE DE SIMULACIÓN - VECTORES (Mosquitos) Y PERSONAS CONTAGIADAS POR DENGUE EN OAXACA",
            font=("Arial", 16, "bold"),
            fg="red"
        )
        titulo.pack(pady=10)

        # Mensaje de bienvenida
        bienvenido = tk.Label(self.raiz, text="¡BIENVENIDO!", font=("Arial", 36, "bold"), fg="red")
        bienvenido.pack(pady=20)

        # Frames de descripción
        frame_textos = tk.Frame(self.raiz)
        frame_textos.pack(pady=20, padx=20, fill="both", expand=True)

        # Texto 1: Sobre el Proyecto
        texto1_titulo = tk.Label(
            frame_textos,
            text="ACERCA DE ESTE PROYECTO:",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        texto1_titulo.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        texto1 = tk.Label(
            frame_textos,
            text=(
                "Pronostica la dinámica de transmisión del virus del dengue en el estado "
                "de Oaxaca a través del modelo matemático Ross-Macdonald.\n\n"
                "Se le proporcionará resultados precisos sobre el número de personas y "
                "mosquitos infectados, así como resultados sobre cómo es la evolución de "
                "la epidemia en el estado."
            ),
            font=("Arial", 12),
            justify="left",
            wraplength=600
        )
        texto1.grid(row=1, column=0, sticky="w", padx=20)

        # Texto 2: Modelo Ross-Macdonald
        texto2_titulo = tk.Label(
            frame_textos,
            text="MODELO ROSS-MACDONALD:",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        texto2_titulo.grid(row=0, column=1, sticky="w", padx=20, pady=10)

        texto2 = tk.Label(
            frame_textos,
            text=(
                "Este modelo consta de dos ecuaciones diferenciales y consiste en la interacción "
                "de 4 poblaciones distribuidas de la siguiente manera: la población de humanos y "
                "la población de mosquito y estas dos a su vez se dividen en susceptibles e infectados, "
                "esto formando cuatro grupos...\n\n"
                "Además mediante el uso de ecuaciones diferenciales, aproxima el número de personas infectadas "
                "y mosquitos infectados en un tiempo determinado..."
            ),
            font=("Arial", 12),
            justify="left",
            wraplength=600
        )
        texto2.grid(row=1, column=1, sticky="w", padx=20)

        # Configurar columnas
        frame_textos.columnconfigure(0, weight=1)
        frame_textos.columnconfigure(1, weight=1)

        # Botón de simulación
        btn_simulacion = tk.Button(
            self.raiz,
            text="IR A LA SIMULACIÓN",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black",
            command=self.abrir_simulacion,
            width=40,
            height=2
        )
        btn_simulacion.pack(pady=150)

    def generar_pdf(self, fig1, fig2, anos_seleccionados, parametros_entrada, parametros_historicos):
        # Abrir ventana para seleccionar dónde guardar el archivo
        ruta_pdf = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not ruta_pdf:  # Si el usuario cancela o no selecciona una ruta, salir de la función
            messagebox.showinfo("Operación cancelada", "No se seleccionó una ubicación para guardar el PDF.")
            return

        # Crear un directorio temporal para guardar las imágenes
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Guardar las figuras como imágenes PNG
            ruta_grafica1 = os.path.join(tmpdirname, 'grafica1.png')
            ruta_grafica2 = os.path.join(tmpdirname, 'grafica2.png')
            
            fig1.savefig(ruta_grafica1, bbox_inches='tight')  # Guardar la primera figura
            fig2.savefig(ruta_grafica2, bbox_inches='tight')  # Guardar la segunda figura

            # Crear el documento PDF
            doc = SimpleDocTemplate(ruta_pdf, pagesize=letter)
            elementos = []
            estilos = getSampleStyleSheet()

            # Título
            titulo = Paragraph("Simulación de Dengue - Modelo Ross-Macdonald en Oaxaca", estilos['Title'])
            elementos.append(titulo)
            elementos.append(Spacer(1, 12))

            # Datos de los años seleccionados
            datos_tabla = [["Año", "Poblacion\nde\nmosquitos", "Poblacion\nde\nPersonas", "Tasa de\npicadura\npor Mosquito", "Probabilidad\nde\ninfeccion por \nPicadura\nen\nHumanos", "Probabilidad\nde\ninfeccion por \nPicadura\nen\nMosquitos", "Tasa\nde\nRecupercion en\nPersonas", "v", "P0", "V0"]]
            for ano in anos_seleccionados:
                datos = parametros_historicos.get(ano, {})
                datos_tabla.append([
                    ano, 
                    datos.get('M', 'N/A'), datos.get('N', 'N/A'), datos.get('a', 'N/A'), datos.get('p', 'N/A'),
                    datos.get('c', 'N/A'), datos.get('g', 'N/A'), datos.get('v', 'N/A'), 
                    datos.get('P0', 'N/A'), datos.get('V0', 'N/A')
                ])
            
            tabla_anos = Table(datos_tabla)
            tabla_anos.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.blue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 7),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            elementos.append(Paragraph("Datos del Programa Epidemiologico:", estilos['Heading3']))
            elementos.append(tabla_anos)
            elementos.append(Spacer(1, 12))

            # Datos de simulación
            datos_simulacion = [
                ["Parámetro", "Valor"],
                ["Poblacion de\nMosquitos", parametros_entrada.get('M', 'N/A')],
                ["Poblacion de\nPersonas", parametros_entrada.get('N', 'N/A')],
                ["Tasa de picadura\npor Mosquitos", parametros_entrada.get('a', 'N/A')],
                ["Probabilidad de\ninfeccion por \nPicadura en Humanos", parametros_entrada.get('p', 'N/A')],
                ["Probabilidad de\ninfeccion por\nPicadura en Mosquitos", parametros_entrada.get('c', 'N/A')],
                ["Tasa de Recuperasion\nen Personas", parametros_entrada.get('g', 'N/A')],
                ["v", parametros_entrada.get('v', 'N/A')],
                ["P0", parametros_entrada.get('P0', 'N/A')],
                ["V0", parametros_entrada.get('V0', 'N/A')]
            ]
            
            tabla_simulacion = Table(datos_simulacion)
            tabla_simulacion.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.blue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            elementos.append(Paragraph("Datos de Simulación:", estilos['Heading3']))
            elementos.append(tabla_simulacion)
            elementos.append(Spacer(1, 12))

            # Añadir las gráficas al PDF
            elementos.append(Image(ruta_grafica1))  # Agregar la primera gráfica
            elementos.append(Paragraph("Gráfica de Personas Infectadas:", estilos['Heading3']))
            
            
            elementos.append(Image(ruta_grafica2))  # Agregar la segunda gráfica
            elementos.append(Paragraph("Gráfica de Mosquitos Infectados:", estilos['Heading3']))

            # Construir el PDF
            doc.build(elementos)

            # Mostrar mensaje de éxito
            messagebox.showinfo("PDF Generado", f"El archivo se guardó en: {ruta_pdf}")

    def abrir_simulacion(self):
        for widget in self.raiz.winfo_children():
            widget.destroy()

        # Configuración de ventana de simulación
        self.raiz.title("Software de Simulación")
        canvas = None
        canvas2 = None

        # Centrar ventana
        ancho_ventana = 1366
        alto_ventana = 768
        ancho_pantalla = self.raiz.winfo_screenwidth()
        alto_pantalla = self.raiz.winfo_screenheight()
        posicion_superior = int(alto_pantalla / 2 - alto_ventana / 2)
        posicion_derecha = int(ancho_pantalla / 2 - ancho_ventana / 2)
        self.raiz.geometry(f"{ancho_ventana}x{alto_ventana}+{posicion_derecha}+{posicion_superior}")

        # Frames
        frame_controles = tk.Frame(self.raiz)
        frame_controles.pack(side=tk.LEFT, padx=20, pady=20)

        frame_centro_superior = tk.Frame(self.raiz, width=ancho_ventana, height=alto_ventana // 2)
        frame_centro_superior.pack()

        texto_etiqueta = "Software de Simulación - Vectores (Mosquitos) y Personas Contagiados Por Dengue en Oaxaca"
        etiqueta = tk.Label(frame_centro_superior, text=texto_etiqueta, font=("Century Gothic", 16, "bold"), fg="black")
        etiqueta.pack()

        # Frame para los años
        frame_anos = tk.Frame(self.raiz)
        frame_anos.pack(pady=10)

        # Label para los años
        tk.Label(frame_anos, text="Años disponibles", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=5)

        # Variables para los checkboxes
        anos_vars = {}
        anos = ["2020", "2021", "2022", "2023", "2024"]
        
        # Crear checkboxes para cada año
        for ano in anos:
            anos_vars[ano] = tk.BooleanVar()
            tk.Checkbutton(frame_anos, text=ano, variable=anos_vars[ano]).pack(side=tk.LEFT, padx=5)

        frame_grafica = tk.Frame(self.raiz)
        frame_grafica.pack(side=tk.RIGHT, padx=20, pady=20)

        # Etiquetas
        etiquetas = [
            ("Poblacion\nde Mosquitos:", 0),
            ("Poblacion\nde Personas:", 1),
            ("Tasa de\nPicadura\npor Mosquito:", 2),
            ("Probabilidad de\nInfección\npor Picadura\nen Humanos:", 3),
            ("Probailidad de\nInfección\nPor Picadura\nen Mosquitos:", 4), 
            ("Tasa de\nRecuperacion\nde Personas:", 5), 
            ("V:", 6), ("X0:", 7), ("Y0:", 8), ("Tiempo en dias:", 9)
        ]
        for texto, fila in etiquetas:
            tk.Label(frame_controles, text=texto).grid(row=fila, column=0, sticky="e")

        # Campos de entrada
        entradas = {}
        nombres_entradas = ['M', 'N', 'a', 'p', 'c', 'g', 'v', 'P0', 'V0']
        for i, nombre in enumerate(nombres_entradas):
            entradas[nombre] = tk.Entry(frame_controles)
            entradas[nombre].grid(row=i, column=1)

        # Deslizador de tiempo
        escala_tiempo = tk.Scale(frame_controles, from_=0, to=365, resolution=1, orient=tk.HORIZONTAL)
        escala_tiempo.grid(row=9, column=1)

        # Etiquetas R0 y Det
        mensaje_R0 = tk.Label(frame_controles, text="")
        mensaje_R0.grid(row=12, column=1)
        mensaje_Det = tk.Label(frame_controles, text="")
        mensaje_Det.grid(row=14, column=1)

        # Valores predeterminados
        valores_predeterminados = {
            'M': "16200000", 'N': "4100000", 'a': "0.30", 'p': "0.25", 
            'c': "0.95", 'g': "0.145", 'v': "0.0666", 
            'P0': "90", 'V0': "1100"
        }
        for nombre, valor in valores_predeterminados.items():
            entradas[nombre].insert(0, valor)
        escala_tiempo.set(365) 
        
        def graficar_resultados(event=None):
            nonlocal canvas, canvas2
            
            # Obtener valores de las entradas
            try:
                parametros = {nombre: float(entradas[nombre].get()) for nombre in nombres_entradas}
                tiempo = float(escala_tiempo.get())
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos")
                return

            # Resolver ecuaciones diferenciales
            t = np.linspace(1, tiempo, 365)
            y0 = [parametros['P0'], parametros['V0']]
            sol = odeint(RossMacdonald, y0, t, args=(
                parametros['a'], parametros['c'], parametros['M'], parametros['N'], 
                parametros['p'], parametros['g'], parametros['v']
            ))

            # Destruir lienzos existentes si existen
            if canvas is not None:
                canvas.get_tk_widget().destroy()
            if canvas2 is not None:
                canvas2.get_tk_widget().destroy()

            # Calcular R0
            R0 = calcular_R0(**{k: parametros[k] for k in ['a', 'c', 'M', 'N', 'p', 'g', 'v']})
            if R0 > 1:
                mensaje_R0.config(text="> 1: Es una epidemia")
            elif R0 < 1:
                mensaje_R0.config(text="< 1: Tendrá un impacto menor")
            else:
                mensaje_R0.config(text="= 1: Posibilidad de alcanzar indicadores endémicos o no")

            # Calcular Det
            Det = calcular_Det(**{k: parametros[k] for k in ['a', 'c', 'M', 'N', 'p', 'g', 'v']})
            if Det > 0:
                mensaje_Det.config(text="> 0: Es un punto estable")
            else:
                mensaje_Det.config(text="< 0: Es un punto silla")

            # Crear gráficas
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(t, sol[:, 0], 'b', label='Personas Infectadas')
            

            # Graficar líneas para años seleccionados
            anos_seleccionados = [ano for ano in anos if anos_vars[ano].get()]
            for ano in anos_seleccionados:
                datos = self.datos_historicos[ano]
                M_historico = datos['M']
                N_historico = datos['N']
                y0_historico = [datos['P0'], datos['V0']]
                sol_historico = odeint(RossMacdonald, y0_historico, t, args=(
                    datos['a'], datos['c'], M_historico, N_historico, 
                    datos['p'], datos['g'], datos['v']
                ))
                ax.plot(t, sol_historico[:, 0], color=self.colores_anos[ano], 
                       label=f'Infectados {ano}')

            ax.legend(loc='best')
            ax.set_xlabel('Tiempo en dias')
            ax.set_ylabel('Población')
            ax.grid()

            fig2 = Figure(figsize=(6, 4), dpi=100)
            ax2 = fig2.add_subplot(111)
            ax2.plot(t, sol[:, 1], 'r', label='Vectores Infectados')

            # Graficar vectores infectados para años seleccionados
            for ano in anos_seleccionados:
                datos = self.datos_historicos[ano]
                M_historico = datos['M']
                N_historico = datos['N']
                y0_historico = [datos['P0'], datos['V0']]
                sol_historico = odeint(RossMacdonald, y0_historico, t, args=(
                    datos['a'], datos['c'], M_historico, N_historico, 
                    datos['p'], datos['g'], datos['v']
                ))
                ax2.plot(t, sol_historico[:, 1], color=self.colores_anos[ano], 
                        label=f'Vectores {ano}')

            ax2.legend(loc='best')
            ax2.set_xlabel('Tiempo en dias')
            ax2.set_ylabel('Población')
            ax2.grid()

            # Crear lienzos de Tkinter
            canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.LEFT)

            canvas2 = FigureCanvasTkAgg(fig2, master=frame_grafica)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side=tk.LEFT)

            return fig, fig2

        # Frame para botones
        frame_botones = tk.Frame(frame_controles)
        frame_botones.grid(row=16, column=1, pady=15)

        # Botón de gráfico
        boton_graficar = tk.Button(frame_botones, text="Ejecutar simulación", 
                                  command=graficar_resultados,  width=20, height=2)
        boton_graficar.pack(pady=5)

        # Botón de generar PDF
        def pdf_callback():
            anos_seleccionados = [ano for ano in anos if anos_vars[ano].get()]
            parametros_entrada = {nombre: entradas[nombre].get() for nombre in nombres_entradas}
            parametros_historicos_seleccionados = {ano: self.datos_historicos[ano] for ano in anos_seleccionados}
            
            figs = graficar_resultados()
            if figs:
                self.generar_pdf(figs[0], figs[1], anos_seleccionados, parametros_entrada, self.datos_historicos)

        boton_pdf = tk.Button(frame_botones, text="Generar PDF", 
                              command=pdf_callback, width=20, height=2)
        boton_pdf.pack(pady=5)

        # Botón de inicio 
        boton_inicio = tk.Button(frame_botones, text="Inicio", 
                                command=self.crear_pantalla_bienvenida,  width=20, height=2)
        boton_inicio.pack(pady=5)

        # Vincular la función graficar_resultados a los checkboxes
        for ano in anos:
            anos_vars[ano].trace_add('write', lambda *args: graficar_resultados())

raiz = tk.Tk()
aplicacion = AplicacionSimulacionDengue(raiz)
raiz.mainloop()