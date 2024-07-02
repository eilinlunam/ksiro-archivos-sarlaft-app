from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from openpyxl import Workbook
import pandas as pd
import os
import shutil
from openpyxl.styles import NamedStyle
from openpyxl import load_workbook
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración de la carpeta de subida
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def vaciar_carpeta(ruta_carpeta):
    try:
        # Verificar si la carpeta existe
        if os.path.exists(ruta_carpeta):
            # Eliminar todos los archivos y subcarpetas dentro de la carpeta
            for archivo in os.listdir(ruta_carpeta):
                archivo_ruta = os.path.join(ruta_carpeta, archivo)
                if os.path.isfile(archivo_ruta):
                    os.remove(archivo_ruta)
                elif os.path.isdir(archivo_ruta):
                    shutil.rmtree(archivo_ruta)
            print(f'Carpeta {ruta_carpeta} vaciada correctamente.')
        else:
            print(f'La carpeta {ruta_carpeta} no existe.')
    except Exception as e:
        print(f'Ocurrió un error al vaciar la carpeta {ruta_carpeta}: {str(e)}')

# Ruta de la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la subida de archivos
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Verificar si se reciben los archivos file1 y file2
        if 'file1' not in request.files or 'file2' not in request.files:
            session['error_message'] = 'Debe subir ambos archivos.'
            return redirect('/')
        
        file1 = request.files['file1']
        file2 = request.files['file2']

        # Verificar si los archivos son válidos y están presentes
        if file1.filename == '' or file2.filename == '':
            session['error_message'] = 'Debe subir ambos archivos.'
            return redirect('/')
        
        if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
            # Limpiar la carpeta de subida antes de guardar los nuevos archivos
            vaciar_carpeta(app.config['UPLOAD_FOLDER'])

            # Guardar los archivos en la carpeta de subida
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)

            filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
            filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
            
            file1.save(filepath1)
            file2.save(filepath2)

            # Capturar la opción seleccionada
            opcion_seleccionada = request.form['menu']
            mes_seleccionado = request.form['mes']
            year_seleccionado = request.form['year']
            historico = request.form.get('historico', 'false')  # Valor por defecto 'false' si no se selecciona

            b1, b2 = modify_files(filepath1, filepath2, opcion_seleccionada)                
            
            if isinstance(b1, str):
                flash(b2,'error')
                return redirect('/')
            
            # Nombres ARCHIVOS
            if historico=="true":
                filepath11 = "Clientes Histórico.xlsx"
                if opcion_seleccionada=="OPA":
                    filepath22 = "T-Histórico OPA.xlsx"
                else:
                    filepath22 = "T-Histórico Visionamos.xlsx" 
            else:
                filepath11 = f"Clientes-"+mes_seleccionado+year_seleccionado+".xlsx"
                if opcion_seleccionada=="OPA":
                    filepath22 = "T-"+mes_seleccionado+year_seleccionado+" OPA.xlsx"
                else:
                    filepath22 = "T-"+mes_seleccionado+year_seleccionado+" Visionamos.xlsx" 
            
            # Guardando archivos
            save_excel(b1, filepath11, "Cliente")
            save_excel(b2, filepath22, "Transacciones")
            
            return render_template('download.html', filename1=filepath11, filename2=filepath22)
        

# Ruta para manejar la subida de archivos
@app.route('/join', methods=['POST'])
def join_file():
    if request.method == 'POST':
        # Verificar si se reciben los archivos file1 y file2
        if 'file1' not in request.files or 'file2' not in request.files:
            session['error_message'] = 'Debe subir ambos archivos.'
            return redirect('/')
        
        file1 = request.files['file1']
        file2 = request.files['file2']

        # Verificar si los archivos son válidos y están presentes
        if file1.filename == '' or file2.filename == '':
            session['error_message'] = 'Debe subir ambos archivos.'
            return redirect('/')
        
        if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
            # Limpiar la carpeta de subida antes de guardar los nuevos archivos
            vaciar_carpeta(app.config['UPLOAD_FOLDER'])

            # Guardar los archivos en la carpeta de subida
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)

            filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
            filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
            
            file1.save(filepath1)
            file2.save(filepath2)

            # Capturar la opción seleccionada
            mes_seleccionado = request.form['mes']
            year_seleccionado = request.form['year']
            historico = request.form.get('historico', 'false')  # Valor por defecto 'false' si no se selecciona

            df = join_files(filepath1, filepath2)                
                        
            # Nombres ARCHIVOS
            if historico=="true":
                filepath = "T-Histórico (All).xlsx"
            else:
                filepath = "T-"+mes_seleccionado+year_seleccionado+" (All).xlsx" 
            
            # Guardando archivos
            save_excel(df, filepath, "Datos")
            return render_template('download2.html', filename1=filepath)
        
        
