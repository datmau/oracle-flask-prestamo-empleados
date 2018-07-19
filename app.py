from flask import Flask, render_template, request, session, url_for,flash,redirect,send_file
import cx_Oracle
from datetime import date,datetime,timedelta
from practica import  generar_pdf
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)


print(ROOT_DIR)
oracle_connection_string = '{username}/{password}@{hostname}:{port}/{database}'
app.secret_key = 'somecharacters'


def connection(name, passw):
    engine = cx_Oracle.connect(oracle_connection_string.format(
        username=name,
        password=passw,
        hostname='localhost',
        port='1521',
        database='xe',
    ))
    return engine

def amtz(cap,ii,num):
    i=ii/100
    res=cap/((1-((1+i)**(-num)))/i)
    return res

def tabla_amor(total,c_anual,ano):
    datos=[]
    cap_amor=total
    interes=cap_amor*0.05
    cap_amor2=0
    for i in range(ano):
        cap_amor=(cap_amor-c_anual)+interes
        morti=c_anual-interes
        cap_amor2 =cap_amor2+morti
        datos.append([i,c_anual,interes,morti,cap_amor,cap_amor2])
        interes=cap_amor*0.05
    return datos
def llenar_cuotas(monto,interes,cuotas,con,fecha_str):

    ora=con
    cur= ora.cursor()
    cur2= ora.cursor()
    c_anual = amtz(float(monto), int(interes), int(cuotas))
    datos = tabla_amor(float(monto), c_anual, int(cuotas))
    stmnt = 'select MAX(PRESTAMO_ID) FROM PRESTAMO'
    dt = cur2.execute(stmnt)
    idp = dt.fetchall()
    print(fecha_str)
    date_object = datetime.strptime(fecha_str, '%Y/%m/%d')
    nueva_fecha = date_object + timedelta(days=31)
    for dato in datos:                
        try:
            fecha_pago = datetime.strftime(nueva_fecha, '%Y/%m/%d')
            statement = 'insert into cuota values(gen_cuotaid,:1,TO_DATE(:2,\'yyyy/mm/dd\'),:3,:4,:5,:6,:7,\'I\')'
            cur.execute(statement, (idp[0][0],fecha_pago,dato[1],dato[2],dato[3],dato[4],dato[5]))
            ora.commit()
            nueva_fecha = nueva_fecha + timedelta(days=31)
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            if error.code == 1400:
                statement = 'insert into cuota values(1,:1, TO_DATE(:2,\'yyyy/mm/dd\'),:3,:4,:5,:6,:7,\'I\')'
                cur.execute(statement, (idp[0][0],fecha_str, dato[1],dato[2], dato[3], dato[4], dato[5]))
                ora.commit()
                
    return 'Sali bien'


@app.route('/')
def loginp():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def Login():
    if request.method == "POST":
        result = request.form['first_name']
        contra = request.form['password']
        session['us_name'] = result
        session['us_pass'] = contra
        try:
            ora = connection(session['us_name'],session['us_pass'])
            if ora:
                cur = ora.cursor()
                cur.execute("SELECT  * FROM EMPLEADO")
                data = cur.fetchall()
                cur.close()
                cur1= ora.cursor()
                cur1.execute("SELECT departamento_id, dep_nombre FROM DEPARTAMENTO")
                data1 = cur1.fetchall()
                return render_template('index2.html', empleados=data,deps=data1)
        except PermissionError as pe:
            per, = pe.args
            if per == 13:
                flash("CREDENCIALES INCORRECTAS")
                return redirect(url_for('loginp'))
        except cx_Oracle.DatabaseError as er:
            error, = er.args
            if error.code==1017:
                flash("CREDENCIALES INCORRECTAS")
                return redirect(url_for('loginp'))
    flash('Logueo correcto pero no tiene permiso para ver las tablas')
    return render_template('login.html')




@app.route('/empleados', methods=['GET'])
def Index():
        ora = connection(session['us_name'],session['us_pass'])
        cur = ora.cursor()
        cur.execute("SELECT  * FROM EMPLEADO")
        data = cur.fetchall()
        cur.close()
        return render_template('index2.html', empleados=data)

@app.route('/insert', methods = ['POST','GET'])
def insert():
    if request.method == "POST":
        flash("Datos ingresados correctamente")
        id = request.form['id']
        nombres = request.form['nombres']
        lastname = request.form['apellidos']
        direccion = request.form['direccion']
        celular = request.form['celular']
        telefono = request.form['telefono']
        email = request.form['email']
        dep = request.form['dep']
        ora = connection(session['us_name'], session['us_pass'])
        cur = ora.cursor()
        statement = 'insert into empleado (CEDULA,DEPARTAMENTO_ID,NOMBRES,APELLIDOS, DIRECCION, CELULAR,TELEFONO,EMAIL) ' \
                    'values (:1,:2,:3,:4,:5,:6,:7,:8)'
        cur.execute(statement, (id,dep,nombres,lastname,direccion,celular,telefono,email))
        ora.commit()
        return redirect(url_for('Index'))
    return flash("ERROR EN INGRESO DE DATOS")



