from flask import Flask, jsonify, request, render_template
import json

app = Flask(__name__)
port = 3001  

@app.route('/')
def index():
    # Vous pouvez inclure des données dynamiques ici
    message = "Bienvenue sur notre site !"
    return render_template('index.html', message=message)

'''@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/getServer', methods=['GET'])
def get_server():
    return jsonify(code=200, server=f"localhost:{port}")'''

with open('products.json', 'r', encoding='utf-8') as file:
    products = json.load(file)['products']

@app.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    inStock = request.args.get('inStock')
    
    filtered_products = products
    
    # Filtre par catégorie
    if category:
        try:
            category = int(category)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid product ID"}), 400 #erreur si la catégorie ne peut être convertit en entier 
        #à modifier en fonction des valeurs qu'on donnera à category
        filtered_products = [product for product in filtered_products if product['category'] == category]
    
    # Filtre par disponibilité en stock
    if inStock is not None:
        inStock = inStock.lower() in ['true', '1', 'yes']
        filtered_products = [product for product in filtered_products if product['inStock'] == inStock]
    
    return jsonify(filtered_products)

#curl -X GET "http://127.0.0.1:3001/products"
#curl -X GET "http://127.0.0.1:3001/products?inStock=True"
#curl -X GET "http://127.0.0.1:3001/products?category=1"
#curl -X GET "http://127.0.0.1:3001/products?category=1&inStock=True"


@app.route('/products/<int:id>', methods=['GET'])
def get_products_by_id(id):

    filtered_products = [product for product in products if product['id'] == id]

    if filtered_products:
        return jsonify(filtered_products[0])
    else:
        return jsonify({"error": "Product not found"}), 404

#curl -X GET "http://127.0.0.1:3001/products/1"


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

    # Sauvegarder dans products.json
    with open('products.json', 'w', encoding='utf-8') as file:
        json.dump({"products": products}, file, indent=4)

    return jsonify({"message": "Product added successfully"}), 201


#curl -X POST http://127.0.0.1:3001/products -H "Content-Type: application/json" -d "{\"name\": \"Produit D\", \"category\": \"Catégorie 2\", \"inStock\": true, \"price\": 12.99}"



@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product_data = request.json
    product = next((product for product in products if product['id'] == id), None)
    
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    product_keys = product.keys()
    for key in product_data.keys():
        if key in product_keys:
            product[key] = product_data[key]

    return jsonify(product), 200

#curl -X PUT http://127.0.0.1:3001/products/4 -H "Content-Type: application/json" -d "{\"price\": 11.99}"

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    global products  # Nécessaire pour modifier la liste au niveau global
    product = next((product for product in products if product['id'] == id), None)
    
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    products = [product for product in products if product['id'] != id]
    
    with open('products.json', 'w', encoding='utf-8') as file:
        json.dump({"products": products}, file, indent=4)
    
    return jsonify({"message": "Product deleted successfully"}), 200

#curl -X DELETE http://127.0.0.1:3001/products/4



try:
    with open('orders.json', 'r', encoding='utf-8') as file:
        orders = json.load(file)
except FileNotFoundError:
    orders = []


@app.route('/orders', methods=['POST'])
def create_order():
    global orders

    order_data = request.json
    total_price = 0
    
    # Calculer le total_price basé sur les produits commandés
    for item in order_data['products']:
        product = next((product for product in products if product['id'] == item['id']), None)
        if product:
            total_price += product['price'] * item['quantity']
    
    # Déterminer le prochain orderId
    if orders:
        order_id_counter = max(order['orderId'] for order in orders) + 1
    else:
        order_id_counter = 1

    new_order = {
        'orderId': order_id_counter,
        'products': order_data['products'],
        'totalPrice': total_price,
        'status': 'Placed',
        'userId': order_data.get('userId', 'Anonymous')
    }
    orders.append(new_order)
    
    # Sauvegarder dans orders.json
    with open('orders.json', 'w', encoding='utf-8') as file:
        json.dump(orders, file, indent=4)

    return jsonify({"message": "Order created successfully"}), 201


#curl -X POST http://127.0.0.1:3001/orders -H "Content-Type: application/json" -d "{\"products\": [{\"id\": 1, \"quantity\": 2}, {\"id\": 2, \"quantity\": 1}], \"userId\": \"123456\"}"


@app.route('/orders/<userId>', methods=['GET'])
def get_orders_by_user(userId):
    # Convertir userId en entier si nécessaire
    try:
        user_id_int = int(userId)
        user_orders = [order for order in orders if order['userId'] == user_id_int]
    except ValueError:
        # Si la conversion échoue, cela signifie que userId n'est pas un entier valide
        return jsonify({"error": "Invalid user ID format"}), 400

    return jsonify(user_orders), 200 if user_orders else 404


#curl -X GET "http://127.0.0.1:3001/orders/123456"




try:
    with open('carts.json', 'r', encoding='utf-8') as file:
        carts = json.load(file)
except FileNotFoundError:
    carts = {}


@app.route('/cart/<userId>', methods=['POST'])
def add_to_cart(userId):
    cart_data = request.get_json()
    product_id = cart_data.get('productId')  # Renommer 'products' en 'productId'
    quantity = cart_data.get('quantity')

    # Vérifier si l'utilisateur a déjà un panier
    if userId not in carts:
        carts[userId] = []

    # Ajouter le produit au panier de l'utilisateur
    carts[userId].append({'productId': product_id, 'quantity': quantity})

    # Sauvegarder dans carts.json
    with open('carts.json', 'w', encoding='utf-8') as file:
        json.dump(carts, file, indent=4)

    return jsonify({"message": "Producted added to cart successfully"}), 201       
        

#curl -X POST http://127.0.0.1:3001/cart/123456 -H "Content-Type: application/json" -d '{"productId": 3, "quantity": 5}'

@app.route('/cart/<userId>', methods=['GET'])
def get_cart(userId):
    # Vérifier si l'utilisateur a un panier
    if userId not in carts:
        return jsonify({'error': 'User has no cart'}), 404

    # Renvoyer le contenu du panier de l'utilisateur en réponse
    return jsonify({'cart': carts[userId]}), 200

#curl -X GET http://127.0.0.1:3001/cart/123456 

@app.route('/cart/<userId>/item/<productId>', methods=['DELETE'])
def remove_from_cart(userId, productId):
    # Vérifier si l'utilisateur a un panier
    if userId not in carts:
        return jsonify({'error': 'User has no cart'}), 404

    # Recherchez l'index du produit dans le panier de l'utilisateur
    product_index = next((i for i, item in enumerate(carts[userId]) if item['productId'] == int(productId)), None)

    # Vérifier si le produit est présent dans le panier de l'utilisateur
    if product_index is None:
        return jsonify({'error': 'Product not found in user\'s cart'}), 404

    # Supprimer le produit du panier de l'utilisateur
    del carts[userId][product_index]
    
    # Sauvegarder dans carts.json
    with open('carts.json', 'w', encoding='utf-8') as file:
        json.dump(carts, file, indent=4)

    # Renvoyer le contenu mis à jour du panier en réponse
    return jsonify({"message": "Product deleted successfully"}), 200

#curl -X DELETE http://127.0.0.1:3001/cart/123456/item/1


if __name__ == '__main__':
    app.run(debug=True, port=port)


