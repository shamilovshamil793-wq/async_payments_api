from sanic import json
from sqlalchemy import select
from app.models import User, Account, Payment
from app.auth import hash_password, verify_password, generate_token, protected

async def register_user(request):
    data = request.json
    email = data.get("email")
    full_name = data.get("full_name")
    password = data.get("password")
    
    if not all([email, full_name, password]):
        return json({"error": "Missing fields"}, status=400)
    
    async with request.app.ctx.session() as session:
        existing = await session.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            return json({"error": "Email already exists"}, status=400)
        
        hashed = hash_password(password)
        new_user = User(email=email, full_name=full_name, hashed_password=hashed)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        new_account = Account(user_id=new_user.id, balance=0)
        session.add(new_account)
        await session.commit()
        
        token = generate_token(new_user.id, new_user.email, is_admin=False)
        return json({"token": token, "user": {"id": new_user.id, "email": new_user.email, "full_name": new_user.full_name}})

async def login_user(request):
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not all([email, password]):
        return json({"error": "Missing email or password"}, status=400)
    
    async with request.app.ctx.session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            return json({"error": "Invalid credentials"}, status=401)
        
        token = generate_token(user.id, user.email, is_admin=user.is_admin)
        return json({"token": token, "user": {"id": user.id, "email": user.email, "full_name": user.full_name}})

@protected()
async def get_me(request):
    user_id = request.ctx.user["user_id"]
    async with request.app.ctx.session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return json({"error": "User not found"}, status=404)
        return json({"id": user.id, "email": user.email, "full_name": user.full_name})

@protected()
async def get_my_accounts(request):
    user_id = request.ctx.user["user_id"]
    async with request.app.ctx.session() as session:
        result = await session.execute(select(Account).where(Account.user_id == user_id))
        accounts = result.scalars().all()
        return json([{"id": a.id, "balance": float(a.balance)} for a in accounts])

@protected()
async def get_my_payments(request):
    user_id = request.ctx.user["user_id"]
    async with request.app.ctx.session() as session:
        result = await session.execute(select(Payment).where(Payment.user_id == user_id))
        payments = result.scalars().all()
        return json([{"id": p.id, "transaction_id": p.transaction_id, "amount": float(p.amount), "processed": p.processed} for p in payments])
