from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Ethiopian P2P Crypto Market API is live"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
