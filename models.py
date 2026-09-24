from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique=True, index = True,nullable = False)
    hashed_password = Column(String,nullable = False)

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer,primary_key=True,index = True)
    name = Column(String, nullable = False)
    location = Column(String, nullable=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name= Column(String,nullable = False)
    price = Column(String,nullable = False)

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    product = relationship("Product")
    store = relationship("Store")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer,primary_key=True,index = True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable = False)
    store_id = Column(Integer,ForeignKey("stores.id"),nullable = False)
    product_id = Column(Integer,ForeignKey("products.id"),nullable = False)
    quantity = Column(Integer,nullable = False)
    status = Column(String,default="placed")
    created_at = Column(DateTime,default=datetime.utcnow)

    user = relationship("User")
    product = relationship("Product")
    store = relationship("Store")