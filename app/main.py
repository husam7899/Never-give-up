from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.database import engine, Base
from app.api import auth, orders, wallets, transactions

# Create tables safely, and if we are on Railway and no DB is provided,
# SQLite will automatically be created in the ephemeral filesystem.
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
except Exception as e:
    print(f"Warning: Could not create tables on startup: {e}")

app = FastAPI(
    title="Ethiopian P2P Crypto Market",
    description="P2P USDT marketplace - Telegram Mini App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(wallets.router)
app.include_router(transactions.router)

# Serve frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
print(f"DEBUG: Checking frontend dir: {frontend_dir}")
if os.path.exists(frontend_dir):
    print(f"DEBUG: Frontend dir exists!")
    app.mount("/static", StaticFiles(directory=frontend_dir), name="frontend")

    @app.get("/app")
    async def mini_app():
        print(f"DEBUG: Serving index.html from {frontend_dir}")
        return FileResponse(os.path.join(frontend_dir, "index.html"))
else:
    print(f"DEBUG: Frontend dir NOT FOUND at {frontend_dir}")


@app.get("/")
async def root():
    return {
        "name": "Ethiopian P2P Crypto Market",
        "version": "1.0.0",
        "status": "live",
        "docs": "/docs",
        "mini_app": "/app",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}