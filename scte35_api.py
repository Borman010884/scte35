
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threefive
import base64
import requests
import asyncio
import logging

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

# 📦 Модель запроса
class SCTE35Request(BaseModel):
    scte35_string: str
    format: str  # "base64" or "hex"

# 🔍 Основной эндпоинт
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

# ❤️ Health-check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 🔁 Фоновая задача мониторинга
async def monitor_service_status():
    url = "http://localhost:8000/health"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logging.info("✅ Service is UP")
            else:
                logging.warning(f"⚠️ Service returned status: {response.status_code}")
        except Exception as e:
            logging.error(f"❌ Error checking service: {e}")
        await asyncio.sleep(600)  # интервал в секундах

# 🚀 Запуск фоновой задачи при старте
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_service_status())

# 🔌 Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
