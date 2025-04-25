-- Crear base de datos
CREATE DATABASE IF NOT EXISTS BD_DHT22_V0;
USE BD_DHT22_V0;

-- Crear tabla DatosDHT22
CREATE TABLE IF NOT EXISTS DatosDHT22 (
    nreg INT AUTO_INCREMENT PRIMARY KEY,
    disp_id INT NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temp FLOAT,
    humed FLOAT,
    ADCtem FLOAT,
    ADC0 FLOAT,
    aux FLOAT
);
