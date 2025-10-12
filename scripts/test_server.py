from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Simple server working", "port": 8000}

@app.get("/test")
async def test():
    return {"status": "ok", "predictions_ready": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
