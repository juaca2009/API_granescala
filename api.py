import pymysql
import json
from datetime import datetime
from flask import Flask, request
from obtener_horarios import obtener_consultorios, generar_horarios, obtener_fechas, obtener_horarios2, obtener_horarios3

#conexion base de datos
conexion = pymysql.Connect(host='mysql-historiasclinicas.alwaysdata.net', 
                           user='203256', password='juancamilo99', db='historiasclinicas_bd')
cursor = conexion.cursor()
#servidor flask
app = Flask(__name__)










@app.route('/horarios/<string:ips>/<string:espc>')
def obtener_horarios(ips, espc):
    global cursor
    cursor.execute(
        """
        select nro_consultorio, fecha_inicial, fecha_final, horarios.fecha, medicos.nro_documento, medicos.nombres, especializaciones.nombre from especializaciones inner join medicos on (especializaciones.id_especializacion = medicos.id_espc)
        inner join consultorios on (medicos.nro_documento = consultorios.id_medico) inner join ips on (consultorios.id_Ips = ips.id_ips)
        inner join horarios on (horarios.id_consultorio = consultorios.nro_consultorio)
        where ips.nombre = %s and especializaciones.nombre = %s order by nro_consultorio, horarios.fecha
        """,
        (ips, espc)
    )
    consulta = cursor.fetchall()
    if len(consulta) != 0:
        consultorios = obtener_consultorios(consulta)
        horarios = generar_horarios(consultorios, consulta)
        cursor.execute(
            """
            select nro_consultorio, fecha_inicial, fecha_final, medicos.nro_documento, medicos.nombres, especializaciones.nombre from especializaciones inner join medicos on (especializaciones.id_especializacion = medicos.id_espc)
            inner join consultorios on (medicos.nro_documento = consultorios.id_medico) inner join ips on (consultorios.id_Ips = ips.id_ips)
            where ips.nombre = %s and especializaciones.nombre = %s order by nro_consultorio
            """,
            (ips, espc)
        )
        consulta = cursor.fetchall()
        consul_ya = list(horarios.keys())
        contador = 0
        consul = list()
        while contador < len(consulta):
            if not(consulta[contador][0] in consul_ya):
                consul.append(consulta[contador][0])
            contador = contador + 1
        if len(consul) == 0 and len(horarios.keys()) != 0:
            return json.dumps(horarios)
        elif len(consul) == 0 and len(horarios.keys()) == 0:
            return  json.dumps({"mensaje":"no hay horarios disponibles"})
        else:
            horarios2 = obtener_horarios2(consul, consulta, horarios)
            return json.dumps(horarios2)

    else:
        cursor.execute(
            """
            select nro_consultorio, fecha_inicial, fecha_final, medicos.nro_documento, medicos.nombres, especializaciones.nombre from especializaciones inner join medicos on (especializaciones.id_especializacion = medicos.id_espc)
            inner join consultorios on (medicos.nro_documento = consultorios.id_medico) inner join ips on (consultorios.id_Ips = ips.id_ips)
            where ips.nombre = %s and especializaciones.nombre = %s order by nro_consultorio
            """,
            (ips, espc)
        )
        consulta = cursor.fetchall()
        if len(consulta) != 0:
            horarios = obtener_horarios3(consulta)
            return json.dumps(horarios)
        else:
            return  json.dumps({"mensaje":"datos erroneos"})













@app.route('/ips')
def obtener_ips():
    global cursor
    cursor.execute(
        """
        select id_ips, nombre, direccion from ips
        """
    )
    consulta = cursor.fetchall()
    if len(consulta) != 0:
        principal = list()
        contador = 0
        while contador < len(consulta):
            ips = {
                'id': consulta[contador][0],
                'name': consulta[contador][1],
                'streetAddress': consulta[contador][2]
            }
            principal.append(ips)
            contador = contador + 1
        return json.dumps(principal)
    else:
        return json.dumps({'mensaje':"no hay ips en la base de datos"})











@app.route('/ips/<string:nombre_ips>')
def obtener_especializaciones(nombre_ips):
    global cursor
    cursor.execute(
        """
        select nro_consultorio, especializaciones.nombre from ips inner join consultorios on (ips.id_ips = consultorios.id_Ips)
        inner join medicos on (consultorios.id_medico = medicos.nro_documento) 
        inner join especializaciones on (medicos.id_espc = especializaciones.id_especializacion)
        where ips.nombre = %s
        """,
        (nombre_ips)
    )  
    consulta = cursor.fetchall()
    if len(consulta) != 0:
        contador = 0
        principal = list()
        while contador < len(consulta):
            nombre = "consultorio "
            nombre = nombre + str(consulta[contador][0])
            consultorio = {
                "name": nombre,
                "specialties": None
            }
            temp = list()
            temp2 = {
                "name": consulta[contador][1]
            }
            temp.append(temp2)
            consultorio["specialties"] = temp
            principal.append(consultorio)
            contador = contador + 1
        return json.dumps(principal)
    else:
        return json.dumps({"mensaje": "no se encontraron especializaciones"})












