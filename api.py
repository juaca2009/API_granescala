import pymysql
import json
from datetime import datetime
from flask import Flask, request
from obtener_horarios import obtener_consultorios, generar_horarios

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
        if len(horarios) != 0:
            return json.dumps(horarios)
        else:
            return json.dumps({"mensaje": "no hay horarios disponibles"})
    else:
        return json.dumps({"mensaje":"no se encontraron resultados"})












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
        temp = list()
        ips = {}
        contador = 0
        while contador < len(consulta):
            plantilla = {
                'nombre': consulta[contador][1],
                'direccion': consulta[contador][2]
            }
            ips[consulta[contador][0]] = plantilla
            contador = contador + 1
        return json.dumps(ips)
    else:
        return json.dumps({'mensaje':"no hay ips en la base de datos"})











@app.route('/ips/<string:nombre_ips>')
def obtener_especializaciones(nombre_ips):
    global cursor
    cursor.execute(
        """
        select especializaciones.nombre from ips inner join consultorios on (ips.id_ips = consultorios.id_Ips)
        inner join medicos on (consultorios.id_medico = medicos.nro_documento) 
        inner join especializaciones on (medicos.id_espc = especializaciones.id_especializacion)
        where ips.nombre = %s group by especializaciones.nombre
        """,
        (nombre_ips)
    )
    consulta = cursor.fetchall()
    consulta = consulta[0]
    if len(consulta) != 0:
        contador = 0
        temp = list()
        espc = {}
        while contador < len(consulta):
            temp.append(consulta[contador])
            contador = contador + 1
        espc[nombre_ips] = temp
        return json.dumps(espc)
    else:
        return json.dumps({"mensaje": "no se encontraron especializaciones"})












@app.route('/horarios/<int:documento>')
def horarios_paciente(documento):
    global cursor
    cursor.execute(
        """
        select nro_cita, nro_consultorio, horarios.fecha, ips.nombre, ips.direccion, medicos.nombres, especializaciones.nombre from horarios
        inner join consultorios on (horarios.id_consultorio = consultorios.nro_consultorio) 
        inner join ips on (consultorios.id_Ips = ips.id_ips) inner join medicos on (consultorios.id_medico = medicos.nro_documento)
        inner join especializaciones on (especializaciones.id_especializacion = medicos.id_espc)
        where horarios.documento_paciente = %s order by horarios.fecha
        """,
        (documento)
    )
    consulta = cursor.fetchall()
    if len(consulta) != 0:
        citas = {}
        contador = 0
        while contador < len(consulta):
            plantilla = {
                'fecha': consulta[contador][2].strftime("%d-%b-%Y (%H:%M:%S)"),
                'ips': consulta[contador][3],
                'direccion': consulta[contador][4],
                'medico': consulta[contador][5],
                'especializacion': consulta[contador][6]
            }
            citas[consulta[contador][0]] = plantilla
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
    if consulta == 1:
        return json.dumps({"mensaje": "cita agendada correctamente"})
    elif consulta == 0:
        return json.dumps({"mensaje": "el medico no se encuentra en la ips"})
    elif consulta == 2:
        return json.dumps({"mensaje": "el medico no existe"})
    else:
        return json.dumps({"mensaje": "la ips no existe"})












if __name__ == '__main__':
    app.run(debug=True)