# CaféLab TrackSilo Edge API

Edge API desarrollado para el prototipo IoT **TrackSilo** de CaféLab.  
Este servicio representa la capa de **Edge Computing** entre el dispositivo IoT ESP32 y el backend principal de CaféLab.

El objetivo del Edge API es permitir que el dispositivo IoT consulte umbrales ambientales, envíe lecturas de temperatura y humedad, y reciba una respuesta con el estado ambiental y el comando de actuador correspondiente.

---

## 1. Propósito del proyecto

TrackSilo es un dispositivo IoT diseñado para monitorear las condiciones ambientales del almacenamiento de café verde.

Este Edge API permite:

- Configurar umbrales de temperatura y humedad.
- Consultar los umbrales actuales desde el ESP32.
- Recibir lecturas del sensor DHT22.
- Evaluar si las condiciones están en estado óptimo, advertencia o peligro.
- Responder al ESP32 con un comando de actuador.
- Guardar lecturas ambientales en una base de datos local SQLite.

---

## 2. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python | Lenguaje principal del Edge API |
| Flask | Framework para construir la API REST |
| Peewee ORM | Mapeo de modelos hacia SQLite |
| SQLite | Base de datos local del Edge API |
| Flask-CORS | Permitir consumo desde clientes externos |
| Gunicorn | Servidor para despliegue en Azure App Service |
| Wokwi | Simulación del ESP32 y sensor IoT |
| ESP32 / Arduino C++ | Embedded Application del dispositivo TrackSilo |

---

## 3. Arquitectura general

El flujo de comunicación propuesto es el siguiente:

```text
ESP32 / DHT22
   ↓
TrackSilo Embedded Application
   ↓ HTTP
CaféLab TrackSilo Edge API
   ↓
Evaluación de umbrales y comando de actuador
   ↓
Backend Cloud de CaféLab / Dashboard