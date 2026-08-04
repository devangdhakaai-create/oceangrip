from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    
    id = Column(Integer, primary_key=True,index=True)
    user_id=Column( Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    added_at =Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")
    product = relationship("Product")