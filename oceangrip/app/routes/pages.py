from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Category, Product
from typing import Optional
from fastapi import Query


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
    
@router.get("/products")
async def product_listing(
    request: Request,
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[str] = Query(None),
    max_price: Optional[str] = Query(None),
    sort: str = "newest", #Here via keyword 'newest' it shows the result in asc to desc order
):
    query = select(Product)

    if category:
        cat_result = await db.execute(select(Category).where(Category.slug == category))
        cat_obj = cat_result.scalar_one_or_none()
        if cat_obj:
            query = query.where(Product.category_id == cat_obj.id)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    if min_price and min_price.strip():
        query = query.where(Product.price >= float(min_price))
    if max_price and max_price.strip():
        query = query.where(Product.price <= float(max_price))
    if sort == "price_low":
            query = query.order_by(Product.price.asc())
    elif sort == "price_high":
            query = query.order_by(Product.price.desc())
    else:
            query = query.order_by(Product.price.desc())
            
    result = await db.execute(query)
    products = result.scalars().all()
    categories_result = await db.execute(select(Category))
    categories = categories_result.scalars().all()
        
    return templates.TemplateResponse(
        request=request,
        name="product_listing.html",
        context={
                "products" :products,
                "categories":categories,
                "search" : search or "",
                "sort": sort,
                "selected_category": category,
        }
    )
    
@router.get("/about")
async def about_page(request: Request):
    return templates.TemplateResponse(request=request, name="about.html", context={})

@router.get("/contact")
async def contact_page(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html", context={})

@router.get("/faq")
async def faq_page(request: Request):
    return templates.TemplateResponse(request=request, name="faq.html", context={})

@router.get("/privacy")
async def privacy_page(request:Request):
    return templates.TemplateResponse(request=request, name="privacy.html", context={})

@router.get("/terms")
async def terms_page(request: Request):
    return templates.TemplateResponse(request=request, name="terms.html", context={})

