from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.routes import pages, cart, admin, auth

app = FastAPI(title="OceanGrip")

app.add_middleware(SessionMiddleware, secret_key="oceangrip-secret-i-will-change-it-later-with-strong-one")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)
app.include_router(cart.router)
app.include_router(admin.router)
app.include_router(auth.router)