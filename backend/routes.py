print("ROUTES.PY RELOADED SUCCESSFULLY!")
from flask import request, jsonify
from models import db, Product, Receipt   # Receipt added here

def setup_routes(app):

    # —— Existing routes (keep them) ——
    @app.route('/products', methods=['GET'])
    def get_products():
        products = Product.query.all()
        result = []
        for p in products:
            result.append({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "category": p.category,
                "stock": p.stock
            })
        return jsonify(result)

    @app.route('/products', methods=['POST'])
    def add_product():
        data = request.get_json()
        name = data.get('name')
        sku = data.get('sku')
        category = data.get('category', '')
        stock = data.get('stock', 0)

        if not name or not sku:
            return jsonify({"error": "Name and SKU are required"}), 400

        new_product = Product(name=name, sku=sku, category=category, stock=stock)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 201

    # —— NEW: Receipt Route ——
    @app.route('/api/receipt', methods=['POST'])
    def create_receipt():
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 0)

        if not product_id or quantity <= 0:
            return jsonify({"error": "product_id and positive quantity required"}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Increase stock
        product.stock += quantity

        # Log the receipt
        receipt = Receipt(product_id=product_id, quantity=quantity)
        db.session.add(receipt)
        db.session.commit()

        return jsonify({
            "message": "Receipt created - stock increased!",
            "product": product.name,
            "new_stock": product.stock
        }), 201
    
        # NEW: Delivery Route (Outgoing Stock)
    @app.route('/api/delivery', methods=['POST'])
    def create_delivery():
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 0)

        if not product_id or quantity <= 0:
            return jsonify({"error": "product_id and positive quantity required"}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        if product.stock < quantity:
            return jsonify({"error": "Not enough stock!"}), 400

        # Decrease stock
        product.stock -= quantity

        # You can add Delivery model later — for now just update stock
        db.session.commit()

        return jsonify({
            "message": "Delivery completed - stock reduced!",
            "product": product.name,
            "new_stock": product.stock
        }), 200