from sanic import json
from sqlalchemy import select
from app.models import Account, Payment
from app.utils import verify_signature, generate_signature
from decimal import Decimal
import uuid

async def payment_webhook(request):
    data = request.json
    
    # Проверяем подпись
    if not verify_signature(data.copy()):
        return json({"error": "Invalid signature"}, status=400)
    
    transaction_id = data.get("transaction_id")
    account_id = data.get("account_id")
    user_id = data.get("user_id")
    amount = Decimal(str(data.get("amount")))
    
    async with request.app.ctx.session() as session:
        # Проверяем уникальность транзакции
        existing = await session.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )
        if existing.scalar_one_or_none():
            return json({"error": "Transaction already processed"}, status=400)
        
        # Проверяем существование счёта, если нет — создаём
        account_result = await session.execute(
            select(Account).where(Account.id == account_id, Account.user_id == user_id)
        )
        account = account_result.scalar_one_or_none()
        
        if not account:
            # Создаём новый счёт для пользователя
            account = Account(id=account_id, user_id=user_id, balance=0)
            session.add(account)
            await session.commit()
        
        # Начисляем сумму
        account.balance += amount
        
        # Сохраняем транзакцию
        payment = Payment(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
            signature=data.get("signature"),
            processed=True
        )
        session.add(payment)
        await session.commit()
        
        return json({"status": "success", "new_balance": float(account.balance)})
