from flask import Flask, jsonify, request, render_template
import json

app = Flask(__name__)
port = 3001  

@app.route('/')
def index():
    message = "Bienvenue sur notre site !"
    return render_template('index.html', message=message)

'''@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/getServer', methods=['GET'])
def get_server():
    return jsonify(code=200, server=f"localhost:{port}")'''

with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/products.json', 'r', encoding='utf-8') as file:
    products = json.load(file)['products']


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
    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/products.json', 'w', encoding='utf-8') as file:
        json.dump({"products": products}, file, indent=4)

    return jsonify({"message": "Product added successfully"}), 201


#curl -X POST http://127.0.0.1:3001/products -H "Content-Type: application/json" -d "{\"name\": \"Produit D\", \"category\": \"Catégorie 2\", \"inStock\": true, \"price\": 12.99}"



@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product_data = request.get_json()
    product = next((product for product in products if product['id'] == id), None)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404

    if 'name' in product_data:
        product['name'] = product_data['name']
    if 'category' in product_data:
        product['category'] = product_data['category']
    if 'inStock' in product_data:
        product['inStock'] = product_data['inStock']
    if 'price' in product_data:
        product['price'] = product_data['price']

    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/products.json', 'w', encoding='utf-8') as file:
        json.dump({"products": products}, file, indent=4)

    return jsonify(product), 200

#curl -X PUT http://127.0.0.1:3001/products/7 -H "Content-Type: application/json" -d "{\"price\": 11.99}"

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    global products  # Nécessaire pour modifier la liste au niveau global
    product = next((product for product in products if product['id'] == id), None)
    
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    products = [product for product in products if product['id'] != id]
    
    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/products.json', 'w', encoding='utf-8') as file:
        json.dump({"products": products}, file, indent=4)
    
    return jsonify({"message": "Product deleted successfully"}), 200

#curl -X DELETE http://127.0.0.1:3001/products/7


try:
    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/orders.json', 'r', encoding='utf-8') as file:
        orders_data = json.load(file)
    orders = orders_data["orders"] 
except FileNotFoundError:
    orders = []


@app.route('/orders', methods=['POST'])
def create_order():
    global orders

    order_data = request.json
    total_price = 0

    try:
        user_id = int(order_data.get('userId'))
    except ValueError:
        return jsonify({"error": "Invalid user ID format"}), 400

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
        'userId': user_id 
    }
    orders.append(new_order)

    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/orders.json', 'w', encoding='utf-8') as file:
        json.dump({"orders": orders}, file, indent=4)  


    return jsonify({"message": "Order created successfully"}), 201



#curl -X POST http://127.0.0.1:3001/orders -H "Content-Type: application/json" -d "{\"userId\": 123, \"products\": [{\"id\": 1, \"quantity\": 2}, {\"id\": 2, \"quantity\": 1}]}"


@app.route('/orders/<int:userId>', methods=['GET'])
def get_orders_by_user(userId):
    user_orders = [order for order in orders if order['userId'] == userId]
    if not user_orders:
        return jsonify({"error": "No orders found for user"}), 404
    return jsonify(user_orders), 200


#curl -X GET "http://127.0.0.1:3001/orders/123"


try:
    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/carts.json', 'r', encoding='utf-8') as file:
        carts = json.load(file)
except FileNotFoundError:
    carts = {}

@app.route('/cart/<userId>', methods=['POST'])
def add_to_cart(userId):
    cart_data = request.get_json()
    product_id = int(cart_data.get('productId'))  
    quantity = int(cart_data.get('quantity', 1))  
    
    # Convertir userId en chaîne pour une utilisation comme clé de dictionnaire
    userId_str = str(userId)

    if userId_str not in carts:
        carts[userId_str] = []

    found = False
    for item in carts[userId_str]:
        if item['productId'] == product_id:
            item['quantity'] += quantity
            found = True
            break

    if not found:
        carts[userId_str].append({'productId': product_id, 'quantity': quantity})

    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/carts.json', 'w', encoding='utf-8') as file:
        json.dump(carts, file, indent=4)

    return jsonify({"message": "Product added to cart successfully"}), 201


#curl -X POST http://127.0.0.1:3001/cart/123 -H "Content-Type: application/json" -d '{"productId": 3, "quantity": 5}'



@app.route('/cart/<userId>', methods=['GET'])
def get_cart(userId):
    userId_str = str(userId) 
    if userId_str not in carts:
        return jsonify({'error': 'User has no cart'}), 404

    return jsonify({'cart': carts[userId_str]}), 200


#curl -X GET http://127.0.0.1:3001/cart/123

@app.route('/cart/<userId>/item/<productId>', methods=['DELETE'])
def remove_from_cart(userId, productId):
    userId_str = str(userId) 
    if userId_str not in carts:
        return jsonify({'error': 'User has no cart'}), 404

    product_index = next((i for i, item in enumerate(carts[userId_str]) if item['productId'] == int(productId)), None)
    if product_index is None:
        return jsonify({'error': 'Product not found in user\'s cart'}), 404

    del carts[userId_str][product_index]

    with open('C:/Users/joshu/OneDrive/Documents/ESILV/A4_S8/Decentralization_Technologies/td3anouk2/TP3/TP3/Basic_Implementation/carts.json', 'w', encoding='utf-8') as file:
        json.dump(carts, file, indent=4)

    return jsonify({"message": "Product deleted successfully"}), 200


#curl -X DELETE http://127.0.0.1:3001/cart/123/item/3


if __name__ == '__main__':
    app.run(debug=True, port=port)


