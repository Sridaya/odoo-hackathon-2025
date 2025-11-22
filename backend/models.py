# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Warehouse
class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=0)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), default=1)

# Receipt (Incoming)
class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# Delivery (Outgoing)
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# Internal Transfer
class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    from_warehouse = db.Column(db.Integer, db.ForeignKey('warehouse.id'))
    to_warehouse = db.Column(db.Integer, db.ForeignKey('warehouse.id'))
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)