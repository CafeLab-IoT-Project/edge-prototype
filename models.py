from datetime import datetime
import os

from dotenv import load_dotenv
from peewee import (
    Model,
    AutoField,
    CharField,
    FloatField,
    DateTimeField,
    BooleanField,
)
from playhouse.db_url import connect


load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not configured. "
        "Create a .env file or configure it in your environment."
    )

db = connect(DATABASE_URL)


class BaseModel(Model):
    class Meta:
        database = db


class StorageThreshold(BaseModel):
    id = AutoField()
    device_id = CharField(default="tracksilo-001")
    min_temperature = FloatField(default=10.0)
    max_temperature = FloatField(default=22.0)
    min_humidity = FloatField(default=40.0)
    max_humidity = FloatField(default=65.0)
    is_current = BooleanField(default=True)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "storage_thresholds"


class SensorReading(BaseModel):
    id = AutoField()
    device_id = CharField(default="tracksilo-001")
    temperature = FloatField()
    humidity = FloatField()
    status = CharField()
    actuator_command = CharField()
    recorded_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "sensor_readings"


def initialize_database():
    if db.is_closed():
        db.connect(reuse_if_open=True)

    db.create_tables([StorageThreshold, SensorReading], safe=True)

    current_threshold = (
        StorageThreshold
        .select()
        .where(StorageThreshold.is_current == True)
        .first()
    )

    if current_threshold is None:
        StorageThreshold.create(
            device_id="tracksilo-001",
            min_temperature=10.0,
            max_temperature=22.0,
            min_humidity=40.0,
            max_humidity=65.0,
            is_current=True,
            updated_at=datetime.utcnow()
        )