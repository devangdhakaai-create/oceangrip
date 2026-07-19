from fastapi import FastAPI

app = FastAPI(title="OceanGrip")

@app.get("/")
async def read_root():
    return {"message":"Welcome to OceanGrip - Fishing Gear Store"}