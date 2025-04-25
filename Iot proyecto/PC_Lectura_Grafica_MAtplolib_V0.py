# grafica en tiempo real
import mysql.connector
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.animation import FuncAnimation

# Configuración de conexión
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'BD_DHT22_V0'
}

# Inicialización de figura
fig, ax = plt.subplots()
ax.set_title('Visualización en Tiempo Real - Sensor DHT22')
ax.set_xlabel('Fecha y Hora')
ax.set_ylabel('Valores')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

# Colores para cada variable
colores = {
    'temp': 'red',
    'humed': 'blue',
    'ADCtem': 'green',
    'ADC0': 'purple',
    'aux': 'orange'
}

# Función para obtener datos de la BD
def obtener_datos():
    conexion = mysql.connector.connect(**config)
    cursor = conexion.cursor()
    consulta = "SELECT fecha_hora, temp, humed, ADCtem, ADC0, aux FROM DatosDHT22 ORDER BY nreg DESC LIMIT 20"
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return resultados[::-1]  # Orden cronológico

# Función de actualización de la gráfica
def actualizar(frame):
    ax.clear()
    datos = obtener_datos()
    
    fechas = [row[0] for row in datos]
    fechas = [datetime.strptime(str(f), '%Y-%m-%d %H:%M:%S') for f in fechas]
    temp = [row[1] for row in datos]
    humed = [row[2] for row in datos]
    adc_tem = [row[3] for row in datos]
    adc0 = [row[4] for row in datos]
    aux = [row[5] for row in datos]

    ax.plot(fechas, temp, label='Temp (°C)', color=colores['temp'])
    ax.plot(fechas, humed, label='Humed (%)', color=colores['humed'])
    ax.plot(fechas, adc_tem, label='ADCtemp', color=colores['ADCtem'])
    ax.plot(fechas, adc0, label='ADC0', color=colores['ADC0'])
    ax.plot(fechas, aux, label='Aux', color=colores['aux'])

    ax.set_title('Datos DHT22 en Tiempo Real')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Valor')
    ax.legend(loc='upper left')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()

# Animación con intervalo de actualización
ani = FuncAnimation(fig, actualizar, interval=50)  # 5 mili segundos

# Mostrar la gráfica
plt.tight_layout()
plt.show()
