# src/app.py

from flask import Flask, render_template_string
import mysql.connector
import os
import time

app = Flask(__name__)

# Configuración de la base de datos desde variables de entorno
DB_HOST = os.environ.get('MYSQL_HOST', 'db')
DB_USER = os.environ.get('MYSQL_USER', 'user')
DB_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
DB_NAME = os.environ.get('MYSQL_DATABASE', 'mydatabase')

def get_db_connection():
    """Intenta conectar a la base de datos, reintentando si falla."""
    conn = None
    retries = 5
    while retries > 0:
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            print("Conexión a la base de datos exitosa.")
            return conn
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")
            retries -= 1
            if retries > 0:
                print(f"Reintentando en 5 segundos... ({retries} intentos restantes)")
                time.sleep(5)
            else:
                print("No se pudo conectar a la base de datos después de varios intentos.")
                raise
    return None

def initialize_db():
    """Inicializa la base de datos: crea la tabla 'messages' si no existe."""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Crea la tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()

            # Inserta un mensaje si la tabla está vacía
            cursor.execute("SELECT COUNT(*) FROM messages")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO messages (content) VALUES (%s)", ("¡Hola Mundo desde MySQL!",))
                conn.commit()
                print("Mensaje '¡Hola Mundo desde MySQL!' insertado.")
            else:
                print("La tabla 'messages' ya contiene datos.")
            cursor.close()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

@app.route('/')
def hello_world():
    """Ruta principal que muestra el mensaje de la base de datos."""
    message = "Error: No se pudo conectar a la base de datos."
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM messages LIMIT 1")
            result = cursor.fetchone()
            if result:
                message = result[0]
            else:
                message = "No hay mensajes en la base de datos. ¡Algo salió mal!"
            cursor.close()
    except Exception as e:
        print(f"Error al obtener el mensaje de la base de datos: {e}")
        message = f"Error al obtener el mensaje: {e}"
    finally:
        if conn:
            conn.close()

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hola Mundo Docker Compose</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {
                    font-family: 'Inter', sans-serif;
                }
            </style>
        </head>
        <body class="bg-gradient-to-r from-blue-500 to-purple-600 min-h-screen flex items-center justify-center">
            <div class="bg-white p-8 rounded-xl shadow-2xl transform hover:scale-105 transition-transform duration-300 text-center max-w-md w-full">
                <h1 class="text-5xl font-extrabold text-gray-800 mb-4 animate-bounce">
                    ¡Hola Mundo!
                </h1>
                <p class="text-2xl text-gray-600">
                    {{ message }}
                </p>
                <p class="mt-6 text-sm text-gray-500">
                    Conectado a MySQL con Docker Compose
                </p>
            </div>
        </body>
        </html>
    """, message=message)

if __name__ == '__main__':
    # Inicializa la base de datos cuando la aplicación se inicia
    # Esto asegura que la tabla y el mensaje inicial existan
    initialize_db()
    app.run(host='0.0.0.0', port=5000)
