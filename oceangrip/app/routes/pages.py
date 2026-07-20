from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Category, Product


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def homepage(request: Request, db: AsyncSession = Depends(get_db)):
    categories_result = await db.execute(select(Category)) # It builds a SQL query
    categories = categories_result.scalars().all()  #& this gives us clean python object
    
    
    products_result = await db.execute(select(Product))
    featured_products = products_result.scalars().all()
    
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "categories": categories,
        "products": featured_products,
    })