def modify_files(filename1, filename2, opcion):

    valor = True if opcion=="VISIONAMOS" else False

    # Paso 1: Leer informe Excel Clientes
    f1 = pd.read_excel(filename1)
    f1.columns = [str(i).strip() for i in f1.columns] # Removiendo espacios en columnas
    f1 = f1.rename(columns={"NIT":"CEDULA", 
                            "Cedula":"CEDULA",
                            "NOMBREINTE":"Nombre y apellido", 
                            "AGENCIA":"COD. AGENCIA",
                            "CODCIUDAD": "COD AGENCIA_2"})
    f1["CEDULA"] = f1["CEDULA"].astype('int64', errors='ignore')  # Convirtiendo cédula a entero

    # Paso 2: Leer informe Excel Transacciones
    f2 = pd.read_excel(filename2)
    f2.columns = [str(i).strip() for i in f2.columns] # Removiendo espacios en columnas
    f2.columns = [col.upper() for col in f2.columns]
        
    f2 = f2.rename(columns={"CEDULA":"DOCUMENTO1", "TOTAL EFECTIVO":"VALOR", "TIPO DE MOVIMIENTO":"OPERACION",
                        "AGENCIA1": "COD. AGENCIA", "TIPODEMOVIMIENTO":"OPERACION", "TOTALEFECTIVO": "VALOR",
                        "NATURALEZA":"OPERACION", "CODAGENCIA":"COD. AGENCIA", "CODLINEA":"PRODUCTO",
                        "AGENCIA2": "COD. AGENCIA_2", "AGENCIA": "COD. AGENCIA_0", "OPERACIÓN":"OPERACION"})
        
    if opcion=="VISIONAMOS":
        f2 = f2.rename(columns={"DOCUMENTO":"DOCUMENTO1"})

    if "DOCUMENTO1" not in f2.columns:
        mje='El archivo no encuentra el campo CÉDULA, asegúrese que la BD es tipo OPA'
        return 'error', mje
    
    if "PRODUCTO" not in f2.columns:
        mje='El archivo de Transacciones no tiene el campo PRODUCTO'
        flash(mje,'warning')
        #return redirect('/')

    f2["OPERACION"] = f2["OPERACION"].apply(lambda x: "CREDITO" if "CNGC" in x else x)
    f2["OPERACION"] = f2["OPERACION"].apply(lambda x: "DEBITO" if "RETC" in x else x)
    f2["OPERACION"] = f2["OPERACION"].apply(lambda x: "CREDITO" if "C" in x else "DEBITO")
    if 'DISPOSITIVO' not in f2.columns: f2['DISPOSITIVO']=''    
    if "ESTADO" in f2.columns: f2 = f2[f2["ESTADO"]=="APROBADA"]
    
    if 'FECHA_REGISTRO' in f2.columns: 
        f2 = f2.rename(columns={'FECHA_REGISTRO':'FECHA'})
        formato = "%Y%m%d"
        f2["FECHA"] = pd.to_datetime(f2['FECHA'], format=formato) 
    else:
        try:
            if opcion=="VISIONAMOS": 
                formato = "%Y%m%d"  
            f2["FECHA"] = pd.to_datetime(f2['FECHA'], format=formato) 
        except:
            f2["FECHA"] = pd.to_datetime(f2['FECHA'])   
    
    f2['Mes'] = f2['FECHA'].dt.to_period('M')  # Extrayendo el mes de la fecha
    f2["DOCUMENTO1"] = f2["DOCUMENTO1"].astype('int64') # Convirtiendo documento a entero
    f2['CANAL'] = f2['CANAL'] + ' ' + f2['DISPOSITIVO'] if 'CANAL' in f2 else 'Taquilla'
    if valor: 
        f2['VALOR'] = f2['VALOR']/100
    condAgencia = 1 if "COD. AGENCIA" in f2.columns else 0
    condAgencia = 1 if "COD. AGENCIA" in f2.columns else 0
    condAgencia1 = 1 if "COD. AGENCIA_1" in f2.columns else 0
    condAgencia2 = 1 if "COD. AGENCIA_2" in f2.columns else 0
    condProducto = 1 if "PRODUCTO" in f2.columns else 0

    # Paso 3: Extrayendo datos de clientes
    b1 = f1[["CEDULA", "Nombre y apellido"]].copy()
    for col in ["Ingresos", "Egresos", "Activos", "Pasivos"]:
        b1[col] = f1[col].values if col in f1.columns else 0
    b1["Codigo"] = 0 # Código actividad económica: CERO
    b1 = b1.fillna(0)

    # Paso 4: Extrayendo datos de transacciones
    cols = ['DOCUMENTO1', 'Mes', 'OPERACION', 'CANAL', 'VALOR']
    if condAgencia: cols=cols[:-1]+["COD. AGENCIA", "VALOR"]
    if condProducto: cols=cols[:-1]+["PRODUCTO", "VALOR"]
    f2 = f2[cols] # Extrayendo columnas

    # Agrupando por documento, mes, operacion y canal: (Hallando conteo y suma del valor)
    b2 = f2.groupby(cols[:-1]).agg({'count', 'sum'}).reset_index()
    b2.columns = b2.columns.droplevel(level=0)

    # Renombrando nuevamente las columnas (Por la agrupacion se borraron los nombres)
    b2.columns.values[:len(cols)-1] = cols[:-1]
    b2 = b2.rename(columns={"sum":"VALOR", "count":"N_VALOR"})

    # Creando variable productos
    if condProducto==0: b2["PRODUCTO"] = "Ahorros"
    b2["DOCUMENTO1"] = b2["DOCUMENTO1"].astype('int64', errors='ignore') # Convirtiendo documento a entero

    # Agregando columna jurisdiccion (COD. AGENCIA) a los datos desde clientes
    if condAgencia==0:
        b2 = pd.merge(b2, f1[['CEDULA', 'COD. AGENCIA']], left_on='DOCUMENTO1', right_on='CEDULA', how='left')
        b2 = b2.drop("CEDULA", axis=1)
    if condAgencia1==0:
        try:        
            sf1 = f1[['CEDULA', 'COD AGENCIA_1']].drop_duplicates(subset=['CEDULA'])
            sf1 = dict(zip(sf1['CEDULA'], sf1['COD AGENCIA_1']))
            b2['COD AGENCIA_1'] = b2['DOCUMENTO1'].apply(lambda x: sf1[x] if x in sf1 else 'N.A.') 
        except: 
            b2["COD AGENCIA_1"] = ""
            
    if condAgencia2==0:
        try:
            sf2 = f1[['CEDULA', 'COD AGENCIA_2']].drop_duplicates(subset=['CEDULA'])
            sf2 = dict(zip(sf2['CEDULA'], sf2['COD AGENCIA_2']))
            b2['COD AGENCIA_2'] = b2['DOCUMENTO1'].apply(lambda x: sf2[x] if x in sf2 else 'N.A.') 
        except: 
            b2["COD AGENCIA_2"] = ""        


    # Renombrar columnas debito y creditos
    columns = ["Mes", "DOCUMENTO1", "N_VALOR", "VALOR", "PRODUCTO", 'CANAL',
            "COD. AGENCIA", 'COD AGENCIA_1', 'COD AGENCIA_2']
    b21 = b2[b2["OPERACION"]=="DEBITO"][columns].rename(columns={"Mes":"Fecha", "DOCUMENTO1":"CEDULA", 
                                                                'CANAL':"CANAL", "N_VALOR":"N_DEBITO",
                                                                "VALOR":"SUMA_DEBITO", "COD. AGENCIA":"JURISDICCION",
                                                                "COD AGENCIA_1":"JURISDICCION1", "COD AGENCIA_2":"JURISDICCION2"})

    b22 = b2[b2["OPERACION"]=="CREDITO"][columns].rename(columns={"Mes":"Fecha", "DOCUMENTO1":"CEDULA", 
                                                                'CANAL':"CANAL", "N_VALOR":"N_CREDITO",
                                                                "VALOR":"SUMA_CREDITO", "COD. AGENCIA":"JURISDICCION",
                                                                "COD AGENCIA_1":"JURISDICCION1", "COD AGENCIA_2":"JURISDICCION2"})
        
    # Concatenando columnas debito, creditos y ordenando
    b2 = pd.concat([b21, b22]).fillna(0).sort_values(by=["CEDULA", "Fecha"])
    b2 = b2[["Fecha", "CEDULA", "N_DEBITO", "SUMA_DEBITO", "N_CREDITO", 
            "SUMA_CREDITO", "PRODUCTO", "CANAL", "JURISDICCION", "JURISDICCION2"]]

    return b1, b2

def join_files(filename1, filename2):
    f1 = pd.read_excel(filename1)
    f2 = pd.read_excel(filename2)

    f1["BD"] = "OPA"
    f2["BD"] = "VISIONAMOS"

    df = pd.concat([f1, f2])
    df = df.sort_values(by=["CEDULA", "Fecha"])

    return df

# Función para modificar el archivo Excel cambiando el nombre de la hoja
def save_excel(df, filename, sheetname):
    columnas_pesos = ["Ingresos", "Egresos", "Activos", "Pasivos", "SUMA_DEBITO", "SUMA_CREDITO"]
    # Crear un escritor de Excel usando pandas
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name=sheetname)
    workbook = writer.book
    worksheet = writer.sheets[sheetname]
    formato_moneda = workbook.add_format({'num_format': '$#,##0.00'})
    for idx, col in enumerate(df):
        series = df[col]
        max_len = max((series.astype(str).map(len).max(),  len(str(series.name)))) + 2
        if col in columnas_pesos:
            worksheet.set_column(idx, idx, max_len+2, formato_moneda)
        else:
            worksheet.set_column(idx, idx, max_len)
    writer.close()

# Ruta para descargar los archivos subidos
@app.route('/download/<filename>')
def download_files(filename):
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
