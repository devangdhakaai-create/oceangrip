# 🎣 OceanGrip

A modern, ocean-themed e-commerce platform built for a fishing gear business. OceanGrip offers a full shopping experience — from browsing products to secure checkout — along with an admin panel for managing the store.

![Status](https://img.shields.io/badge/status-in%20development-blue)
![Python](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)

---

## ✨ Features

- **Product Catalog** — Browse by category, search, filter by price, and sort
- **Shopping Cart** — Add, update, and remove items with live subtotal
- **Coupons** — Apply discount codes at checkout
- **Secure Checkout** — Razorpay payment gateway integration
- **User Accounts** — Register, login, and view order history
- **Wishlist & Recently Viewed** — Personalized shopping experience
- **Order Confirmation Emails** — Automatic email receipts via Gmail SMTP
- **Admin Panel** — Manage products, coupons, and view sales reports
- **Responsive Design** — Works smoothly across desktop, tablet, and mobile

---

## 🛠️ Tech Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Backend        | FastAPI (async)                     |
| Templating     | Jinja2                              |
| Database       | PostgreSQL                          |
| ORM            | SQLAlchemy (async) + asyncpg        |
| Payments       | Razorpay                            |
| Email          | Gmail SMTP (aiosmtplib)             |
| Auth           | Session-based, bcrypt password hashing |

---

## 📁 Project Structure

oceangrip/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Async DB connection setup
│   ├── auth_utils.py        # Password hashing utilities
│   ├── email_utils.py       # Order confirmation email logic
│   ├── payment_utils.py     # Razorpay integration
│   ├── models/               # SQLAlchemy models
│   ├── routes/                # Route handlers (pages, cart, auth, admin)
│   ├── templates/            # Jinja2 HTML templates
│   └── static/css/          # CSS and static assets
├── venv/                      # Virtual environment
├── create_tables.py          # One-time DB table setup script
├── seed_data.py               # Sample data seeder
├── requirements.txt
├── .env                        # Environment variables (not committed)
├── .gitignore
├── .gitattributes
├── LICENSE
└── README.md

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL installed and running

### 1. Clone the repository

```bash
git clone https://github.com/your-username/oceangrip.git
cd oceangrip
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL database

Open pgAdmin (or psql) and create the database:

```sql
CREATE DATABASE oceangrip;
```

### 5. Configure environment variables

Create a `.env` file in the project root:

GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

### 6. Update database credentials

In `app/database.py`, update the `DATABASE_URL` with your PostgreSQL username and password:

```python
DATABASE_URL = "postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/oceangrip"
```

### 7. Create database tables

```bash
python create_tables.py
```

### 8. (Optional) Seed sample data

```bash
python seed_data.py
```

---

## ▶️ Running the App

```bash
cd oceangrip
venv\Scripts\activate
uvicorn app.main:app --reload
```

Then open your browser to:

- **Website:** http://127.0.0.1:8000
- **API Docs:** http://127.0.0.1:8000/docs
- **Admin Panel:** http://127.0.0.1:8000/admin/login

---

## 🔐 Admin Access

The admin panel is protected by a password. Update the `ADMIN_PASSWORD` in `app/routes/admin.py` before deploying to production, and move it to an environment variable for security.

---

## 📌 Notes

- This project is under active development, built incrementally as a portfolio piece.
- Payment gateway is integrated in **Test Mode** — no real transactions occur during development.
- Product images use placeholders until real product photography is available.

---

## 📄 License

This project is built for OceanGrip and is not licensed for public redistribution.

---

**Built with ❤️ by Devang Dhaka**
