import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import panel as pn
import seaborn as sns
from matplotlib.dates import DateFormatter

# Habilitar Panel
pn.extension()

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',       # Cambiar según sea necesario
    'password': '',       # Cambiar según sea necesario
    'database': 'BD_DHT22_V0'
}

# Función para leer datos de la tabla DatosDHT22
def generar_datos(n):
    conn = mysql.connector.connect(**db_config)
    query = "SELECT fecha_hora, temp, humed, ADCtem, ADC0, aux FROM DatosDHT22 ORDER BY nreg DESC LIMIT %s"
    data = pd.read_sql(query, conn, params=(n,))
    conn.close()
    return data.sort_values('fecha_hora')  # Orden cronológico

# Función para crear el gráfico según el tipo elegido
def crear_grafico(tipo_grafico, n):
    data = generar_datos(n)

    fig, ax = plt.subplots(figsize=(10, 5))
    if tipo_grafico == 'Gráfico de línea':
        ax.plot(data['fecha_hora'], data['temp'], label='Temp (°C)', color='red')
        ax.plot(data['fecha_hora'], data['humed'], label='Humedad (%)', color='blue')
        ax.plot(data['fecha_hora'], data['ADCtem'], label='ADCtem', color='green')
        ax.plot(data['fecha_hora'], data['ADC0'], label='ADC0', color='purple')
        ax.plot(data['fecha_hora'], data['aux'], label='Aux', color='orange')
        ax.set_title('Serie de Tiempo de Variables DHT22')
        ax.set_xlabel('Fecha y Hora')
        ax.set_ylabel('Valores')
        ax.legend()
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate()

    elif tipo_grafico == 'Boxplot':
        sns.boxplot(data=data[['temp', 'humed', 'ADCtem', 'ADC0', 'aux']], ax=ax)
        ax.set_title('Boxplot de Variables Sensadas')
        ax.set_ylabel('Valor')
        ax.set_xlabel('Variable')

    elif tipo_grafico == 'Histograma':
        sns.histplot(data.melt(value_vars=['temp', 'humed', 'ADCtem', 'ADC0', 'aux']),
                     x='value', hue='variable', bins=20, kde=True, ax=ax)
        ax.set_title('Histograma de Variables')

    elif tipo_grafico == 'Gráfico de dispersión':
        ax.scatter(data['fecha_hora'], data['temp'], label='Temp', alpha=0.7)
        ax.scatter(data['fecha_hora'], data['humed'], label='Humed', alpha=0.7)
        ax.scatter(data['fecha_hora'], data['ADCtem'], label='ADCtem', alpha=0.7)
        ax.scatter(data['fecha_hora'], data['ADC0'], label='ADC0', alpha=0.7)
        ax.scatter(data['fecha_hora'], data['aux'], label='Aux', alpha=0.7)
        ax.set_title('Dispersión vs Tiempo')
        ax.set_xlabel('Fecha y Hora')
        ax.set_ylabel('Valor')
        ax.legend()
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate()

    return fig

# Crear widgets interactivos
slider = pn.widgets.IntSlider(name='Cantidad de datos', start=5, end=100, step=5, value=20)
dropdown = pn.widgets.Select(name='Tipo de gráfico', options=['Gráfico de línea', 'Boxplot', 'Histograma', 'Gráfico de dispersión'], value='Gráfico de línea')

# Crear gráfico dinámico con Panel
grafico_interactivo = pn.bind(crear_grafico, tipo_grafico=dropdown, n=slider)

# Análisis descriptivo simple
def analisis_descriptivo(n):
    df = generar_datos(n)
    desc = df.describe().T
    markdown = "### Estadísticas descriptivas\n"
    for var in desc.index:
        media = desc.loc[var, 'mean']
        std = desc.loc[var, 'std']
        markdown += f"- {var}: media = {media:.2f}, desviación estándar = {std:.2f}\n"
    return pn.pane.Markdown(markdown)

# Panel general
dashboard = pn.Column(
    "# 🌡️ Dashboard IoT - Sensor DHT22",
    "Ajusta los controles para visualizar datos desde la tabla `DatosDHT22`",
    pn.Row(slider, dropdown),
    grafico_interactivo,
    pn.bind(analisis_descriptivo, n=slider)
)

# Mostrar dashboard
dashboard.show()
