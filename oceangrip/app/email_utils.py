import os
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


async def send_order_confirmation_email(order):
    message = EmailMessage()
    message["From"] = GMAIL_ADDRESS
    message["To"] = order.email
    message["Subject"] = f"Order Confirmed - {order.order_number} | OceanGrip"

    items_text = "\n".join(
        f"- {item.product_name} x{item.quantity} - ₹{item.price * item.quantity:.2f}"
        for item in order.items
    )

    body = f"""Hi {order.full_name},

Thank you for your order! Here are your order details:

Order Number: {order.order_number}

Items:
{items_text}

Subtotal: ₹{order.subtotal:.2f}
Shipping: ₹{order.shipping:.2f}
Total: ₹{order.total:.2f}

Shipping to:
{order.address}, {order.city} - {order.pincode}
Delivery: {order.delivery_option}

We'll notify you once your order ships.

Thanks for shopping with OceanGrip!
"""

    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=GMAIL_ADDRESS,
            password=GMAIL_APP_PASSWORD,
        )
    except Exception as e:
        print(f"Email sending failed: {e}")