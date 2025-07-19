# src/app.py
from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

@app.route('/')
def hello():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "db"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", "example"),
            database=os.environ.get("DB_NAME", "testdb")
        )
        return "Hola Mundo! Conexión a MySQL exitosa Crear por Victor Galvez 2023-1836✅"
    except mysql.connector.Error as err:
        return f"Error al conectar a la base de datos ❌: {err}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
