import asyncio
from app.database import AsyncSessionLocal
from app.models import Category, Product


async def seed() :
    async with AsyncSessionLocal()  as session:
        # Sample Data for Reference Only
        categories = [
            Category(name="Fishing Rods", slug="fishing-rods"),
            Category(name="Fishing Reels", slug="fishing-reels"),
            Category(name="Fishing Lines", slug="fishing-lines"),
            Category(name="Fishing Hooks", slug="fishing-hooks"),
            Category(name="Fishing Lures", slug="fishing-lures"),
            Category(name="Fishing Nets", slug="fishing-nets"),
            Category(name="Fishing Accessories", slug="fishing-accessories"), 
        ]
        session.add_all(categories)
        await session.commit()
        
        for c in categories:
            await session.refresh(c)
            
        # Sample Products who's general description & details generated using Microsoft Copilot
        products = [
            Product(
                name="Carbon Fiber Fishing Rod",
                slug="carbon-fiber-fishing-rod",
                description="Lightweight, durable carbon fiber rod ideal for freshwater and saltwater fishing.",
                price=1499.00,
                stock=25,
                image_url="https://images.unsplash.com/photo-1587730593720-6be3a9c02aa2",
                specifications="Length: 7ft | Material: Carbon Fiber | Weight: 180g",
                category_id=categories[0].id,
            ),
            
            Product(
                name="Spinning Fishing Reel",
                slug="spinning-fishing-reel",
                description="Smooth spinning reel with 5.2:1 gear ratio, perfect for beginners and pros alike.",
                price=999.00,
                stock=40,
                image_url="https://images.unsplash.com/photo-1516908309489-7c8b93586e5b",
                specifications="Gear Ratio: 5.2:1 | Ball Bearings: 8+1 | Weight: 250g",
                category_id=categories[1].id,
            ),
            
            Product(
                name="Braided Fishing Line 20lb",
                slug="braided-fishing-line-20lb",
                description="High-strength braided line with low stretch and excellent knot strength.",
                price=399.00,
                stock=60,
                image_url="https://images.unsplash.com/photo-1519575706483-221027bfbb31",
                specifications="Length: 150m | Strength: 20lb | Material: PE Braid",
                category_id=categories[2].id,
            ),
        ]
        
        session.add_all(products)
        await session.commit()
        
        print("Seed Data Updated/Inserted Successfully")
        

if __name__ == "__main__":
    asyncio.run(seed())