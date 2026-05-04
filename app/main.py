import os
import time
import random
import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Configuration from Environment
MODE = os.getenv("MODE", "stable").lower()
VERSION = os.getenv("APP_VERSION", "1.0.0")
start_time = time.time()

# Global Chaos State
chaos_state = {"mode": "recover", "duration": 0, "rate": 0.0}

class ChaosRequest(BaseModel):
    mode: str
    duration: int = 0
    rate: float = 0.0

@app.middleware("http")
async def apply_chaos_and_headers(request: Request, call_next):
    # 1. Handle "slow" chaos
    if MODE == "canary" and chaos_state["mode"] == "slow":
        time.sleep(chaos_state["duration"])

    # 2. Handle "error" chaos
    if MODE == "canary" and chaos_state["mode"] == "error":
        if random.random() < chaos_state["rate"]:
            return Response(content="Chaos Error", status_code=500)

    response = await call_next(request)

    # 3. Add Canary Header
    if MODE == "canary":
        response.headers["X-Mode"] = "canary"
    
    return response

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SwiftDeploy API",
        "mode": MODE,
        "version": VERSION,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

@app.get("/healthz")
def health_check():
    uptime_seconds = int(time.time() - start_time)
    return {"status": "healthy", "uptime": uptime_seconds}

@app.post("/chaos")
def trigger_chaos(config: ChaosRequest):
    if MODE != "canary":
        raise HTTPException(status_code=403, detail="Chaos only allowed in Canary mode")
    
    global chaos_state
    chaos_state = config.dict()
    return {"message": f"Chaos mode set to {chaos_state['mode']}"}

# --- THIS SECTION MUST BE AT THE BOTTOM AND NOT INDENTED ---
if __name__ == "__main__":
    # This reads the 'port: 5050' you set in manifest.yaml
    port_env = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port_env)