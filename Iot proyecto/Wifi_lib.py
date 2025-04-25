import network
import ubinascii
import urequests as requests
from secretsp import secrets  # Archivo separado con las credenciales Wi-Fi
import socket
from machine import Pin
import time
import sys
import gc
from utime import sleep

ssid = secrets['ssid']
password = secrets['password']

# Función para inicializar la conexión Wi-Fi
def wifi_init():
    # Configurar la plataforma dependiendo si es Raspberry Pi Pico W o ESP32
    if sys.platform == 'rp2':
        # Raspberry Pi Pico W
        print("Inicializando Wi-Fi en Raspberry Pi Pico W")
        # Establecer el país para evitar posibles errores en el Wi-Fi
        import rp2
        rp2.country('DE')  # Ajusta según tu país si lo necesitas
    elif sys.platform == 'esp32':
        # ESP32
        print("Inicializando Wi-Fi en ESP32")
        # No es necesario establecer el país en ESP32

    # Configuración de la interfaz Wi-Fi en modo estación (client)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print('Esperando encender el modulo wifi...')
    sleep(3) # wait three seconds for the chip to power up and initialize
    wlan.connect(ssid, password)       
    print('Esperando encender el modulo wifi...')
    sleep(3) # wait three seconds for the chip to power up and initialize

    while wlan.active() == False:
      pass
    print('Coneccion exitosa')
    print('IP: ', wlan.ifconfig()[0])
    print('RSSI: ', wlan.status('rssi'))    
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    print("MAC:",mac)
    print("Canal:",wlan.config('channel'))
    print("SSID:",wlan.config('essid'))
    print("power:",wlan.config('txpower'))
    print("Hostname:",wlan.config('hostname'))


# Función para cargar una página HTML desde un archivo
def get_html(html_name):
    try:
        with open(html_name, 'r') as file:
            html = file.read()
        return html
    except Exception as e:
        print(f"Error al leer el archivo {html_name}: {e}")
        return "<html><body>Error al cargar el archivo HTML</body></html>"

