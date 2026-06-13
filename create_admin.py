import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import User

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/payments_db"

async def create_admin():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Проверяем, есть ли уже админ
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        admin = result.scalar_one_or_none()
        
        if admin:
            print("Admin already exists")
            return
        
        # Создаём админа
        hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        new_admin = User(
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=hashed,
            is_admin=True
        )
        session.add(new_admin)
        await session.commit()
        print("Admin created successfully!")
        print("Email: admin@example.com")
        print("Password: admin123")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin())
