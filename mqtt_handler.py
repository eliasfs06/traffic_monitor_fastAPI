import json
import paho.mqtt.client as mqtt
from models import TrafficRaw, TrafficStatus, DeviceHealth
from database import SessionLocal
from datetime import datetime

MQTT_BROKER = "107.172.94.10"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("Conectado ao MQTT")
    client.subscribe("traffic/raw/+")
    client.subscribe("traffic/health")

def on_message(client, userdata, msg):
    session = SessionLocal()
    try:
        payload = json.loads(msg.payload.decode())
        topic = msg.topic
        print(f"Mensagem recebida no tópico {topic}: {payload}")

        if topic.startswith("traffic/raw/"):
            street_id = topic.split("/")[-1] 

            raw = TrafficRaw(
                device_id=payload["device_id"],
                timestamp=parse_iso_timestamp(payload["timestamp"]),
                street_id=street_id,
                vehicle_count=payload["vehicle_count"],
                congestion_level=payload.get("congestion_level")
            )
            session.add(raw)

            status_topic = f"traffic/status/{street_id}"
            status_payload = {
                "device_id": payload["device_id"],
                "timestamp": payload["timestamp"],  
                "street_id": street_id,
                "congestion_level": payload.get("congestion_level", "desconhecido")
            }
            client.publish(status_topic, json.dumps(status_payload))

            status_payload["timestamp"] = parse_iso_timestamp(status_payload["timestamp"])
            status = TrafficStatus(**status_payload)
            session.add(status)

        elif topic == "traffic/health":
            health = DeviceHealth(
                device_id=payload["device_id"],
                timestamp=parse_iso_timestamp(payload["timestamp"]),
                status=payload["status"],
                uptime_s=payload["uptime_s"]
            )
            session.add(health)

        session.commit()
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
    finally:
        session.close()

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

def parse_iso_timestamp(iso_str):
    if iso_str.endswith("+00:00Z"):
        iso_str = iso_str.replace("+00:00Z", "+00:00")
    elif iso_str.endswith("Z"):
        iso_str = iso_str.replace("Z", "+00:00")
    return datetime.fromisoformat(iso_str)
