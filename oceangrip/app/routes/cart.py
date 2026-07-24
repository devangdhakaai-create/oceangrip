from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Product
import random
import string
from app.models import Order, OrderItem

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/cart/add/{product_id}")
async def add_to_cart(product_id: int, request: Request, quantity: int = Form(1)):
    cart = request.session.get("cart", {})
    product_id_str = str(product_id)
    
    cart[product_id_str]  = cart.get(product_id_str, 0) + quantity
    request.session["cart"] = cart
    
    return RedirectResponse(url="/cart", status_code=303)


@router.get("/cart")
async def view_cart(request: Request, db: AsyncSession = Depends(get_db)):
    cart = request.session.get("cart", {})
    items = []
    subtotal  = 0.0
    
    for product_id_str, qty in cart.items():
        result = await db.execute(select(Product).where(Product.id == int(product_id_str)))
        product = result.scalar_one_or_none()
        
        if product:
            item_total = product.price*qty
            subtotal += item_total
            items.append({"product":product, "quantity": qty, "item_total": item_total })
            
            
    shipping = 50.00 if subtotal > 0 else 0.00
    total = subtotal + shipping
    
    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
        }
    )
    

@router.post("/cart/remove/{product_id}")
async def remove_from_cart(product_id: int, request: Request):
    cart = request.session.get("cart",{})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return RedirectResponse(url="/cart", status_code=303)


@router.post("/cart/update/{product_id}")
async def update_cart(product_id: int, request:Request, quantity: int = Form(...)):
    cart = request.session.get("cart", {})
    if quantity > 0:
        cart[str(product_id)] = quantity
    else:
        cart.pop(str(product_id), None)
    
    request.session["cart"] = cart
    return RedirectResponse(url="/cart", status_code=303)


def generate_order_number():
    return "OG" + "".join(random.choices(string.digits, k=8))

@router.get("/checkout")
async def checkout_page(request: Request, db: AsyncSession = Depends(get_db)):
    cart = request.session.get("cart", {})
    items = []
    subtotal = 0.00

    for product_id_str , qty in cart.items():
        result = await db.execute (select(Product).where(Product.id == int(product_id_str)) )
        product = result.scalar_one_or_none()
        
        if product:
            item_total = product.price * qty
            subtotal += item_total
            items.append({"product": product, "quantity": qty, "item_total": item_total})
            
    if not items:
        return RedirectResponse(url="/cart", status_code=303)
    
    shipping = 50.00
    total = subtotal + shipping
    
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
        }
    )
    
@router.post("/checkout")
async def place_order(
    request: Request,
    db: AsyncSession = Depends(get_db),
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    pincode: str = Form(...),
    delivery_option: str = Form("Standard"),
):
    cart = request.session.get("cart", {})
    items = []
    subtotal = 0.00
    
    for product_id_str, qty in cart.items():
        result = await db.execute(select(Product).where(Product.id == int(product_id_str)))
        product = result.scalar_one_or_none()
        if product:
            item_total = product.price *qty
            subtotal += item_total
            items.append({"product":product, "quantity": qty})
            
    if not items:
        return RedirectResponse(url="/cart", status_code=303)
    
    shipping = 50.00
    total = shipping + subtotal
    
    order = Order(
        order_number=generate_order_number(),
        full_name=full_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        pincode=pincode,
        delivery_option=delivery_option,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
    )
    db.add(order)
    await db.flush()
    
    for entry in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=entry["product"].id,
            product_name=entry["product"].name,
            price=entry["product"].price,
            quantity=entry["quantity"],
        ) 
        db.add(order_item)
    await db.commit()
    request.session["cart"] = {}
    return RedirectResponse(url=f"/order-confirmation/{order.order_number}",  status_code=303)


@router.get("/order-confirmation/{order_nnumber}")
async def order_confirmation(order_number: str, request: Request, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.order_number == order_number)
    ) 
    order = result.scalar_one_or_none()
    
    if not order:
        return templates.TemplateResponse(request=request, name="404.html", context={} ,status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="order_confirmation.html",
        context={"order":order}
    )