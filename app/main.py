from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.database import engine, Base
from app.api import auth, orders, wallets, transactions

# Create tables safely, and if we are on Railway and no DB is provided,
# SQLite will automatically be created in the ephemeral filesystem.
@app.on_event("startup")
async def startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Warning: Could not create tables on startup: {e}")
        
    # Start bot and background tasks
    import asyncio
    from bot import app as bot_app
    
    # Run polling as a background task
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("Telegram bot polling started.")

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
# Since 'app/' is now in root, 'frontend' is in root.
# os.path.dirname(os.path.abspath(__file__)) is '/opt/data/Never-give-up/app'
# So parent dir is '/opt/data/Never-give-up/'
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
# wait, if abspath is /opt/data/Never-give-up/app/main.py
# dirname is /opt/data/Never-give-up/app
# dirname(dirname) is /opt/data/Never-give-up/
# This is correct.
print(f"DEBUG: Checking frontend dir: {frontend_dir}")
if os.path.exists(frontend_dir):
    print(f"DEBUG: Frontend dir exists!")
    app.mount("/static", StaticFiles(directory=frontend_dir), name="frontend")

    @app.get("/app")
    async def mini_app():
        print(f"DEBUG: Serving index.html from {frontend_dir}")
        return FileResponse(os.path.join(frontend_dir, "index.html"))
else:
    # Try just current directory if that fails
    try_dir = os.path.join(os.getcwd(), "frontend")
    print(f"DEBUG: Frontend dir NOT FOUND at {frontend_dir}, trying {try_dir}")
    if os.path.exists(try_dir):
        app.mount("/static", StaticFiles(directory=try_dir), name="frontend")
        @app.get("/app")
        async def mini_app_fallback():
            return FileResponse(os.path.join(try_dir, "index.html"))


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