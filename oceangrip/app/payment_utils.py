import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount_in_rupees: float, receipt_id: str):
    amount_in_paise = int(amount_in_rupees * 100)

    order = razorpay_client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": receipt_id,
        "payment_capture": 1,  # auto-capture payment once authorized
    })
    return order


def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False