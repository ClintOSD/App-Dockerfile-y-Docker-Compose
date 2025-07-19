# src/app.py
from flask import Flask
import pymysql.cursors
import os
import time

app = Flask(__name__)

# Configuración de la base de datos obtenida de las variables de entorno
DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')

# Función para obtener una conexión a la base de datos
def get_db_connection():
    """
    Intenta conectar a la base de datos MySQL con reintentos.
    Esto es útil para esperar a que el servicio de la base de datos esté listo.
    """
    max_retries = 10
    retry_delay = 5 # segundos
    for i in range(max_retries):
        try:
            connection = pymysql.connect(host=DB_HOST,
                                       user=DB_USER,
                                       password=DB_PASSWORD,
                                       database=DB_NAME,
                                       cursorclass=pymysql.cursors.DictCursor)
            print(f"Conexión a la base de datos exitosa en el intento {i+1}")
            return connection
        except pymysql.Error as e:
            print(f"Error al conectar a la base de datos (intento {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise # Re-lanza la excepción si se agotan los reintentos
    return None # Nunca debería llegar aquí si raise es llamado

@app.route('/')
def hello_world():
    """
    Ruta principal que muestra un mensaje de "Hola Mundo" desde la base de datos.
    """
    message = "Error al conectar a la base de datos o recuperar el mensaje."
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Crear la tabla 'messages' si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content VARCHAR(255) NOT NULL
                )
            """)
            # Verificar si el mensaje "Hola Mundo" ya existe, si no, insertarlo
            cursor.execute("SELECT COUNT(*) FROM messages WHERE content = %s", ("Hola Mundo desde MySQL!",))
            if cursor.fetchone()['COUNT(*)'] == 0:
                cursor.execute("INSERT INTO messages (content) VALUES (%s)", ("Hola Mundo desde MySQL!",))
                connection.commit()
                print("Mensaje 'Hola Mundo desde MySQL!' insertado.")
            else:
                print("Mensaje 'Hola Mundo desde MySQL!' ya existe.")

            # Recuperar el mensaje de la base de datos
            cursor.execute("SELECT content FROM messages WHERE content = %s", ("Hola Mundo desde MySQL!",))
            result = cursor.fetchone()
            if result:
                message = result['content']
            else:
                message = "Mensaje 'Hola Mundo desde MySQL!' no encontrado después de la inserción."
    except Exception as e:
        message = f"Error de conexión o base de datos: {e}"
        print(f"Error en la aplicación: {e}")
    finally:
        # Asegura que la conexión se cierre si se estableció, sin depender de 'connection.open'
        if connection:
            connection.close()
            print("Conexión a la base de datos cerrada.")
    return f"<h1>{message}</h1>"

if __name__ == '__main__':
    # Ejecutar la aplicación Flask en todas las interfaces disponibles
    # Esto es necesario para que sea accesible desde Docker
    app.run(host='0.0.0.0', port=5000)

```text
# src/requirements.txt
Flask==2.3.3
PyMySQL==1.0.2
```dockerfile
# src/Dockerfile
# Usa una imagen base oficial de Python
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requisitos y la aplicación al contenedor
COPY requirements.txt .
COPY app.py .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5000 para que la aplicación sea accesible
EXPOSE 5000

# Comando para ejecutar la aplicación cuando el contenedor se inicie
CMD ["python", "app.py"]
