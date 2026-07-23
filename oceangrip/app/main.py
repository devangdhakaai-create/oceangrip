from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.routes import pages, cart

app = FastAPI(title="OceanGrip")

app.add_middleware(SessionMiddleware, secret_key="oceangrip-dev-secret-i-will-change-it-later-with-actual-one")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)
app.include_router(cart.router)