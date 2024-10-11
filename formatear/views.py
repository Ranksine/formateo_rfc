from django.http import HttpResponse
from django.shortcuts import render
from .forms import MainForm

from openpyxl import Workbook
import pandas as pd
from datetime import datetime
import sys
import re

def index(request):
    if request.method == 'POST':
        form = MainForm(request.POST, request.FILES)
        if form.is_valid():
            archivini = request.FILES['sel_archivo']
            
            df = pd.read_excel(archivini)
            rfc_col = []
            for idx, row in df.iterrows():
                paterno = row['PATERNO']
                materno = row['MATERNO']
                nombre = row['NOMBRE']
                sexo = row['SEXO']
                
                try:
                    f_nac = row['F_NAC']
                    fecha_nacimiento = str(f_nac)[:10]
                    fecha_nac_formated = formatearRFC(str(f_nac))
                    paterno_filtred = paterno.strip()
                    materno_filtred = materno.strip()
                    nombre_filtred = nombre.strip()
                    
                    homonimia_code = homonimia(paterno_filtred, materno_filtred, nombre_filtred)
                    iniciales =get_iniciales(paterno_filtred, materno_filtred, nombre_filtred)
                            
                    rfc12 = f"{iniciales}{fecha_nac_formated[:6]}{homonimia_code}"
                    rfc = calcular_digito_verificador(rfc12)
                    
                    print(f"""
                            Información de la fila:
                                - Nombre completo: {nombre_filtred} {paterno_filtred} {materno_filtred}
                                - Siglas nombre: {iniciales}
                                - Fecha de nacimiento: {fecha_nacimiento}
                                - Codigo de homonimia: {homonimia_code}
                                - RFC final: {rfc}
                          """)
                    
                    rfc_col.append(rfc)
                    df['RFC_13'] = rfc_col
                except Exception as e:
                    print('Fin del archivo: {e}')
            print(f'Todos RFC: {rfc_col}')
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=RFC_Generados.xlsx'
            df.to_excel(response, index=False)
            return response     
    else:
        form = MainForm()
        return render(request, 'index.html', {'form': form})

def formatearRFC(fecha):
    try:
        # Asume que la fecha tiene el formato YYYY-MM-DD
        año, mes, dia = fecha.split('-')
        return f"{año[2:]}{mes}{dia}"
    except ValueError as e:
        return "Fecha inválida"
    except Exception:
        print('Excepcion en formatear RFC.')
        return "Fecha inválida Excepcion"

def formateo_nueva_fecha(fecha):
    try:
        fecha = datetime.strptime(fecha, "%Y-%m-%d")
        return fecha.strftime("%d/%m/%Y")
    except ValueError:
        return "Fecha inválida"

def filtrar_nombres_RFC(str_texto):
    """Filtra una cadena de texto para obtener un nombre adecuado para un RFC.

    Args:
        str_texto: La cadena de texto a filtrar.

    Returns:
        str: La cadena filtrada.
    """

    # Lista de palabras a eliminar (mejorada para incluir expresiones regulares)
    palabras_a_eliminar = r"\b(?:de|del|la|los|las|y|mc|mac|von|van|j|jose|maria|mi|i|o|o'|e|ma)\b"

    # Eliminar espacios en blanco adicionales
    str_texto = ' '.join(str_texto.split())

    # Eliminar artículos y conectores usando expresiones regulares
    str_texto = re.sub(palabras_a_eliminar, "", str_texto, flags=re.IGNORECASE)
        
    if str_texto.startswith('ch'):
        str_texto = str_texto.replace('ch', 'c')
    elif str_texto.startswith('ll'):
        str_texto = str_texto.replace('ll', 'l')
        
    return str_texto

