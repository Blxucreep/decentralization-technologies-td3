const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Question 1 - Hello World Server
app.get('/', (req, res) => {
  res.send('Hello, World!');
});

// Question 2 - DNS Registry
app.get('/getServer', (req, res) => {
  const serverURL = `localhost:${port}`;
  res.json({ code: 200, server: serverURL });
});

// Question 3 - E-commerce API

// Sample data for products, orders, and cart
let products = [
  { id: 1, name: 'Product A', description: 'Description A', price: 10, category: 'Category A', inStock: 20 },
  { id: 2, name: 'Product B', description: 'Description B', price: 15, category: 'Category B', inStock: 15 },
];

let orders = [];
let cart = {};

// Products Routes

app.get('/products', (req, res) => {
 
  res.json(products);
});

app.get('/products/:id', (req, res) => {
  const productId = parseInt(req.params.id);
  const product = products.find(product => product.id === productId);

  if (!product) {
    res.status(404).json({ error: 'Product not found' });
  } else {
    res.json(product);
  }
});

app.post('/products', (req, res) => {
  const newProduct = req.body;
  newProduct.id = products.length + 1;
  products.push(newProduct);

  res.json(newProduct);
});

app.put('/products/:id', (req, res) => {
  const productId = parseInt(req.params.id);
  const updatedProduct = req.body;

  products = products.map(product => (product.id === productId ? { ...product, ...updatedProduct } : product));

  res.json(products.find(product => product.id === productId));
});

app.delete('/products/:id', (req, res) => {
  const productId = parseInt(req.params.id);
  products = products.filter(product => product.id !== productId);

  res.json({ message: 'Product deleted successfully' });
});

// Orders Routes

app.post('/orders', (req, res) => {
  const newOrder = req.body;
  newOrder.id = orders.length + 1;
  orders.push(newOrder);

  res.json(newOrder);
});

app.get('/orders/:userId', (req, res) => {
  const userId = parseInt(req.params.userId);
  const userOrders = orders.filter(order => order.userId === userId);

  res.json(userOrders);
});

// Cart Routes

app.post('/cart/:userId', (req, res) => {
  const userId = parseInt(req.params.userId);
  const { productId, quantity } = req.body;

  if (!cart[userId]) {
    cart[userId] = {};
  }

  if (!cart[userId][productId]) {
    cart[userId][productId] = 0;
  }

  cart[userId][productId] += quantity;

  res.json({ cart: cart[userId] });
});

app.get('/cart/:userId', (req, res) => {
  const userId = parseInt(req.params.userId);
  const userCart = cart[userId] || {};

  res.json({ cart: userCart });
});

app.delete('/cart/:userId/item/:productId', (req, res) => {
  const userId = parseInt(req.params.userId);
  const productId = parseInt(req.params.productId);

  if (cart[userId] && cart[userId][productId]) {
    delete cart[userId][productId];
  }

  res.json({ cart: cart[userId] || {} });
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
