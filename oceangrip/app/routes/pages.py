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
    
@router.get("/products/{slug}")
async def product_details (slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.slug == slug))
    product = result.scalar_one_or_none() # Here scalar gives the single column/object & one_or_none expect exactly 0 or 1 matching rows, means if 1 is found then return the product object intead none .
    if not product:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={},
            status_code=404
        )
    related_result  = await  db.execute(
        select(Product).where (
            Product.category_id == product.category_id,
            Product.id != product.id
        ).limit(4)
    )
    related_products = related_result.scalars().all()
    
    return templates.TemplateResponse(
        request=request,
        name="product_details.html",
        context={
            "product":product,
            "related_products": related_products,
        }
    )
    