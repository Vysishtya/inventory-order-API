from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update
from pydantic import BaseModel,Field

from database import get_db
from models import Inventory, Order

router = APIRouter(tags=["orders"])

class OrderCreate(BaseModel):
    user_id:int
    product_id:int
    store_id:int
    quantity:int = Field(gt=0)

@router.post("/orders")
def place_order(order:OrderCreate, db:Session = Depends(get_db)):
    inventory_item = db.query(Inventory).filter(
        Inventory.product_id == order.product_id,
        Inventory.store_id == order.store_id
    ).first()

    if not inventory_item:
        raise HTTPException(status_code = 404,detail = "product not available at the store")

    result = db.execute(
        update(Inventory)
        .where(
            Inventory.id == inventory_item.id,
            Inventory.quantity >= order.quantity

        )
        .values(quantity=Inventory.quantity - order.quantity)   
    )

    if result.rowcount == 0:
        raise HTTPException(status_code = 409,detail = "Not enough stock available")

    new_order = Order(
        user_id = order.user_id,
        product_id = order.product_id,
        store_id = order.store_id,
        quantity = order.quantity,
        status = "placed"

    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/orders/{order_id}")
def get_order(order_id:int,db:Session=Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code = 404,detail = "Order not found")
    return{
        "id": order.id,
        "user_id":order.user_id,
        "product_id":order.product_id,
        "store_id":order.store_id,
        "quantity":order.quantity,
        "status":order.status,
        "created_at":order.created_at
    }