@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Registro borrado satisfactoriamente")
    ora = connection(session['us_name'], session['us_pass'])
    cur = ora.cursor()
    statement = 'DELETE FROM EMPLEADO WHERE empleado_id=:1'
    cur.execute(statement, (id_data,))
    ora.commit()
    return redirect(url_for('Index'))


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == "POST":
        id_data = request.form['id']
        nombres = request.form['nombres']
        lastname = request.form['apellidos']
        direccion = request.form['direccion']
        celular = request.form['celular']
        telefono = request.form['telefono']
        email = request.form['email']
        dep = request.form['dep']
        ora = connection(session['us_name'], session['us_pass'])
        cur = ora.cursor()
        cur.execute("""
               UPDATE EMPLEADO
               SET  departamento_id=%s, nombres=%s, apellidos=%s, direccion=%s, celular=%s, phone=%s
               , email=%s WHERE id=%s
            """, (dep, nombres, lastname, direccion, celular, telefono, email,id_data))
        flash("Actualización Correcta")
        ora.commit()
        return redirect(url_for('Index'))


@app.route('/update/<int:data_id>', methods=['POST'])
def update_new(data_id):
    if request.method == 'POST':
        nombres = request.form['nombres']
        lastname = request.form['apellidos']
        direccion = request.form['direccion']
        celular = request.form['celular']
        telefono = request.form['telefono']
        email = request.form['email']
        ora = connection(session['us_name'], session['us_pass'])
        cur = ora.cursor()
        statement = 'UPDATE EMPLEADO SET   nombres=:1, apellidos=:2, direccion=:3, celular=:4, telefono=:5, email=:6 WHERE cedula=:8'
        cur.execute(statement, (nombres,lastname,direccion,celular,telefono,email,data_id))
        flash("Actualización Correcta")
        ora.commit()
        return redirect(url_for('Index'))


@app.route('/departamentos', methods=['POST', 'GET'])
def new_dep():
    if request.method == 'POST':
        nombre = request.form['nombre']
        desc = request.form['desc']
        ora = connection(session['us_name'], session['us_pass'])
        try:
            cur = ora.cursor()
            statement = 'insert into DEPARTAMENTO VALUES (gen_id_dep,:1,:2)'
            cur.execute(statement, (nombre, desc))
            flash("INGRESO CORRECTO")
            ora.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            print("{}".format(error.code))
            if error.code == 1:
                flash("El nombre del departamento debe ser único")
                return render_template('departamentos.html')
        return redirect(url_for('sel_dep'))
    else:
        return render_template('departamentos.html')

@app.route('/sel_depart', methods=['GET'])
def sel_dep():
        ora = connection(session['us_name'],session['us_pass'])
        cur = ora.cursor()
        cur.execute("SELECT  * FROM DEPARTAMENTO")
        data = cur.fetchall()
        cur.close()
        return render_template('res_departamento.html', departamento=data)

@app.route('/tipo', methods=['POST', 'GET'])
def new_tipo():
    if request.method == 'POST':
        nombre = request.form['tabla']
        monto = request.form['cant']
        desc = request.form['infor']
        ora = connection(session['us_name'],session['us_pass'])
        try:
            cur = ora.cursor()
            statement = 'insert into TIPO values ( gen_tipoid ,:1 , :2, :3)'
            cur.execute(statement, (nombre, monto, desc))
            flash("INGRESO CORRECTO")
            ora.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            print("{}".format(error.code))
            if error.code == 1:
                flash("El nombre de ser unico")
                return render_template('interfaz_tipo.html')
            if error.code == 1400:
                statement = 'insert into TIPO values ( 1 ,:1 , :2, :3)'
                cur.execute(statement, (nombre, monto, desc))
                flash("INGRESO CORRECTO")
                ora.commit()
        return redirect(url_for('sel_tipo'))
    else:
        return render_template('interfaz_tipo.html')

@app.route('/sel_tipos', methods=['GET'])
def sel_tipo():
        ora = connection(session['us_name'],session['us_pass'])
        cur = ora.cursor()
        cur.execute("SELECT  * FROM TIPO")
        data = cur.fetchall()
        cur.close()
        return render_template('res_tipo.html', tipos=data)

