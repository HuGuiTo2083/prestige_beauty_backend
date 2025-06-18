from flask import Flask, jsonify, url_for, render_template, request
import os
from dotenv import load_dotenv
import psycopg2
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText

import psycopg2.extras

load_dotenv()

app = Flask(__name__)

# Permite CORS para todos los orígenes (esto es útil para desarrollo)
CORS(app)
#test de git
def get_db_connection():
    """
    Abre una conexión a PostgreSQL usando la URI almacenada en la
    variable de entorno DB_STRING.

    Ejemplo de valor (sin saltos de línea):
    postgresql://usuario:contraseña@host:puerto/base_de_datos
    """
    dsn = os.getenv("DB_STRING")
    if not dsn:
        raise RuntimeError("La variable de entorno DB_STRING no está definida")

    # Conexión; puedes añadir parámetros extra (sslmode, connect_timeout, etc.)
    conn = psycopg2.connect(dsn)
    return conn



@app.route('/getSchedule', methods=['POST'])
def getScheduleById():
    data = request.get_json()
    myId = data.get('id')  

    try:
        # Aquí puedes verificar si el usuario existe en tu base de datos.
        # Si no existe, puedes registrar al usuario.
         sql = """
    SELECT SCHEDULE_DATE, SCHEDULE_HOUR, SCHEDULE_STATUS
    FROM SCHEDULE_MSTR
    WHERE SCHEDULE_USR_ID = %s

    """
         conn = get_db_connection()
         try:
             with conn.cursor() as cur:
                 cur.execute(sql, (myId,))
                 rows = cur.fetchall()
                 if not rows:
                     # No existe ningún registro con ese email
                     return {"Messsage": "No hay registros"}
     
                 schedules = [
                      {
                          "date":    row[0],
                          "hour":    row[1],
                          "status":  row[2]
                      }
                      for row in rows
                      ]
        # Devuelve JSON (puede estar vacío si no hay filas)
                 return jsonify(schedules), 200
         finally:
             conn.close()

    except ValueError as e:
        print("error...." + str(e))
        # Si el token no es válido, devuelve un error
        return jsonify({"error": "Invalid Info"}), 400

#este endpoint es para sacar los pedidos que un usuario ha hecho desde los servicios
@app.route('/getSchedule_with_user', methods=['POST'])
def getScheduleById_with_user():
    data = request.get_json()
    myId = data.get('id')  
    myUser_Id = data.get('user_id')  
    try:
        # Aquí puedes verificar si el usuario existe en tu base de datos.
        # Si no existe, puedes registrar al usuario.
         sql = """
    SELECT SCHEDULE_DATE, SCHEDULE_HOUR, SCHEDULE_STATUS, SCHEDULEDET_USER_ID, SCHEDULEDET_SERVICE
    FROM SCHEDULE_MSTR JOIN SCHEDULE_DET ON SCHEDULEDET_SCHEDULE_ID = SCHEDULE_ID
    WHERE SCHEDULE_USR_ID = %s AND SCHEDULEDET_USER_ID = %s

    """
         conn = get_db_connection()
         try:
             with conn.cursor() as cur:
                 cur.execute(sql, (myId, myUser_Id,))
                 rows = cur.fetchall()
                 if not rows:
                     # No existe ningún registro con ese email
                     return {"Messsage": "No hay registros"}
     
                 schedules = [
                      {
                          "date":    row[0],
                          "hour":    row[1],
                          "status":  row[2],
                          "id": row[3],
                          "service":  row[4]
                      }
                      for row in rows
                      ]
        # Devuelve JSON (puede estar vacío si no hay filas)
                 return jsonify(schedules), 200
         finally:
             conn.close()

    except ValueError as e:
        print("error...." + str(e))
        # Si el token no es válido, devuelve un error
        return jsonify({"error": "Invalid Info"}), 400


#este endpoint es para sacar los pedisos que debe de aprobar/rechazar en el admin

