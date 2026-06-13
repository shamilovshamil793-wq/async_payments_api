# Async Payments API

Асинхронное REST API на Sanic + PostgreSQL.  
JWT‑авторизация, роли пользователя и администратора, вебхук пополнения баланса с SHA256 подписью.

## Технологии

- Python 3.12
- Sanic
- PostgreSQL
- SQLAlchemy (async)
- JWT
- Docker / Docker Compose

## Запуск

```bash
git clone https://github.com/shamilovshamil793-wq/async_payments_api.git
cd async_payments_api

docker-compose up -d
pip install -r requirements.txt
python -m app.main
