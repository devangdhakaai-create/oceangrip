from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number= Column(String(20), unique=True,  nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)   # nullable for guest checkout
    user = relationship("User", back_populates="orders")
    
    full_name= Column(String(150), nullable=False)
    email= Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(300), nullable=False)
    city = Column(String(100), nullable=False)
    pincode= Column(String(10), nullable=False)
    delivery_option = Column(String(50),  default="Standard")
    
    subtotal= Column(Float, nullable=False)
    shipping = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    created_at= Column(DateTime(timezone=True), server_default=func.now())
    items = relationship("OrderItem", back_populates="order")
    
    
class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id= Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    
    product_name= Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    quantity= Column(Integer, nullable=False)
    
    order = relationship("Order", back_populates="items")