import mysql.connector

# Configuración de conexión a la base de datos
config = {
    'host': 'localhost',        # Cambia si tu DB está en otro host
    'user': 'root',             # Tu usuario MySQL
    'password': '',             # Tu contraseña MySQL
    'database': 'BD_DHT22_V0',   # Nombre de la base de datos
    'port': '3306'
}

try:
    # Conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    cursor = conexion.cursor()

    # Consulta para obtener todos los datos
    consulta = "SELECT * FROM DatosDHT22 ORDER BY nreg DESC"
    cursor.execute(consulta)

    # Obtener los nombres de columna
    columnas = [desc[0] for desc in cursor.description]
    print(" | ".join(columnas))
    print("-" * 80)

    # Mostrar los resultados
    for fila in cursor.fetchall():
        print(" | ".join(str(dato) for dato in fila))

except mysql.connector.Error as err:
    print(f"Error al conectar a la base de datos: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conexion' in locals() and conexion.is_connected():
        conexion.close()
