from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import json
import threading
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/db_ecommerce'
db = SQLAlchemy(app)
port = 3001

# Modèle de données pour les produits dans PostgreSQL
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    inStock = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

# Lecture des produits depuis la base de données JSON
def read_json_products():
    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/tp3loevan/decentralization-technologies-td3/Asynchronous-Replication/products.json', 'r', encoding='utf-8') as file:
        products_data = json.load(file)['products']
    return products_data

# Initialisation de la base de données PostgreSQL
def initialize_database():
    with app.app_context():
        if not Product.query.first():  # Vérifier si la base de données est vide
            db.create_all()
            products_data = read_json_products()
            for product_data in products_data:
                new_product = Product(
                    name=product_data['name'],
                    category=product_data['category'],
                    inStock=bool(product_data['inStock']),  # Convertir en booléen
                    price=product_data['price']
                )
                db.session.add(new_product)
            db.session.commit()

# Réplication asynchrone des données depuis la base de données JSON vers PostgreSQL
def replicate_json_to_postgres():
    while True:
        try:
            products_data = read_json_products()
            with app.app_context():
                for product_data in products_data:
                    product = Product.query.filter_by(id=product_data['id']).first()
                    if not product:
                        new_product = Product(
                            id=product_data['id'],
                            name=product_data['name'],
                            category=product_data['category'],
                            inStock=product_data['inStock'],
                            price=product_data['price']
                        )
                        db.session.add(new_product)
                    else:
                        product.name = product_data['name']
                        product.category = product_data['category']
                        product.inStock = product_data['inStock']
                        product.price = product_data['price']
                db.session.commit()
            print("Replication successful")
        except SQLAlchemyError as e:
            print(f"Replication error: {e}")
        time.sleep(60)  # Réplication toutes les 60 secondes

# Démarrage de la réplication asynchrone dans un thread
replication_thread = threading.Thread(target=replicate_json_to_postgres)
replication_thread.start()

@app.route('/')
def index():
    message = "Bienvenue sur notre site !"
    return render_template('index.html', message=message)

# Lecture des produits depuis la base de données PostgreSQL
@app.route('/products', methods=['GET'])
def get_products():
    with app.app_context():
        products = Product.query.all()
        products_data = [{'id': product.id, 'name': product.name, 'category': product.category, 'inStock': product.inStock, 'price': product.price} for product in products]
    return jsonify(products_data)

# Ajout d'un produit dans la base de données JSON
@app.route('/products', methods=['POST'])
def add_product():
    product_data = request.json
    with app.app_context():
        new_product = Product(
            name=product_data['name'],
            category=product_data['category'],
            inStock=product_data['inStock'],
            price=product_data['price']
        )
        db.session.add(new_product)
        db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

# Mise à jour d'un produit dans la base de données JSON
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product_data = request.json
    with app.app_context():
        product = Product.query.get(id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        product.name = product_data.get('name', product.name)
        product.category = product_data.get('category', product.category)
        product.inStock = product_data.get('inStock', product.inStock)
        product.price = product_data.get('price', product.price)

        db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200

# Suppression d'un produit de la base de données JSON
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    with app.app_context():
        product = Product.query.get(id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        db.session.delete(product)
        db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200

if __name__ == '__main__':
    initialize_database()  # Initialiser la base de données avec les données du fichier JSON
    app.run(debug=True, port=port)
