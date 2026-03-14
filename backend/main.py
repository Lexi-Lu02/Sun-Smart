from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import uv

app = FastAPI(title="SunSmart API", version="1.0.0")

# Allow frontend dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uv.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "SunSmart API running"}