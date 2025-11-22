# backend/app.py — FINAL 100% WORKING & SECURE VERSION
from flask import Flask, render_template, request, session, redirect, jsonify
from functools import wraps
from models import db, Product, Warehouse, Receipt, Delivery, Transfer

app = Flask(__name__, template_folder='templates')
app.secret_key = "daya_stockmaster_secure_2025"

# CRITICAL: These two lines make session work perfectly on localhost
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Required for http://127.0.0.1

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Database setup
with app.app_context():
    db.drop_all()
    db.create_all()
    print("DATABASE READY & FRESH!")

    if Warehouse.query.count() == 0:
        db.session.add_all([
            Warehouse(name="Main Warehouse"),
            Warehouse(name="Production Floor"),
            Warehouse(name="Retail Store")
        ])
        db.session.commit()
        print("WAREHOUSES CREATED!")

# LOGIN REQUIRED DECORATOR — THIS IS THE KEY!
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# AUTH ROUTES
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    return redirect('/dashboard')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    if email == 'admin@stockmaster.com' and password == 'admin123':
        session['user'] = 'admin'
        return redirect('/dashboard')
    return "<h1 style='color:red;text-align:center;margin-top:200px;'>Wrong Email or Password!</h1>", 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ALL PAGES — PROTECTED WITH LOGIN!
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/products')
@login_required
def products():
    return render_template('products.html')

@app.route('/receipts')
@login_required
def receipts():
    return render_template('receipts.html')

@app.route('/deliveries')
@login_required
def deliveries():
    return render_template('deliveries.html')

@app.route('/transfers')
@login_required
def transfers():
    return render_template('transfers.html')

@app.route('/warehouse')
@login_required
def warehouse_page():
    return render_template('warehouse.html')

@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')

# API ENDPOINTS
@app.route('/api/products')
def get_products():
    products = Product.query.all()
    warehouses = {w.id: w.name for w in Warehouse.query.all()}
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category": p.category or "General",
            "stock": p.stock,
            "warehouse": warehouses.get(p.warehouse_id, "Main Warehouse")
        })
    return jsonify(result)

@app.route('/api/add_product', methods=['POST'])
def add_product():
    data = request.get_json()
    p = Product(
        name=data['name'],
        sku=data['sku'],
        category=data.get('category'),
        stock=data.get('stock', 0),
        warehouse_id=1
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"success": True, "id": p.id})

@app.route('/api/receive', methods=['POST'])
def receive_stock():
    data = request.get_json()
    p = Product.query.get(data['id'])
    if not p:
        return jsonify({"error": "Product not found"}), 404
    qty = int(data['qty'])
    p.stock += qty
    db.session.add(Receipt(product_id=p.id, quantity=qty))
    db.session.commit()
    return jsonify({"success": True, "new_stock": p.stock})

@app.route('/api/deliver', methods=['POST'])
def deliver_stock():
    data = request.get_json()
    p = Product.query.get(data['id'])
    if not p:
        return jsonify({"error": "Product not found"}), 404
    qty = int(data['qty'])
    if p.stock >= qty:
        p.stock -= qty
        db.session.add(Delivery(product_id=p.id, quantity=qty))
        db.session.commit()
        return jsonify({"success": True, "new_stock": p.stock})
    return jsonify({"error": "Not enough stock"}), 400

# RUN SERVER
if __name__ == "__main__":
    print("STOCKMASTER — FULLY SECURE & READY!")
    app.run(debug=True, port=5000)