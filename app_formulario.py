#==========================================================================================================================================
# 24/Mayo/2024
# autor: @eilinlunam
# Clase objetos
#==========================================================================================================================================

from IPython.display import HTML, FileLink, clear_output
import ipywidgets as widgets
from ipyfilechooser import FileChooser
import os
import pandas as pd
from app import save_excel

class App1:
    
    def __init__(self):
        
        # CREANDO OBJETO TÍTULO: MODELO DE REFERENCIA EN HTML
        t1 = "<h1 style='text-align:center'><span style='font-size:36px'><strong>MODELO DE REFERENCIA</strong><hr/></span></h1>"
        self.titulo1 = widgets.HTML(value=t1, layout=widgets.Layout(width='90%'))

        # CREANDO OBJETO TEXTO: INGRESE X ARCHIVO... EN HTML 
        tipoLetra = "<span style='font-family:Georgia,serif'>"
        TamanoLetra = "<span style='font-size:16px'>"
        t1 = ("<p>"+TamanoLetra+tipoLetra+"Ingrese el archivo (EXCEL) con los datos "+
              " correspondiente a la Base de Datos <strong>OPA</strong>. </span></span></p>")
        t2 = ("<p>"+TamanoLetra+tipoLetra+"Ingrese el archivo (EXCEL) con los datos "+
              " correspondiente a la Base de Datos <strong>VISIONAMOS</strong>. </span></span></p>")

        self.texto1 = widgets.HTML(value=t1, layout=widgets.Layout(width='80%'))
        self.texto2 = widgets.HTML(value=t2, layout=widgets.Layout(width='80%'))


        # CREANDO OBJETO DESPLEGAR ESCOGEDOR DE ARCHIVOS
        self.chooser1 = FileChooser(os.getcwd(), layout=widgets.Layout(width='100%'))
        self.chooser2 = FileChooser(os.getcwd(), layout=widgets.Layout(width='100%'))

        # CREANDO OBJETO BOTON CALCULAR
        self.boton1 = widgets.Button(description='CALCULAR', button_style='info', 
                                     layout=widgets.Layout(width='60%'))
        self.Boton1 = widgets.Box(children=[self.boton1], layout=widgets.Layout(display='flex', flex_flow ='column',
                                                   overflow_y='auto', align_items='center',
                                                   width='90%'))
        self.boton1.on_click(self.calcularBD)

        # CREANDO OBJETO SALIDAS/ESPACIOS
        self.out = widgets.Output()

        # Colores
        self.color1 = 'cornflowerblue'
        self.color2 = 'goldenrod'
        self.color3 = 'mediumseagreen'

        display(self.texto1, self.chooser1, self.texto2, self.chooser2, self.Boton1, self.out)
        
    # CLICK EN CALCULAR BASE DE DATOS
    def calcularBD(self, b):
        
        with self.out:
            
            # LIMPIANDO VENTANAS
            self.out.clear_output()
             
            # EXTRAYENDO NOMBRE O RUTA DE LOS ARCHIVOS SELECCIONADOS
            file1 = str(self.chooser1.selected)
            file2 = str(self.chooser2.selected)
            
            if file1=="None" or file2=="None":
                print("No se han seleccionado archivos")
                return
            
            f1 = pd.read_excel(file1)
            f2 = pd.read_excel(file2)

            f1["BD"] = "OPA"
            f2["BD"] = "VISIONAMOS"

            df = pd.concat([f1, f2])
            df = df.sort_values(by=["CEDULA", "Fecha"])

            filepath = "BDresultante.xlsx"
            save_excel(df, filepath, "Transacciones")
            enlace = FileLink(filepath)
            print("Guardado")
            display(enlace)
            return