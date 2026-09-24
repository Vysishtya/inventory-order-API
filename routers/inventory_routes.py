from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database import get_db
from models import Store, Product, Inventory
from datetime import datetime,timedelta
from models import Order

router = APIRouter(tags=["inventory"])

class StoreCreate(BaseModel):
    name:str
    location:str
class ProductCreate(BaseModel):
    name:str
    price: float   

class InventoryCreate(BaseModel):
    product_id:int
    store_id: int
    quantity: int = Field(gt=0)

@router.post("/stores")
def create_store(store: StoreCreate,db:Session = Depends(get_db)):
    new_store = Store(name=store.name, location=store.location)
    db.add(new_store) 
    db.commit()
    db.refresh(new_store)
    return new_store

@router.get("/stores")
def list_stores(db:Session=Depends(get_db)):
    return db.query(Store).all()

@router.post("/products")
def create_product(product: ProductCreate, db:Session=Depends(get_db)):
    new_product = Product(name=product.name,price=product.price)
    db.add(new_product) 
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/products")
def list_products(db:Session = Depends(get_db)):
    return db.query(Product).all()

@router.post("/inventory")
def add_inventory(item: InventoryCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    store = db.query(Store).filter(Store.id == item.store_id).first()
    if not product or not store:
        raise HTTPException(status_code=404,detail="product or store not found")
    
    new_inventory = Inventory(
        product_id = item.product_id,
        store_id = item.store_id,
        quantity = item.quantity
    )  
    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)
    return new_inventory

@router.get("/inventory/{store_id}")
def get_store_inventory(store_id:int,db:Session = Depends(get_db)):
    items = db.query(Inventory).filter(Inventory.store_id == store_id).all()
    if not items:
        raise HTTPException(status_code = 404, detail = "No inventory found for this store")
    return items  

@router.get("/inventory/{store_id}/forecast")
def forecast_restock(store_id: int,days_lookback: int = 7,db: Session = Depends(get_db)):
    inventory_items = db.query(Inventory).filter(Inventory.store_id).all()
    if not inventory_items:
        raise HTTPException(status_code=404,detail = "No inventory found for this store")

    since_date = datetime.utcnow() - timedelta(days =days_lookback)
    forecast_results = []

    for item in inventory_items:
        recent_orders = db.query(Order).filter(
            Order.store_id == store_id,
            Order.product_id == item.product_id,
            Order.created_at>= since_date
        ).all()

        total_ordered = sum(o.quantity for o in recent_orders)
        avg_daily_orders = total_ordered/days_lookback if days_lookback>0 else 0  

        if avg_daily_orders>0:
            estimated_days_left = round(item.quantity/avg_daily_orders,1)
        else:
            estimated_days_left = None

        needs_restock = estimated_days_left is not None and estimated_days_left<2

        forecast_results.append({
            "product_id":item.product_id,
            "current_stock":item.quantity,
            "avg_daily_orders":round(avg_daily_orders,2),
            "estimated_days_left":estimated_days_left,
            "needs_restock_soon":needs_restock
        })

    return forecast_results    