@app.route('/amorti', methods=['GET','POST'])
def new_amortizacion():
    if request.method == 'POST':
        nombre = request.form['nom']
        formula = request.form['for']
        infor = request.form['des']
        ora = connection(session['us_name'],session['us_pass'])
        try:
            cur = ora.cursor()
            statement = 'insert into TABLASA values (gen_amorti,:1 ,:2, :3)'
            cur.execute(statement, ( nombre, formula, infor))
            flash("INGRESO CORRECTO")
            ora.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            print("{}".format(error.code))
            if error.code == 1:
                flash("El nombre de ser unico")
                return render_template('amortizacion.html')
            if error.code == 1400:
                statement = 'insert into TABLASA values (1,:1 ,:2, :3)'
                cur.execute(statement, (nombre, formula, infor))
                flash("INGRESO CORRECTO")
                ora.commit()
        return redirect(url_for('sel_amort'))
    else:
        return render_template('amortizacion.html')

@app.route('/sel_amorti', methods=['GET'])
def sel_amort():
        ora = connection(session['us_name'],session['us_pass'])
        cur = ora.cursor()
        cur.execute("SELECT  * FROM TABLASA")
        data = cur.fetchall()
        cur.close()
        return render_template('res_amorti.html', amorti=data)

@app.route('/prestamo', methods=['GET'])
def ver_prestamos():
        ora = connection(session['us_name'],session['us_pass'])
        cur = ora.cursor()
        cur.execute("SELECT  * FROM prestamo")
        data = cur.fetchall()
        cur.close()
        return render_template('prestamos.html', prestamos=data)

@app.route('/prestamo/new', methods=['POST','GET'])
def nuevo_prestamo():
    if request.method == 'POST':
        amort = request.form['amort']
        tipo = request.form['tipo']
        cedula = request.form['cedula']
        fecha = request.form['fecha']
        monto = request.form['monto']
        estado = request.form['estado']
        cuotas = request.form['cuotas']
        interes = request.form['interes']
        ora = connection(session['us_name'], session['us_pass'])
        print(fecha)
        try:
            cur = ora.cursor()
            statement = 'insert into prestamo values ( gen_prestamoid,:1 ,:2, :3, TO_DATE(:4,\'YYYY-MM-DD\'), :5,:6 ,:7,:8)'
            cur.execute(statement, ( tipo, cedula, amort, fecha, monto , estado, cuotas, interes))
            flash('Ingreso correcto de prestamo')
            ora.commit()
        except cx_Oracle.IntegrityError as e:
            error, = e.args
            print(error.code)
            print(error.message)
            if error.code == 1400:
                statement = 'insert into prestamo values ( 1,:1 ,:2, :3,  TO_DATE(:4,\'YYYY-MM-DD\'), :5,:6 ,:7,:8)'
                cur.execute(statement, (tipo, cedula, amort, fecha, monto, estado, cuotas, interes))
                flash('Ingreso correcto de prestamo')
                ora.commit()
                llenar_cuotas(monto, interes, cuotas, ora)
                return redirect(url_for('ver_prestamos'))
        llenar_cuotas(monto,interes,cuotas,ora,fecha.replace('-','/'))
        return redirect(url_for('ver_prestamos'))
    else:
        ora = connection(session['us_name'], session['us_pass'])
        cur2 = ora.cursor()
        cur3= ora.cursor()
        stm1 = cur2.execute('SELECT nombre_ta,TABLASA_ID FROM TABLASA')
        stm2 = cur3.execute('SELECT nombre_ti,tipo_id FROM TIPO')
        amorti = stm1.fetchall()
        tipo = stm2.fetchall()
        return render_template('new_prestamo.html', amorti = amorti,tipo=tipo)


@app.route('/cuotas',methods=['POST'])
def ver_cuotas():
    ora = connection(session['us_name'], session['us_pass'])
    cur = ora.cursor()
    if request.method == 'POST':        
        idc = request.form['idp']
        statement="SELECT  * FROM cuota where prestamo_id=:1 AND ESTADO=\'I\'"
        cur.execute(statement, (idc))
        data = cur.fetchall()
        cur.close()
        return render_template('coutas.html', cuotas=data)
    
  

@app.route('/pago')
def update_cuota():
    if request.method == 'GET':
        ahora = datetime.now()
        fecha = datetime.strftime(ahora,'%d-%m-%Y')
        cuota= request.args.get('cuot_id')
        prestamo= request.args.get('pres_id')
        ora = connection(session['us_name'], session['us_pass'])
        cur = ora.cursor()
        statement = 'UPDATE CUOTA SET ESTADO = \'A\' WHERE PRESTAMO_ID=:1 AND CUOTA_ID=:2'
        cur.execute(statement, (prestamo, cuota))
        flash("Pago Registrado")
        ora.commit()
        statement2='SELECT * FROM cuota where prestamo_id=:1 AND ESTADO=\'I\''
        ora1 = connection(session['us_name'], session['us_pass'])
        cur2 = ora1.cursor()
        cur2.execute(statement2, (prestamo,))
        data = cur2.fetchall()
        print (data)
        ruta = generar_pdf(data,fecha,prestamo,'Consumidor final',ROOT_DIR)
        cur2.close()
        return send_file(ruta)

    




if __name__ == '__main__':
    app.run()
