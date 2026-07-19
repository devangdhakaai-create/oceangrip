from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column (Integer, primary_key=True  , index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    stock = Column (Integer, default=0)
    image_url = Column(String(400))
    specifications = Column(Text)
    
    
    category_id = Column(Integer , ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")