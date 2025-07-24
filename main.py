from fastapi import FastAPI
import models
from database import engine
from mqtt_handler import start_mqtt

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    start_mqtt()

@app.get("/")
def root():
    return {"message": "MQTT Traffic Backend is running"}
