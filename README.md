# Traffic Monitor FastAPI

This project implements a real-time traffic monitoring backend using FastAPI, MQTT, and PostgreSQL. It listens to messages published by ESP32 devices and manages traffic status updates, storing data and broadcasting results to displays.

---

## Features

- Subscribes to MQTT topics from ESP32 traffic sensors
- Validates and stores traffic data and device health
- Publishes congestion status to `traffic/{street_id}/status`
- Serves a FastAPI server (can be extended with REST/GraphQL)
- Persists data using SQLAlchemy + PostgreSQL

---

## Technologies

- Python 3.10+
- FastAPI
- Paho MQTT Client
- SQLAlchemy
- PostgreSQL

---

## MQTT Configuration

- Broker: `107.172.94.10`  
- Port: `1883`  
- Authentication: None  

### Subscribed Topics

- `traffic/raw/+` — raw vehicle count and congestion level
- `traffic/all/health` — device keep-alive messages

### Published Topics

- `traffic/status/{street_id}` — broadcasted congestion level

---

## Database Models

- `traffic_raw`: stores raw sensor data
- `traffic_status`: stores computed status
- `device_health`: stores heartbeat and uptime

---

## Example Payloads

### `traffic/raw/{street_id}`

```json
{
  "device_id": "esp32-01",
  "timestamp": "2025-07-23T22:15:00Z",
  "street_id": "prudente_de_moraes",
  "vehicle_count": 12,
  "congestion_level": "high"
}
````

### `traffic/all/health`

```json
{
  "device_id": "esp32-01",
  "timestamp": "2025-07-23T22:15:10Z",
  "status": "online",
  "uptime_s": 3600
}
```

### `traffic/status/{street_id}`

```json
{
  "device_id": "esp32-01",
  "timestamp": "2025-07-23T22:15:05Z",
  "street_id": "prudente_de_moraes",
  "congestion_level": "medium"
}
```

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/eliasfs06/traffic-monitor-fastapi.git
cd traffic-monitor-fastapi
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate       # On Linux/macOS
# venv\Scripts\activate        # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Make sure PostgreSQL is running and accessible.

Update the `DATABASE_URL` in `database.py`:

```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
```

Replace the password or database name if different in your environment.

### 5. Run the application

```bash
uvicorn main:app --reload
```

The backend will connect to the MQTT broker and begin processing messages.