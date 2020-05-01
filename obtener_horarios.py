from datetime import datetime
from datetime import timedelta

def obtener_consultorios(_consulta):
    contador = 0
    consultorios = list()
    temp = _consulta[0][0]
    consultorios.append(temp)
    while contador < len(_consulta):
        if _consulta[contador][0] != temp:
            temp = _consulta[contador][0]
            consultorios.append(temp)
        contador = contador + 1
    return consultorios



def obtener_fechas(fecha_inicial, fecha_final):
    fechas = list()
    referencia = datetime(2020,1,1,21,0,0)
    while fecha_inicial <= fecha_final:
        fechas.append(fecha_inicial)
        fecha_inicial = fecha_inicial + timedelta(minutes=30)
        if fecha_inicial.hour == referencia.hour:
            fecha_inicial = fecha_inicial + timedelta(hours=10)
    return fechas

def obtener_fechas_consultorio(_consul, _consulta):
    contador = 0
    while contador < len(_consulta):
        if _consulta[contador][0] == _consul:
            return obtener_fechas(_consulta[contador][1], _consulta[contador][2])
        contador = contador + 1
    return []

def verificar_fecha(_fecha, _fechas):
    if _fecha in _fechas:
        return True
    else:
        return False


def info_consultorio(_consu, _consulta):
    info = list()
    contador = 0
    while contador < len(_consulta):
        if _consulta[contador][0] == _consu:
            info.append(_consulta[contador][0]) #nro consultorio
            info.append(_consulta[contador][4]) #documento doctor
            info.append(_consulta[contador][5]) #nombre doctor
            return info
        contador = contador + 1
    return []


def generar_horarios(_consultorios, _consulta):
    _horarios = {}
    contador1 = 0
    contador2 = 0
    while contador1 < len(_consultorios):
        temp = obtener_fechas_consultorio(_consultorios[contador1], _consulta)
        while contador2 < len(_consulta):
            if _consulta[contador2][0] == _consultorios[contador1]:
                if verificar_fecha(_consulta[contador2][3], temp) == True:
                    temp.remove(_consulta[contador2][3])
            contador2 = contador2 + 1
        if len(temp) != 0:
            _info = info_consultorio(_consultorios[contador1], _consulta)
            contador3 = 0
            h_temp = list()
            while contador3 < len(temp):
                plantilla = {
                    'nombre doctor': _info[2], 
                    'documento doctor': _info[1], 
                    'fecha cita': temp[contador3].strftime("%d-%b-%Y %H:%M:%S")
                }
                h_temp.append(plantilla)
                contador3 = contador3 + 1
            _horarios[_info[0]] = h_temp
        contador1 = contador1 + 1
    return _horarios

        




if __name__ == '__main__':
    fech1 = datetime(2020,4,1,7,0,0)
    fech2 = datetime(2020,4,30,21,0,0)
    fech3 = datetime(2021,4,1,7,0,0)
    print(obtener_fechas(fech1, fech2))
    #print(verificar_fecha(fech3, obtener_fechas(fech1, fech2)))