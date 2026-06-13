import os
from sanic import Sanic, json
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import Base
from app.handlers.user import register_user, login_user, get_me, get_my_accounts, get_my_payments
from app.handlers.admin import get_users, create_user, update_user, delete_user

load_dotenv()

app = Sanic("PaymentsAPI")

# Настройка БД
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "payments_db")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

@app.before_server_start
async def setup_db(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.ctx.session = async_session

@app.after_server_stop
async def shutdown_db(app):
    await engine.dispose()

@app.get("/health", name="health_check")
async def health_check(request):
    return json({"status": "ok", "message": "Server is running"})

# Пользовательские роуты
app.post("/register", name="register")(register_user)
app.post("/login", name="login")(login_user)
app.get("/me", name="get_me")(get_me)
app.get("/me/accounts", name="get_my_accounts")(get_my_accounts)
app.get("/me/payments", name="get_my_payments")(get_my_payments)

# Административные роуты
app.get("/admin/users", name="get_users")(get_users)
app.post("/admin/users", name="create_user")(create_user)
app.put("/admin/users/<user_id:int>", name="update_user")(update_user)
app.delete("/admin/users/<user_id:int>", name="delete_user")(delete_user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

# Вебхук для платежей
from app.handlers.webhook import payment_webhook

app.post("/webhook/payment", name="payment_webhook")(payment_webhook)
