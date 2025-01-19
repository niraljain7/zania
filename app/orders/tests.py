from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from orders.models import Product, Order, OrderProduct

class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product_data = {
            "name": "Test Product",
            "description": "testing",
            "price": 10.0,
            "stock": 100
        }

    def test_create_product(self):
        response = self.client.post("/products/", self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, "Test Product")

    def test_list_products(self):
        Product.objects.create(**self.product_data)
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Product")

class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product1 = Product.objects.create(name="Product 1", description="First product", price=20.0, stock=50)
        self.product2 = Product.objects.create(name="Product 2", description="Second product", price=15.0, stock=30)
        self.order_data = {
            "products": [
                {"product": self.product1.id, "quantity": 2},
                {"product": self.product2.id, "quantity": 3}
            ]
        }

    def test_create_order_success(self):
        response = self.client.post("/orders/", self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.total_price, 85.0)
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.products.count(), 2)

    def test_create_order_insufficient_stock(self):
        self.order_data['products'][0]['quantity'] = 60
        response = self.client.post("/orders/", self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Insufficient stock", response.data['error'])

    def test_create_order_invalid_product(self):
        self.order_data['products'].append({"product_id": 999, "quantity": 1})
        response = self.client.post("/orders/", self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class IntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product1 = Product.objects.create(name="Product 1", description="p1", price=10.0, stock=5)
        self.product2 = Product.objects.create(name="Product 2", description="p2", price=20.0, stock=2)

    def test_full_order_flow(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        order_data = {
            "products": [
                {"product": self.product1.id, "quantity": 2},
                {"product": self.product2.id, "quantity": 1}
            ]
        }
        response = self.client.post("/orders/", order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']

        order = Order.objects.get(id=order_id)
        self.assertEqual(order.total_price, 40.0)
        self.assertEqual(order.status, "pending")
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 3) 
        self.assertEqual(self.product2.stock, 1)