@app.route('/horarios/<int:documento>')
def horarios_paciente(documento):
    global cursor
    cursor.execute(
        """
        select nro_cita, horarios.fecha, ips.nombre, ips.direccion, medicos.nombres, especializaciones.nombre from horarios
        inner join consultorios on (horarios.id_consultorio = consultorios.nro_consultorio) 
        inner join ips on (consultorios.id_Ips = ips.id_ips) inner join medicos on (consultorios.id_medico = medicos.nro_documento)
        inner join especializaciones on (especializaciones.id_especializacion = medicos.id_espc)
        where horarios.documento_paciente = %s order by horarios.fecha
        """,
        (documento)
    )
    consulta = cursor.fetchall()
    if len(consulta) != 0:
        citas = list()
        contador = 0
        while contador < len(consulta):
            plantilla = {
                'id': consulta[contador][0],
                'date': consulta[contador][1].strftime("%d-%b-%Y (%H:%M:%S)"),
                'healthProviderInstitute': consulta[contador][2],
                'address': consulta[contador][3],
                'doctorName': consulta[contador][4],
                'specialization': consulta[contador][5]
            }
            citas.append(plantilla)
            contador = contador + 1
        return json.dumps(citas)
    else:
        return json.dumps({'mensaje': 'no hay citas para este paciente'})















@app.route('/horarios/<int:nro_cita>', methods=['DELETE'])
def eliminar_cita(nro_cita):
    global cursor, conexion
    cursor.execute(
        """
        select nro_cita from horarios where nro_cita = %s
        """,
        (nro_cita)
    )
    verificar = cursor.fetchall()
    if len(verificar) != 0:
        cursor.execute(
            """
            delete from horarios where nro_cita = %s
            """,
            (nro_cita)
        )
        conexion.commit()
        return json.dumps({'mensaje': 'cita eliminada'})
    else:
        return json.dumps({'mensaje': 'la cita solicitada no exite'})












@app.route('/horarios', methods=['POST'])
def agendar_cita():
    global cursor, conexion
    datos = request.json
    temp = list(datos.keys())
    id_paciente = int(temp[0])
    temp = datos[temp[0]]
    fecha = temp["fecha"]
    fecha = datetime.strptime(fecha, '%m/%d/%y %H:%M:%S')
    id_medico = int(temp["medico"])
    cursor.execute(
        """
        select agendar_cita(%s, %s, %s, %s)
        """,
        (fecha, id_medico, temp["ips"], id_paciente)
    )
    consulta = cursor.fetchall()
    consulta = consulta[0][0]
    conexion.commit()
    if consulta != 0:
        temp = {}
        temp["nro cita"] = consulta
        return json.dumps(temp)
    else:
        return json.dumps({"mensaje": "la ips no existe"})












@app.route('/solicitud',  methods=['POST'])
def modificar_cita():
    global cursor, conexion
    datos = request.json
    temp = list(datos.keys())
    id_paciente = int(temp[0])
    info_cita = datos[temp[0]]
    id_medico = int(info_cita["medico"])
    n_fecha = info_cita["fecha"]
    n_cita = int(info_cita["cita"])
    n_fecha = datetime.strptime(n_fecha, '%m/%d/%y %H:%M:%S')
    cursor.execute(
        """
        select nro_consultorio, fecha_inicial, fecha_final from medicos inner join consultorios on (medicos.nro_documento = consultorios.id_medico)
        where medicos.nro_documento = %s
        """,
        (id_medico)
    )
    consulta = cursor.fetchall()
    fechas = obtener_fechas(consulta[0][1], consulta[0][2])
    cursor.execute(
        """
        select fecha from consultorios inner join horarios on (consultorios.nro_consultorio = horarios.id_consultorio)
        where nro_consultorio = %s
        """,
        (consulta[0][0])
    )
    horarios = cursor.fetchall()
    contador = 0
    while contador < len(horarios):
        fechas.remove(horarios[contador][0])
        contador = contador + 1
    if n_fecha in fechas:
        cursor.execute(
            """
            delete from horarios where nro_cita = %s
            """,
            (n_cita)
        )
        conexion.commit()
        cursor.execute(
            """
            select agendar_cita(%s, %s, %s, %s)
            """,
            (n_fecha, id_medico, info_cita["ips"], id_paciente)
        )
        consulta = cursor.fetchall()
        consulta = consulta[0][0]
        conexion.commit()
        if consulta == 1:
            return json.dumps({"mensaje": "se ha modificado la cita solicitada"})
        else:
            return json.dumps({"mensaje": "ha ocurrido un error"})
    else:
        return json.dumps({"mensaje": "el horario solicitado no esta disponible"})













if __name__ == '__main__':
    app.run(debug=True)