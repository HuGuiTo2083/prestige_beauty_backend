from flask import Flask, jsonify, url_for, render_template, request
import os
from dotenv import load_dotenv
import psycopg2
from flask_cors import CORS


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







@app.route('/')
def home():
    return render_template('index.html')

#if __name__ == '__main__':
#     app.run(debug=True)
    
