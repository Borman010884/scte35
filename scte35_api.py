
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import requests
import asyncio
import logging
from contextlib import asynccontextmanager

# 🔧 Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("service_monitor.log"),
        logging.StreamHandler()
    ]
)

# 🔁 Фоновая задача мониторинга
async def monitor_service_status():
    await asyncio.sleep(5)  # ⏳ Подождать немного после старта
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
        await asyncio.sleep(600)

# 🔄 Контекст жизненного цикла
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(monitor_service_status())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

# 📦 Модель запроса
class SCTE35Request(BaseModel):
    scte35_string: str
    format: str  # "base64" or "hex"

# 📦 Модель запроса для энкодинга
class SCTE35EncodeRequest(BaseModel):
    event_id: int
    duration: float
    pts_time: int
    format: str  # "base64" или "hex"

# 🔍 Основной эндпоинт для парсинга
@app.post("/parse_scte35/")
async def parse_scte35(request: SCTE35Request):
    try:
        if request.format == "base64":
            scte35_data = base64.b64decode(request.scte35_string)
        elif request.format == "hex":
            scte35_data = bytes.fromhex(request.scte35_string)
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'base64' or 'hex'.")
        
        # Заглушка вместо threefive
        cue = {"decoded_data": "example_decoded_data"}
        return cue

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔍 Основной эндпоинт для энкодинга
@app.post("/encode_scte35/")
async def encode_scte35(request: SCTE35EncodeRequest):
    try:
        # Заглушка вместо threefive
        scte35_data = f"event_id={request.event_id}, duration={request.duration}, pts_time={request.pts_time}"
        if request.format == "base64":
            scte35_string = base64.b64encode(scte35_data.encode()).decode()
        elif request.format == "hex":
            scte35_string = scte35_data.encode().hex()
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'base64' or 'hex'.")
        
        return {"scte35_string": scte35_string, "format": request.format}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ❤️ Health-check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 🔌 Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
