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
from fastapi import BackgroundTasks
from app.email_utils import send_order_confirmation_email
from app.payment_utils import create_razorpay_order, verify_payment_signature, RAZORPAY_KEY_ID
import json
from app.models import Coupon

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
    coupon_code = request.session.get("coupon_code")
    coupon_discount_percent = request.session.get("coupon_discount",0)
    discount_amount = (subtotal *  coupon_discount_percent/100) if coupon_discount_percent else 0
    total = subtotal + shipping - discount_amount
    
    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
            "coupon_code":coupon_code,
            "discount_amount":discount_amount,
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
            items.append({"product": product,"quantity": qty, "item_total":item_total})
            
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

async def initiate_payment(
    request: Request,
    db: AsyncSession = Depends(get_db),
    full_name: str =Form(...),
    email: str = Form(...),
    phone: str= Form(...),
    address:str = Form(...),
    city: str = Form(...),
    pincode: str= Form(...),
    delivery_option: str =Form("Standard"),
):
    cart = request.session.get("cart", {})
    items = []
    subtotal = 0.0

    for product_id_str, qty in cart.items():
        result = await db.execute(select(Product).where(Product.id == int(product_id_str)))
        product = result.scalar_one_or_none()
        if product:
            item_total = product.price * qty
            subtotal += item_total
            items.append({"product_id": product.id, "name": product.name,"price": product.price, "quantity": qty})

    if not items:
        return RedirectResponse(url="/cart", status_code=303)

    shipping = 50.00
    coupon_discount_percent = request.session.get("coupon_discount", 0)
    discount_amount = (subtotal * coupon_discount_percent/ 100) if coupon_discount_percent else 0
    total = subtotal + shipping - discount_amount

    order_number = generate_order_number()
    razorpay_order = create_razorpay_order(total, receipt_id=order_number)

    # pending order details stored in session not in db until payment is verified
    request.session["pending_order"] = {
        "order_number": order_number,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "address": address,
        "city": city,
        "pincode": pincode,
        "delivery_option": delivery_option,
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "razorpay_order_id": razorpay_order["id"],
    }

    return templates.TemplateResponse(
        request=request,
        name="payment.html",
        context={
            "razorpay_key_id": RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order["id"],
            "amount": int(total * 100),
            "full_name": full_name,
            "email": email,
            "phone": phone,
        }
    )
    
@router.post("/checkout/verify")
async def verify_payment(
    request: Request,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None,
    razorpay_payment_id: str = Form(...),
    razorpay_order_id: str = Form(...),
    razorpay_signature: str = Form(...),
):
    pending = request.session.get("pending_order")

    if not pending or pending["razorpay_order_id"] != razorpay_order_id:
        return RedirectResponse(url="/cart", status_code=303)

    is_valid = verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)

    if not is_valid:
        return templates.TemplateResponse(
            request=request,
            name="payment_failed.html",
            context={}
        )        
    order = Order(
        order_number=pending["order_number"],
        user_id=request.session.get("user_id"),
        full_name=pending["full_name"],
        email=pending["email"],
        phone=pending["phone"],
        address=pending["address"],
        city=pending["city"],
        pincode=pending["pincode"],
        delivery_option=pending["delivery_option"],
        subtotal=pending["subtotal"],
        shipping=pending["shipping"],
        total=pending["total"],
    )
    db.add(order)
    await db.flush()

    for entry in pending["items"]:
        order_item = OrderItem(
            order_id=order.id,
            product_id=entry["product_id"],
            product_name=entry["name"],
            price=entry["price"],
            quantity=entry["quantity"],
        )
        db.add(order_item)

    await db.commit()

    request.session["cart"] = {}
    request.session["pending_order"] = None

    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order.id)
    )
    order_with_items = result.scalar_one()

    background_tasks.add_task(send_order_confirmation_email, order_with_items)

    return RedirectResponse(url=f"/order-confirmation/{order.order_number}", status_code=303)


@router.get("/order-confirmation/{order_number}")
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
    
@router.post("/cart/apply-coupon")
async def apply_coupon(request: Request, db: AsyncSession = Depends(get_db), coupon_code: str =Form(...)):
    result = await db.execute(
        select(Coupon).where(Coupon.code == coupon_code.upper(), Coupon.is_active == True)
    )
    coupon = result.scalar_one_or_none()
    if coupon:
        request.session["coupon_code"] = coupon.code
        request.session["coupon_discount"] = coupon.discount_percent
    else:
        request.session["coupon_code"] = None
        request.session["coupon_discount"] = None
    return RedirectResponse(url="/cart", status_code=303)