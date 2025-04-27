from machine import Pin, PWM, ADC, time_pulse_us
import dht
import time
import network
import urequests
import ujson
from Wifi_lib import wifi_init  # Usar tu librería WiFi_lib

# ------------------ CONFIGURACIÓN WIFI ------------------
wifi_init()

# Pines de conexión
pin_pot = 34   # Potenciómetro (no usado aquí)
pin_led = 32   # LED para PWM
pin_dht = 4    # DHT22 Data Pin
trig_pin = 5   # Trigger del sensor ultrasónico
echo_pin = 18  # Echo del sensor ultrasónico

# Configuración de sensores
dht_sensor = dht.DHT22(Pin(pin_dht))
led_pwm = PWM(Pin(pin_led), freq=1000)
trig = Pin(trig_pin, Pin.OUT)
echo = Pin(echo_pin, Pin.IN)

SOUND_SPEED = 0.034  # Velocidad del sonido (cm/us)

def leer_dht22():
    dht_sensor.measure()
    temperatura = dht_sensor.temperature()
    humedad = dht_sensor.humidity()
    return temperatura, humedad

def get_distance():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    duration = time_pulse_us(echo, 1, 30000)  # Timeout de 30ms
    distance_cm = duration * SOUND_SPEED / 2
    return distance_cm

def definir_color_led(distancia):
    if distancia <= 5:
        return 1  # Nivel bajo
    elif distancia <= 8:
        return 2  # Nivel medio
    else:
        return 3  # Nivel alto

def enviar_datos(temperatura, humedad, distancia, color_led, id_planta):
    url = "http://192.168.0.9/conexion.php"  # URL corregida
    headers = {'Content-Type': 'application/json'}
    data = {
        "temperatura": temperatura,
        "humedad": humedad,
        "distancia": distancia,
        "color_led": color_led,
        "id_planta": id_planta
    }
    try:
        response = urequests.post(url, data=ujson.dumps(data), headers=headers)
        print("Respuesta del servidor:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar datos:", e)

# ------------------ BUCLE PRINCIPAL ------------------
id_planta = 1  # Siempre enviar 1
while True:
    try:
        temperatura, humedad = leer_dht22()
        distancia = get_distance()

        # Calcular color_led según distancia
        color_led = definir_color_led(distancia)

        print("Temperatura: {:.2f}°C, Humedad: {:.2f}%, Distancia: {:.2f}cm, Nivel: {}".format(
            temperatura, humedad, distancia, color_led))
        
        # Encender LED (opcional si quieres mostrar con intensidad distinta)
        led_pwm.duty(512)  # Un valor medio, si quieres ajustar

        # Enviar datos al servidor
        enviar_datos(temperatura, humedad, distancia, color_led, id_planta)

    except OSError as e:
        print("Error al leer sensores:", e)

    time.sleep(5)  # Espera de 5 segundos