@app.route('/getRequests', methods=['POST'])
def getRequests():
    data = request.get_json()
    myId = data.get('id')  

    try:
        # Aquí puedes verificar si el usuario existe en tu base de datos.
        # Si no existe, puedes registrar al usuario.
         sql = """
    SELECT SCHEDULE_DATE, SCHEDULE_HOUR, SCHEDULE_STATUS, SCHEDULEDET_SERVICE, USR_NAME, SCHEDULE_ID
    FROM SCHEDULE_MSTR JOIN SCHEDULE_DET ON SCHEDULEDET_SCHEDULE_ID = SCHEDULE_ID
    JOIN USR_MSTR ON SCHEDULEDET_USER_ID = USR_ID
    WHERE SCHEDULE_USR_ID = %s 

    """
         conn = get_db_connection()
         try:
             with conn.cursor() as cur:
                 cur.execute(sql, (myId,))
                 rows = cur.fetchall()
                 if not rows:
                     # No existe ningún registro con ese email
                     return {"Messsage": "No hay registros"}
     
                 schedules = [
                      {
                          "date":    row[0],
                          "hour":    row[1],
                          "status":  row[2],
                          "service": row[3],
                          "name": row[4],
                          "id" : row[5]
                      }
                      for row in rows
                      ]
        # Devuelve JSON (puede estar vacío si no hay filas)
                 return jsonify(schedules), 200
         finally:
             conn.close()

    except ValueError as e:
        print("error...." + str(e))
        # Si el token no es válido, devuelve un error
        return jsonify({"error": "Invalid Info"}), 400



def exist_email(email) ->bool:
    mySQL ="""
      SELECT USR_NAME FROM USR_MSTR WHERE USR_EMAIL = %s
    """
    try: 
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(mySQL, (email,))
        rows = cur.fetchall()
        if not rows:
            return False
        else:
            return True
    except ValueError as e:
        print("error: " + str(e))
        return {"error" + str(e)}



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    myEmail = data.get('email')
    myPassword = data.get('password')

    try:
        mySQL = """
         SELECT * FROM USR_MSTR WHERE USR_EMAIL = %s
         AND USR_PASSWORD = %s
        """
        try:
            
            conn = get_db_connection()

            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(mySQL, (myEmail, myPassword,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            if not rows:
                if  exist_email(myEmail):
                    return {"status": 0, "number": 0}
                else:
                    return {"status": 0, "number": 1}
            
            return {"rows" : rows, "status" : 1}
        except Exception as e:
            print(str(e))
            return {"error" + str(e)}
            
    except ValueError as e:
        print("error: " + str(e))
        return {"error" + str(e)}

@app.route('/regist', methods=['POST'])
def regist():
    data = request.get_json()
    myEmail = data.get('email')
    if exist_email(myEmail):
        return jsonify({"error": "ya existe email", "status": 1}), 400
    
    myName = data.get('name')
    myPassword = data.get('password')
    mySQL = """INSERT INTO USR_MSTR (USR_NAME, USR_PASSWORD, USR_EMAIL, USR_TYPE_USER)
               VALUES (%s, %s, %s, 1)
                RETURNING USR_ID, USR_TYPE_USER;
               """
    try:
        conn  = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(mySQL, (myName, myPassword, myEmail,))
        row = cur.fetchone()
        return jsonify({
            "success": "creado exitosamente", 
            "status": 0, 
            "id": row['USR_ID'],
            "type": row['USR_TYPE_USER']
            }), 200
        
        print("")
    except ValueError as e:
        print("error: " + str(e))
        return jsonify({"error": str(e)})






# Configuración SMTP de Gmail
SMTP_SERVER = os.getenv("GMAIL_ACCOUNT")
SMTP_PORT = 587
GMAIL_USER = os.getenv("GMAIL_ACCOUNT")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

def enviar_codigo_por_email(destinatario, codigo):
    asunto = "Tu código de verificación"
    cuerpo = f"Tu código de verificación es: {codigo}"
    mensaje = MIMEText(cuerpo, "plain")
    mensaje["Subject"] = asunto
    mensaje["From"] = GMAIL_USER
    mensaje["To"] = destinatario

    # Conexión y envío
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Seguridad
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, destinatario, mensaje.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

@app.route("/send_code", methods=["POST"])
def send_code():
    data = request.json
    email = data.get("email")
    codigo = data.get("code")

    if not email or not codigo:
        return jsonify({"error": "Faltan parámetros email o codigo"}), 400

    exito = enviar_codigo_por_email(email, codigo)
    if exito:
        return jsonify({"mensaje": "Correo enviado correctamente"})
    else:
        return jsonify({"error": "Error enviando correo"}), 500



@app.route('/')
def home():
    return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)
    
