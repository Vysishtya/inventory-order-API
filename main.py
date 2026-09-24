from fastapi import FastAPI
from database import Base, engine
import models
from routers import auth_routes,inventory_routes
from routers import auth_routes, inventory_routes, order_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory API")

app.include_router(auth_routes.router)
app.include_router(inventory_routes.router)

app.include_router(order_routes.router)

@app.get("/")
def read_root():
    return{"message":"API is running"}