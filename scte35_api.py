from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threefive
import base64
import requests
import asyncio
import logging
import json

# 🔧 Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("service_monitor.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI()

# 📦 Модели запросов
class SCTE35Request(BaseModel):
    scte35_string: str
    format: str  # "base64" or "hex"

class SCTE35EncodeRequest(BaseModel):
    scte35_json: dict
    format: str  # "base64" or "hex"

# 🔍 Декодирование SCTE-35
@app.post("/parse_scte35/")
async def parse_scte35(request: SCTE35Request):
    try:
        if request.format == "base64":
            scte35_data = base64.b64decode(request.scte35_string)
        elif request.format == "hex":
            scte35_data = bytes.fromhex(request.scte35_string)
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'base64' or 'hex'.")
        
        cue = threefive.Cue(scte35_data)
        cue.decode()
        return cue.get()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🧬 Кодирование SCTE-35
@app.post("/encode_scte35/")
async def encode_scte35(request: SCTE35EncodeRequest):
    try:
        cue = threefive.Cue()
        cue.set(request.scte35_json)
        cue.encode()
        binary_data = cue.packet
        if request.format == "base64":
            encoded = base64.b64encode(binary_data).decode()
        elif request.format == "hex":
            encoded = binary_data.hex()
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'base64' or 'hex'.")

        return {"encoded": encoded}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ❤️ Health-check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 🔁 Фоновая задача мониторинга
async def monitor_service_status():
    await asyncio.sleep(5)
    url = "http://localhost:8000/health"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200;
