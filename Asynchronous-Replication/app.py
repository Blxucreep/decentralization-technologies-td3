from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/db_ecommerce'
db = SQLAlchemy(app)
port = 3001

# Modèle de données pour les produits
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    inStock = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

# Lecture des données à partir du fichier JSON et ajout à la base de données PostgreSQL
def initialize_database():
    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/products.json', 'r', encoding='utf-8') as file:
       products_data = json.load(file)['products']

    for product_data in products_data:
        new_product = Product(
            name=product_data['name'],
            category=product_data['category'],
            inStock=product_data['inStock'],
            price=product_data['price']
        )
        db.session.add(new_product)
    db.session.commit()

# Lecture des produits à partir de la base de données
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_json = [{"id": product.id, "name": product.name, "category": product.category, "inStock": product.inStock, "price": product.price} for product in products]
    return jsonify(products_json)

# Ajout d'un produit à la base de données
@app.route('/products', methods=['POST'])
def add_product():
    product_data = request.json

    try:
        new_product = Product(
            name=product_data['name'],
            category=product_data['category'],
            inStock=product_data['inStock'],
            price=product_data['price']
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Mise à jour d'un produit dans la base de données
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product_data = request.json
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    try:
        product.name = product_data['name']
        product.category = product_data['category']
        product.inStock = product_data['inStock']
        product.price = product_data['price']
        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Suppression d'un produit de la base de données
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    initialize_database()  # Initialiser la base de données avec les données du fichier JSON
    app.run(debug=True, port=port)
