import sys
import os
import time
import machine
from machine import Pin
import dht
import network
import urequests
import ujson
from Wifi_lib import wifi_init, get_html

wifi_init()

# ------------------- CLASE PARA DETECTAR PLACA -------------------
class Board:
    class BoardType:
        PICO_W = 'Raspberry Pi Pico W'
        PICO = 'Raspberry Pi Pico'
        RP2040 = 'RP2040'
        ESP8266 = 'ESP8266'
        ESP32 = 'ESP32'
        UNKNOWN = 'Unknown'

    def __init__(self):
        self.type = self.detect_board_type()

    def detect_board_type(self):
        sysname = os.uname().sysname.lower()
        machine_name = os.uname().machine.lower()

        if sysname == 'rp2' and 'pico w' in machine_name:
            return self.BoardType.PICO_W
        elif sysname == 'rp2' and 'pico' in machine_name:
            return self.BoardType.PICO
        elif sysname == 'rp2' and 'rp2040' in machine_name:
            return self.BoardType.RP2040
        elif sysname == 'esp8266':
            return self.BoardType.ESP8266
        elif sysname == 'esp32' and 'esp32' in machine_name:
            return self.BoardType.ESP32
        else:
            return self.BoardType.UNKNOWN

# ------------------- DETECCIÓN DE PLACA Y PINES -------------------
BOARD_TYPE = Board().type
print("Tipo de placa: " + BOARD_TYPE)

if BOARD_TYPE == Board.BoardType.PICO_W:
    led = Pin("LED", Pin.OUT)
    ledv = Pin(6, Pin.OUT)
    data_pin = 15
elif BOARD_TYPE == Board.BoardType.PICO or BOARD_TYPE == Board.BoardType.RP2040:
    led = Pin(25, Pin.OUT)
    data_pin = 15
elif BOARD_TYPE == Board.BoardType.ESP8266:
    led = Pin(2, Pin.OUT)
    data_pin = 0
elif BOARD_TYPE == Board.BoardType.ESP32:
    led = Pin(2, Pin.OUT)
    ledv = Pin(4, Pin.OUT)  # LED secundario
    data_pin = 14           # Pin para DHT22
else:
    print("Placa desconocida, usando GPIO 2 y pin de datos 0 por defecto.")
    led = Pin(2, Pin.OUT)
    data_pin = 0

# ------------------- CONFIGURACIÓN SENSOR -------------------
dht_sensor = dht.DHT22(Pin(data_pin))
umbral_temperatura = 30.0
umbral_humedad = 70.0

# ------------------- CONFIGURACIÓN ADC PARA ESP32 -------------------
tempint = machine.ADC(machine.Pin(34))  # GPIO34
tempint.atten(machine.ADC.ATTN_11DB)

ADC0 = machine.ADC(machine.Pin(35))     # GPIO35
ADC0.atten(machine.ADC.ATTN_11DB)

# ------------------- FUNCIÓN DE LECTURA -------------------
def leer_dht22():
    dht_sensor.measure()
    temperatura = dht_sensor.temperature()
    humedad = dht_sensor.humidity()
    return temperatura, humedad

def controlar_led(temperatura, humedad):
    if temperatura > umbral_temperatura or humedad > umbral_humedad:
        led.on()
        print("Alta temperatura o humedad, LED encendido")
    else:
        led.off()
        print("Temperatura y humedad normales, LED apagado")

# ------------------- ENVÍO DE DATOS JSON -------------------
def enviar_datos_json(disp_id, temp, humed, adc_temp, adc0, aux):
    url = "http://192.168.189.231/insertar_dht22.php"
    headers = {'Content-Type': 'application/json'}
    datos = {
        "disp_id": disp_id,
        "temp": temp,
        "humed": humed,
        "ADCtem": adc_temp,
        "ADC0": adc0,
        "aux": aux
    }
    try:
        respuesta = urequests.post(url, data=ujson.dumps(datos), headers=headers)
        print("Respuesta del servidor:", respuesta.text)
        respuesta.close()
    except Exception as e:
        print("Error al enviar los datos:", e)

# ------------------- BUCLE PRINCIPAL -------------------
disp_id = 1
while True:
    try:
        temperatura, humedad = leer_dht22()
        
        ADCtem = tempint.read() * 3.3 / 4095  # Convertir a voltaje
        ADCtem_simulado = 27 - (ADCtem - 0.706) / 0.001721
        
        ADC0_val = ADC0.read()
        ADC0_simulado = ADC0_val * 100 / 4095
        
        if ADC0_simulado < 50:
            aux_simulado = 10
            ledv.value(1)
        else:
            aux_simulado = 5
            ledv.value(0)

        print(disp_id, temperatura, humedad, ADCtem_simulado, ADC0_simulado, aux_simulado)
        controlar_led(temperatura, humedad)

        enviar_datos_json(disp_id, temperatura, humedad, ADCtem_simulado, ADC0_simulado, aux_simulado)

    except OSError as e:
        print("Error al leer el sensor DHT22:", e)

    time.sleep(1)
