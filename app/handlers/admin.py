from sanic import json
from sqlalchemy import select, delete
from app.models import User, Account
from app.auth import hash_password, protected

def admin_required():
    def decorator(f):
        @protected()
        async def decorated(request, *args, **kwargs):
            if not request.ctx.user.get("is_admin"):
                return json({"error": "Admin access required"}, status=403)
            return await f(request, *args, **kwargs)
        return decorated
    return decorator

@admin_required()
async def get_users(request):
    async with request.app.ctx.session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        users_list = []
        for u in users:
            accounts_result = await session.execute(select(Account).where(Account.user_id == u.id))
            accounts = accounts_result.scalars().all()
            users_list.append({
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "accounts": [{"id": a.id, "balance": float(a.balance)} for a in accounts]
            })
        return json(users_list)

@admin_required()
async def create_user(request):
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
        
        return json({"id": new_user.id, "email": new_user.email, "full_name": new_user.full_name})

@admin_required()
async def update_user(request, user_id):
    data = request.json
    async with request.app.ctx.session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return json({"error": "User not found"}, status=404)
        
        if "email" in data:
            user.email = data["email"]
        if "full_name" in data:
            user.full_name = data["full_name"]
        if "password" in data:
            user.hashed_password = hash_password(data["password"])
        
        await session.commit()
        return json({"id": user.id, "email": user.email, "full_name": user.full_name})

@admin_required()
async def delete_user(request, user_id):
    async with request.app.ctx.session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return json({"error": "User not found"}, status=404)
        
        await session.delete(user)
        await session.commit()
        return json({"message": "User deleted"})
