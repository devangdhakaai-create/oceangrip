from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

class  Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30),unique=True, nullable=False)
    discount_percent= Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    