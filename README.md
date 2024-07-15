<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carrito de Compras</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .product, .cart-item {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            margin: 10px;
            width: 200px;
        }
        .product img {
            width: 100%;
        }
        .cart {
            border: 1px solid #ccc;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .cart-items {
            list-style: none;
            padding: 0;
        }
    </style>
</head>
<body>
    <h1>Productos</h1>
    <div class="product">
        <img src="https://via.placeholder.com/150" alt="Producto 1">
        <h2>Producto 1</h2>
        <input type="number" id="quantity-1" value="1" min="1">
        <button onclick="addToCart('Producto 1', document.getElementById('quantity-1').value)">Añadir al Carrito</button>
    </div>
    <div class="product">
        <img src="https://via.placeholder.com/150" alt="Producto 2">
        <h2>Producto 2</h2>
        <input type="number" id="quantity-2" value="1" min="1">
        <button onclick="addToCart('Producto 2', document.getElementById('quantity-2').value)">Añadir al Carrito</button>
    </div>
    <div class="cart">
        <h2>Carrito de Compras</h2>
        <ul class="cart-items" id="cart-items"></ul>
        <p>Total: $<span id="total">0.00</span></p>
    </div>
    <script>
        const cartItems = JSON.parse(localStorage.getItem('cartItems')) || [];

        function addToCart(productName, quantity) {
            const product = cartItems.find(item => item.name === productName);
            if (product) {
                product.quantity += parseInt(quantity);
            } else {
                cartItems.push({ name: productName, quantity: parseInt(quantity) });
            }
            localStorage.setItem('cartItems', JSON.stringify(cartItems));
            renderCart();
        }

        function renderCart() {
            const cartItemsElement = document.getElementById('cart-items');
            cartItemsElement.innerHTML = '';
            let total = 0;
            cartItems.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.name} - Cantidad: ${item.quantity}`;
                cartItemsElement.appendChild(li);
                total += item.quantity * 10; // Suponiendo que cada producto cuesta $10
            });
            document.getElementById('total').textContent = total.toFixed(2);
        }

        // Renderizar el carrito al cargar la página
        document.addEventListener('DOMContentLoaded', renderCart);
    </script>
</body>
</html>
