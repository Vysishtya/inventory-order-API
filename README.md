# Inventory & Order API

A backend system for per-store inventory tracking and order placement, 
built to solve a real problem: preventing overselling when multiple 
customers order the last unit of a product at the same time.

## The core problem this solves

In quick-commerce systems, stock is limited and demand is high. If two 
customers order the last item simultaneously, a naive implementation 
lets both orders succeed — overselling the item. This project solves 
that with an atomic database update, and proves it works under real 
concurrent load.

## Proof: concurrency test

50 simultaneous order requests were fired at a product with exactly 
1 unit in stock:

Total requests: 50
Successful orders (200): 1
Rejected orders (non-200): 49
Status code breakdown: {200: 1, 409: 49}

Result: exactly 1 order succeeded, 49 were cleanly rejected with 
409 Conflict, and final stock was 0 — never negative.

## Features

- JWT-based authentication (signup/login)
- Per-store inventory (not global stock)
- Atomic order placement — race-condition safe
- Restock forecasting based on recent order velocity

## Tech stack

FastAPI, SQLAlchemy, SQLite, JWT (python-jose), bcrypt (passlib)

## How the concurrency fix works

Instead of checking stock and decrementing it as two separate steps 
(which creates a race condition), this uses a single atomic SQL 
UPDATE with a WHERE clause:

UPDATE inventory SET quantity = quantity - X WHERE id = ? AND quantity >= X

If two requests race for the last item, the database processes them 
one at a time — only one UPDATE actually affects a row. The order is 
only created if the update succeeds.

## API Endpoints

- POST /auth/signup, POST /auth/login
- POST /stores, GET /stores
- POST /products, GET /products
- POST /inventory, GET /inventory/{store_id}
- POST /orders, GET /orders/{order_id}
- GET /inventory/{store_id}/forecast

## Running locally

1. python -m venv venv
2. venv\Scripts\activate  (Windows)
3. pip install -r requirements.txt
4. uvicorn main:app --reload
5. Visit http://127.0.0.1:8000/docs