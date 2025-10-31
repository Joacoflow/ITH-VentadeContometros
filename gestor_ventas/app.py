from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
import webbrowser
import threading
import time

app = Flask(__name__)
app.secret_key = 'clave_super_secreta'

navegador_abierto = False

def abrir_navegador():
    global navegador_abierto
    if not navegador_abierto:
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:5000/")
        navegador_abierto = True

def conectar_bd():
    conexion = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\MSSQLSERVER2014;'  
        'DATABASE=GestorVentas;'
        'Trusted_Connection=yes;'
    )
    return conexion

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuario WHERE username = ? AND password = ?", (username, password))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session['usuario'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

#----------------------------DASHBOARD-------------------------------
#----------------------------------------------------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = conectar_bd()
    cursor = conn.cursor()

    mensaje = None
    error = None
    editar_id = request.args.get('editar', type=int)

    if request.method == 'POST':
        if 'registrar' in request.form:
            try:
                descripcion = request.form['descripcion']
                cliente = request.form['cliente']
                dni = request.form['dni']
                monto = float(request.form['monto'])
                fecha = request.form['fecha']
                cursor.execute("INSERT INTO Ventas (descripcion, cliente, dni, monto, fecha) VALUES (?, ?, ?, ?, ?)",
                               (descripcion, cliente, dni, monto, fecha))
                conn.commit()
                mensaje = 'Venta registrada correctamente.'
            except Exception as e:
                error = f'Error al registrar venta: {e}'

        elif 'editar' in request.form:
            try:
                venta_id = int(request.form['venta_id'])
                descripcion = request.form['descripcion']
                cliente = request.form['cliente']
                dni = request.form['dni']
                monto = float(request.form['monto'])
                fecha = request.form['fecha']
                cursor.execute("UPDATE Ventas SET descripcion=?, cliente=?, dni=?, monto=?, fecha=? WHERE id=?",
                               (descripcion, cliente, dni, monto, fecha, venta_id))
                conn.commit()
                mensaje = 'Venta actualizada correctamente.'
                editar_id = None
            except Exception as e:
                error = f'Error al actualizar venta: {e}'

        elif 'eliminar' in request.form:
            try:
                venta_id = int(request.form['eliminar'])
                cursor.execute("DELETE FROM Ventas WHERE id = ?", (venta_id,))
                conn.commit()
                mensaje = 'Venta eliminada correctamente.'
            except Exception as e:
                error = f'Error al eliminar venta: {e}'

    # filtros por mes/año
    anio = request.args.get('anio', type=int)
    mes = request.args.get('mes', type=int)

    ventas = []
    total = 0
    if anio and mes:
        cursor.execute("""
            SELECT id, descripcion, cliente, dni, monto, fecha
            FROM Ventas
            WHERE YEAR(fecha) = ? AND MONTH(fecha) = ?
            ORDER BY fecha
        """, (anio, mes))
        ventas = cursor.fetchall()

        cursor.execute("""
            SELECT ISNULL(SUM(monto), 0)
            FROM Ventas
            WHERE YEAR(fecha) = ? AND MONTH(fecha) = ?
        """, (anio, mes))
        total = cursor.fetchone()[0]

    venta_editar = None
    if editar_id:
        cursor.execute("SELECT * FROM Ventas WHERE id = ?", (editar_id,))
        venta_editar = cursor.fetchone()

    conn.close()

    return render_template('dashboard.html',
                           usuario=session['usuario'],
                           ventas=ventas,
                           total=total,
                           mes=mes,
                           anio=anio,
                           mensaje=mensaje,
                           error=error,
                           editar_id=editar_id,
                           venta_editar=venta_editar)

#----------------------------ver_ventas-------------------------------
#----------------------------------------------------------------------
@app.route('/ver_ventas')
def ver_ventas():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    busqueda = request.args.get('busqueda')
    anio = request.args.get('anio', type=int)
    mes = request.args.get('mes', type=int)

    conn = conectar_bd()
    cursor = conn.cursor()

    query = """
        SELECT id, descripcion, monto, fecha, cliente, dni
        FROM Ventas
        WHERE 1=1
    """
    params = []

    if busqueda:
        query += " AND (cliente LIKE ? OR dni LIKE ?)"
        params.extend([f"%{busqueda}%", f"%{busqueda}%"])
    
    if anio:
        query += " AND YEAR(fecha) = ?"
        params.append(anio)
    
    if mes:
        query += " AND MONTH(fecha) = ?"
        params.append(mes)

    cursor.execute(query, params)
    ventas = cursor.fetchall()

    total = sum([v[2] for v in ventas]) if ventas else 0

    cliente_nombre = ventas[0][4] if ventas else ""
    cliente_dni = ventas[0][5] if ventas else ""

    conn.close()

    return render_template('ver_ventas.html',
                           ventas=ventas,
                           total=total,
                           busqueda=busqueda,
                           anio=anio,
                           mes=mes,
                           cliente_nombre=cliente_nombre,
                           cliente_dni=cliente_dni)

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
@app.route('/ranking_clientes', methods=['GET'])
def ranking_clientes():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    # Filtros opcionales
    desde = request.args.get('desde')  # 'YYYY-MM-DD'
    hasta = request.args.get('hasta')  # 'YYYY-MM-DD'
    top = request.args.get('top', type=int) or 20

    conn = conectar_bd()
    cursor = conn.cursor()

    query = """
        SELECT
            COALESCE(NULLIF(dni,''), cliente) AS clave_cliente,
            MAX(cliente)                           AS cliente,
            MAX(NULLIF(dni,''))                    AS dni,
            COUNT(*)                               AS compras,
            SUM(monto)                             AS total,
            MIN(fecha)                             AS primera_compra,
            MAX(fecha)                             AS ultima_compra
        FROM Ventas
        WHERE 1=1
    """
    params = []

    if desde:
        query += " AND fecha >= ?"
        params.append(desde)
    if hasta:
        query += " AND fecha <= ?"
        params.append(hasta)

    query += """
        GROUP BY COALESCE(NULLIF(dni,''), cliente)
        ORDER BY total DESC
    """

    cursor.execute(query, params)
    ranking = cursor.fetchall()
    conn.close()

    # Aplica Top N en Python para evitar lío con TOP(@var)
    ranking = ranking[:top] if ranking else []

    return render_template(
        'ranking_clientes.html',
        ranking=ranking,
        desde=desde,
        hasta=hasta,
        top=top
    )
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=abrir_navegador, daemon=True).start()
    app.run(debug=True, use_reloader=False)
