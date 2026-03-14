from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import uv, postcode

load_dotenv()

app = FastAPI(title="SunSmart API", version="1.0.0")

# Allow frontend (and EC2 cross-origin) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uv.router)
app.include_router(postcode.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "SunSmart API running"}