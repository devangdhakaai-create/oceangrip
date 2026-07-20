from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import pages

app = FastAPI(title="OceanGrip")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)