def get_iniciales(paterno, materno, nombre):
    paterno = filtrar_nombres_RFC(paterno)
    materno = filtrar_nombres_RFC(materno)
    
    primera_paterno = paterno[0].upper()
    
    vocales = "AEIOUaeiou"
    primera_vocal_paterno = next((letra for letra in paterno[1:] if letra in vocales), '').upper()
    
    primera_materno = materno[0].upper()
    
    nombre_list = nombre.strip().split()
    
    if nombre_list[0].lower() in ['jose', 'maria'] and len(nombre_list) >= 2:
            primera_nombre = filtrar_nombres_RFC(' '.join(nombre_list[1:]).upper())
            primera_nombre = primera_nombre[:1]
    else:
        primera_nombre = nombre_list[0][0].upper()
    
    codigo = primera_paterno + primera_vocal_paterno + primera_materno + primera_nombre
    
    return codigo
    

def homonimia(ap_paterno, ap_materno, nombre):
    nombre_completo = f"{ap_paterno.strip()} {ap_materno.strip()} {nombre.strip()}"
    numero = '0'
    numeroSuma = 0
    letras_a_numeros = {
        'ñ': '10', 'ü': '10', 'a': '11', 'b': '12', 'c': '13', 'd': '14', 'e': '15',
        'f': '16', 'g': '17', 'h': '18', 'i': '19', 'j': '21', 'k': '22', 'l': '23',
        'm': '24', 'n': '25', 'o': '26', 'p': '27', 'q': '28', 'r': '29', 's': '32',
        't': '33', 'u': '34', 'v': '35', 'w': '36', 'x': '37', 'y': '38', 'z': '39',
        ' ': '00'
    }

    for letra in nombre_completo.lower():
        numero += letras_a_numeros.get(letra, '00')
    
    for i in range(len(numero) - 1):
        numero1 = int(numero[i:i + 2])
        numero2 = int(numero[i + 1:i + 2])
        numeroSuma += numero1 * numero2
    
    numero3 = numeroSuma % 1000
    numero4 = numero3 // 34
    numero5 = int(numero4)
    numero6 = numero3 % 34
    
    numeros_a_letras = {
        0: '1', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8', 8: '9', 9: 'A',
        10: 'B', 11: 'C', 12: 'D', 13: 'E', 14: 'F', 15: 'G', 16: 'H', 17: 'I', 18: 'J', 
        19: 'K', 20: 'L', 21: 'M', 22: 'N', 23: 'P', 24: 'Q', 25: 'R', 26: 'S', 27: 'T',
        28: 'U', 29: 'V', 30: 'W', 31: 'X', 32: 'Y', 33: 'Z'
    }
    
    homonimio = numeros_a_letras.get(numero5, '')
    homonimio += numeros_a_letras.get(numero6, '')

    return homonimio

def calcular_digito_verificador(rfc):
    rfcsuma = []
    nv = 0
    
    # Mapear cada carácter del RFC a un valor numérico
    valores = {
        '0': '00', '1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06', '7': '07', '8': '08', '9': '09',
        'A': '10', 'B': '11', 'C': '12', 'D': '13', 'E': '14', 'F': '15', 'G': '16', 'H': '17', 'I': '18', 'J': '19',
        'K': '20', 'L': '21', 'M': '22', 'N': '23', '&': '24', 'O': '25', 'P': '26', 'Q': '27', 'R': '28', 'S': '29',
        'T': '30', 'U': '31', 'V': '32', 'W': '33', 'X': '34', 'Y': '35', 'Z': '36', ' ': '37', 'Ñ': '38'
    }

    # Convertir cada letra a su número correspondiente y agregarlo a rfcsuma
    for letra in rfc:
        rfcsuma.append(int(valores.get(letra, '00')))

    # Calcular el número verificador
    y = 0
    for i in range(13, 1, -1):
        nv += rfcsuma[y] * i
        y += 1

    nv = nv % 11

    # Determinar el dígito verificador según el resultado
    if nv == 0:
        rfc += '0'
    else:
        nv = 11 - nv
        if nv == 10:
            rfc += 'A'
        else:
            rfc += str(nv)

    return rfc
