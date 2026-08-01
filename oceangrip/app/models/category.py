from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100),  unique=True, nullable=True)
    slug = Column( String(100), unique=True,  nullable=True)
    # Here slug is an url-friendly version of name, using for clean url's like fishing-rod.
    
    products = relationship("Product", back_populates="category")