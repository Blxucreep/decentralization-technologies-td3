from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/db_ecommerce'
db = SQLAlchemy(app)
port = 3001

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    inStock = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/products.json', 'r', encoding='utf-8') as file:
    products = json.load(file)['products']

@app.route('/')
def index():
    message = "Bienvenue sur notre site !"
    return render_template('index.html', message=message)

@app.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    inStock = request.args.get('inStock')
    
    filtered_products = products
    
    # Filtre par catégorie
    if category:
        filtered_products = [product for product in filtered_products if product['category'] == category]
    
    # Filtre par disponibilité en stock
    if inStock is not None:
        inStock = inStock.lower() in ['true', '1', 'yes']
        filtered_products = [product for product in filtered_products if product['inStock'] == inStock]
    
    return jsonify(filtered_products)

@app.route('/products/<int:id>', methods=['GET'])
def get_products_by_id(id):
    filtered_products = [product for product in products if product['id'] == id]

    if filtered_products:
        return jsonify(filtered_products[0])
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/products', methods=['POST'])
def add_product():
    product_data = request.json

    new_id = max([product['id'] for product in products], default=0) + 1

    products.append({
        "id": new_id,
        "name": product_data['name'],
        "category": product_data['category'],
        "inStock": product_data['inStock'],
        "price": product_data['price']
    })

    try:
        inStock = product_data.get('inStock', '').lower() in ['true', '1', 'yes']
        # Créez une instance de la classe Product pour ajouter à la base de données PostgreSQL
        new_product = Product(
            name=product_data['name'],
            category=product_data['category'],
            inStock=inStock,
            price=product_data['price']
        )

        # Ajoutez le nouveau produit à la base de données PostgreSQL
        db.session.add(new_product)
        db.session.commit()

        # Sauvegarder dans products.json
        with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/products.json', 'w', encoding='utf-8') as file:
            json.dump({"products": products}, file, indent=4)

        return jsonify({"message": "Product added successfully"}), 201

    except SQLAlchemyError as e:
        # En cas d'erreur lors de l'ajout du produit à la base de données PostgreSQL
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    global products
    product = next((product for product in products if product['id'] == id), None)
    
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    products = [product for product in products if product['id'] != id]
    
    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/products.json', 'w', encoding='utf-8') as file:
        json.dump({"products": products}, file, indent=4)
    
    try:
        # Supprimer le produit de la base de données PostgreSQL
        Product.query.filter_by(id=id).delete()
        db.session.commit()
        
        return jsonify({"message": "Product deleted successfully"}), 200

    except SQLAlchemyError as e:
        # En cas d'erreur lors de la suppression du produit de la base de données PostgreSQL
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=port)
