from flask import Flask, render_template, request, redirect, send_from_directory
import pandas as pd
import qrcode
import os

app = Flask(__name__)

excel = '/home/Knicox/mysite/alumnos.xlsx'

try:
    df = pd.read_excel(excel)
    df.set_index('ID', inplace=True)
except Exception as e:
    print("Error al cargar el archivo 'alumnos.xlsx':", e)

qr_dir = '/home/Knicox/mysite/qrs'

# Función para generar un código QR para un ID de alumno
def generar_codigo_qr(id_alumno):

    qr_path = os.path.join(qr_dir, f'{id_alumno}.png')
    if not os.path.exists(qr_path):

        data = f"https://knicox.pythonanywhere.com/consultarsaldo/{id_alumno}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)

        # Crear imagen QR
        img = qr.make_image(fill='black', back_color='white')

        # Guardar imagen
        os.makedirs(qr_dir, exist_ok=True)
        img.save(qr_path)

# Generar códigos QR para todos los alumnos
for id_alumno in df.index:
    generar_codigo_qr(id_alumno)

@app.route('/')
def index():
    return 'Bienvenido al sistema de gestión de saldos de alumnos'

@app.route('/hola')
def manu():

    return ("Ruta del archivo:", os.path.abspath('home/knicox/mysite/alumnos.xlsx'))


@app.route('/consultarsaldo/<int:id_alumno>', methods=['GET', 'POST'])
def consultarsaldo(id_alumno):
    if id_alumno not in df.index:
        return render_template('error.html', message='Alumno no encontrado'), 404

    if request.method == 'POST':
        data = request.form
        if 'monto' in data and 'operacion' in data:
            try:
                monto = float(data['monto'])
                if data['operacion'] == 'sumar':
                    df.at[id_alumno, 'Saldo'] += monto
                elif data['operacion'] == 'restar':
                    df.at[id_alumno, 'Saldo'] -= monto

                try:
                    df.to_excel(excel)
                    mensaje = 'Saldo actualizado con éxito'
                except PermissionError:
                    mensaje = 'Error: No se puede escribir en el archivo alumnos.xlsx. Verifique que no esté abierto en otro programa y que tenga los permisos necesarios.'
            except ValueError:
                mensaje = 'Monto inválido'
        else:
            mensaje = 'Monto u operación no proporcionados'

        return render_template('consultarsaldo.html', alumno=df.loc[id_alumno].to_dict(), mensaje=mensaje)

    alumno = df.loc[id_alumno].to_dict()
    return render_template('consultarsaldo.html', alumno=alumno)

@app.route('/tarjetas')
def tarjetas():
    alumnos = df.to_dict(orient='index')
    return render_template('tarjetas.html', alumnos=alumnos)

@app.route('/qrs/<filename>')
def qr_code(filename):
    return send_from_directory('qrs', filename)

if __name__ == '__main__':
    app.run()
