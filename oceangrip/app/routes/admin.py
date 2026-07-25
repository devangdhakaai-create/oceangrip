from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Product, Category

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")
ADMIN_PASSWORD = "oceangrip2027" #i will move it later to .env file

def is_admin(request: Request) -> bool:
    return request.session.get("is_admin", False)

@router.get("/login")
async def admin_login_page(request: Request):
    return templates.TemplateResponse(request=request,  name="admin/login.html", context={})

@router.post("/login")
async def admin_login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["is_admin"] = True
        return RedirectResponse(url="/admin/products", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"error":"Incorrect Password"}
    )
    
@router.get("/logout")
async def admin_logout(request: Request):
    request.session["is_admin"] = False
    return RedirectResponse(url="/admin/login",  status_code=303)

@router.get("/products")
async def admin_product_list(request: Request, db: AsyncSession = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    result = await db.execute(select(Product))
    products = result.scalars().all()
    
    return templates.TemplateResponse(
        request=request,
        name="admin/product_list.html",
        context={"products":products}
    )
    
@router.get("/products/add")
async def admin_add_product_page(request: Request, db: AsyncSession = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    
    return templates.TemplateResponse(
        request=request,
        name="admin/product_form.html",
        context={"categories":categories}
    )
    
@router.post("/products/add")
async def admin_add_product(
    request: Request,
    db: AsyncSession =Depends(get_db),
    name: str = Form(...),
    slug: str =Form(...),
    description: str =Form(...),
    price: float =Form(...),
    stock: int = Form(0),
    image_url: str =Form(""),
    specifications: str =Form(""),
    category_id: int = Form(...),
):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    
    product = Product(
        name=name, slug=slug, description=description, price=price, stock=stock,
        image_url=image_url, specifications=specifications, category_id=category_id,
    )
    db.add(product)
    await db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)

@router.get("/products/edit/{product_id}")
async def admin_edit_product_page(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    cat_result = await db.execute(select(Category))
    categories = cat_result.scalars().all()
    
    return templates.TemplateResponse(
        request=request,
        name="admin/product_form.html",
        context={"categories":categories, "product":product}
    )
    
@router.post("/products/edit/{product_id}")
async def admin_edit_product(
    product_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str =Form(...),
    slug: str = Form(...),
    description: str =Form(...),
    price: float =Form(...),
    stock: int = Form(0),
    image_url: str = Form(""),
    specifications: str = Form(""),
    category_id: int = Form(...),
):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    product.name = name
    product.slug = slug
    product.description = description
    product.price = price
    product.stock = stock
    product.image_url = image_url
    product.specifications = specifications
    product.category_id = category_id
    await db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)

@router.post("/products/delete/{product_id}")
async def admin_delete_product(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product:
        await db.delete(product)
        await db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)