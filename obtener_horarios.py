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
    principal = list()
    consultorio = {}
    contador1 = 0
    contador2 = 0
    now = datetime.now()
    while contador1 < len(_consultorios):
        _info = info_consultorio(_consultorios[contador1], _consulta)
        consultorio["name"] = "consultorio " + str(_info[0])
        consultorio["availableAppointment"] = None
        temp = obtener_fechas_consultorio(_consultorios[contador1], _consulta)
        while contador2 < len(_consulta):
            if _consulta[contador2][0] == _consultorios[contador1]:
                if verificar_fecha(_consulta[contador2][3], temp) == True or _consulta[contador2][3] < now:
                    temp.remove(_consulta[contador2][3])
            contador2 = contador2 + 1
        if len(temp) != 0:
            horarios = list()
            contador3 = 0
            while contador3 < len(temp):
                plantilla = {
                    'doctorName': _info[2], 
                    'doctorDocument': _info[1], 
                    'date': temp[contador3].strftime("%d-%b-%Y %H:%M:%S")
                }
                horarios.append(plantilla)
                contador3 = contador3 + 1
            consultorio["availableAppointment"] = horarios      
            principal.append(consultorio)     
        contador1 = contador1 + 1
    return principal







def obtener_horarios2(_consul, _consulta, _horarios):
    contador = 0
    contador2 = 0
    contador3 = 0
    consultorio = {}
    while contador < len(_consul):
        while contador2 < len(_consulta):
            if _consul[contador] == _consulta[contador2][0]:
                consultorio["name"] = "consultorio " + str(_consulta[contador2][0])
                consultorio["availableAppointment"] = None
                temp = obtener_fechas(_consulta[contador2][1], _consulta[contador2][2])
                horarios = list()
                while contador3 < len(temp):
                    plantilla = {
                        'doctorName': _consulta[contador2][4], 
                        'doctorDocument': _consulta[contador2][3], 
                        'date': temp[contador3].strftime("%d-%b-%Y %H:%M:%S")
                    }
                    horarios.append(plantilla)
                    contador3 = contador3 + 1
                consultorio["availableAppointment"] = horarios
                _horarios.append(consultorio)
            contador2 = contador2 + 1
        
        contador = contador + 1
    return _horarios






def obtener_horarios3(_consulta):
    contador = 0
    principal = list()
    while contador < len(_consulta):
        consultorio = {}
        consultorio["name"] = "consultorio " + str(_consulta[contador][0])
        consultorio["availableAppointment"] = None
        temp = obtener_fechas(_consulta[contador][1], _consulta[contador][2])
        horarios = list()
        contador2 = 0
        while contador2 < len(temp):
            plantilla = {
                'doctorName': _consulta[contador][4], 
                'doctorDocument': _consulta[contador][3], 
                'date': temp[contador2].strftime("%d-%b-%Y %H:%M:%S")
            }
            horarios.append(plantilla)
            contador2 = contador2 + 1
        consultorio["availableAppointment"] = horarios
        principal.append(consultorio)
        contador = contador + 1
    return principal






def obtener_consultorios_faltantes(_consulta, _consultorios):
    contador = 0
    faltantes = list()
    while contador < len(_consulta):
        if not(_consulta[contador][0] in _consultorios):
            faltantes.append(_consulta[contador][0])
        contador = contador + 1
    return faltantes




if __name__ == '__main__':
    fech1 = datetime(2020,4,1,7,0,0)
    fech2 = datetime(2020,4,30,21,0,0)
    fech3 = datetime(2021,4,1,7,0,0)
    print(obtener_fechas(fech1, fech2))
    #print(verificar_fecha(fech3, obtener_fechas(fech1, fech2)))