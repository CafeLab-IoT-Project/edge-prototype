from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from models import (
    db,
    initialize_database,
    StorageThreshold,
    SensorReading,
)


app = Flask(__name__)
CORS(app)


initialize_database()


@app.before_request
def before_request():
    if db.is_closed():
        db.connect(reuse_if_open=True)


@app.teardown_request
def teardown_request(exception):
    if not db.is_closed():
        db.close()


@app.get("/")
def health_check():
    return jsonify({
        "service": "CaféLab TrackSilo Edge API",
        "status": "running",
        "database": "connected"
    })


@app.get("/api/v1/edge/thresholds")
def get_thresholds():
    thresholds = (
        StorageThreshold
        .select()
        .where(StorageThreshold.is_current == True)
        .first()
    )

    if thresholds is None:
        return jsonify({
            "message": "No thresholds configured"
        }), 404

    return jsonify({
        "deviceId": thresholds.device_id,
        "minTemperature": thresholds.min_temperature,
        "maxTemperature": thresholds.max_temperature,
        "minHumidity": thresholds.min_humidity,
        "maxHumidity": thresholds.max_humidity,
        "updatedAt": thresholds.updated_at.isoformat()
    })


@app.put("/api/v1/edge/thresholds")
def update_thresholds():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    required_fields = [
        "deviceId",
        "minTemperature",
        "maxTemperature",
        "minHumidity",
        "maxHumidity"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    try:
        device_id = str(data["deviceId"])
        min_temperature = float(data["minTemperature"])
        max_temperature = float(data["maxTemperature"])
        min_humidity = float(data["minHumidity"])
        max_humidity = float(data["maxHumidity"])
    except ValueError:
        return jsonify({
            "error": "Temperature and humidity values must be numeric"
        }), 400

    if min_temperature >= max_temperature:
        return jsonify({
            "error": "minTemperature must be lower than maxTemperature"
        }), 400

    if min_humidity >= max_humidity:
        return jsonify({
            "error": "minHumidity must be lower than maxHumidity"
        }), 400

    StorageThreshold.update(is_current=False).execute()

    thresholds = StorageThreshold.create(
        device_id=device_id,
        min_temperature=min_temperature,
        max_temperature=max_temperature,
        min_humidity=min_humidity,
        max_humidity=max_humidity,
        is_current=True,
        updated_at=datetime.utcnow()
    )

    return jsonify({
        "message": "Thresholds updated successfully",
        "deviceId": thresholds.device_id,
        "minTemperature": thresholds.min_temperature,
        "maxTemperature": thresholds.max_temperature,
        "minHumidity": thresholds.min_humidity,
        "maxHumidity": thresholds.max_humidity,
        "updatedAt": thresholds.updated_at.isoformat()
    })


@app.post("/api/v1/edge/readings")
def register_reading():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    required_fields = ["deviceId", "temperature", "humidity"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    try:
        device_id = str(data["deviceId"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
    except ValueError:
        return jsonify({
            "error": "Temperature and humidity values must be numeric"
        }), 400

    thresholds = (
        StorageThreshold
        .select()
        .where(StorageThreshold.is_current == True)
        .first()
    )

    if thresholds is None:
        return jsonify({
            "error": "No thresholds configured"
        }), 500

    status = "OPTIMAL"
    actuator_command = "NONE"

    if temperature > thresholds.max_temperature or humidity > thresholds.max_humidity:
        status = "DANGER"
        actuator_command = "ACTIVATE"
    elif temperature < thresholds.min_temperature or humidity < thresholds.min_humidity:
        status = "WARNING"
        actuator_command = "NONE"

    reading = SensorReading.create(
        device_id=device_id,
        temperature=temperature,
        humidity=humidity,
        status=status,
        actuator_command=actuator_command,
        recorded_at=datetime.utcnow()
    )

    return jsonify({
        "readingId": reading.id,
        "deviceId": reading.device_id,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "status": reading.status,
        "actuatorCommand": reading.actuator_command,
        "recordedAt": reading.recorded_at.isoformat()
    }), 201


@app.get("/api/v1/edge/readings/latest")
def get_latest_reading():
    reading = (
        SensorReading
        .select()
        .order_by(SensorReading.recorded_at.desc())
        .first()
    )

    if reading is None:
        return jsonify({
            "message": "No readings registered yet"
        }), 404

    return jsonify({
        "readingId": reading.id,
        "deviceId": reading.device_id,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "status": reading.status,
        "actuatorCommand": reading.actuator_command,
        "recordedAt": reading.recorded_at.isoformat()
    })


@app.get("/api/v1/edge/readings")
def get_readings():
    limit = request.args.get("limit", default=20, type=int)

    if limit <= 0:
        limit = 20

    if limit > 100:
        limit = 100

    readings = (
        SensorReading
        .select()
        .order_by(SensorReading.recorded_at.desc())
        .limit(limit)
    )

    return jsonify([
        {
            "readingId": reading.id,
            "deviceId": reading.device_id,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "status": reading.status,
            "actuatorCommand": reading.actuator_command,
            "recordedAt": reading.recorded_at.isoformat()
        }
        for reading in readings
    ])


if __name__ == "__main__":
    app.run(debug=True)