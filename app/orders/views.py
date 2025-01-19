from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from orders.models import Product, Order, OrderProduct
from orders.serializers import ProductSerializer, OrderSerializer, OrderRequestSerializer


class ProductListCreateView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = JSONParser().parse(request)
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderCreateView(APIView):
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            order_serializer = OrderRequestSerializer(data=data)
            order_serializer.is_valid(raise_exception=True)

            products_data = order_serializer.validated_data['products']
            total_price = 0
            order = Order.objects.create(total_price=0, status='pending')

            for item in products_data:
                product = Product.objects.get(id=item['product']['id'])
                if product.stock < item['quantity']:
                    raise ValidationError(f"Insufficient stock for product: {product.name}")
                total_price += product.price * item['quantity']
                OrderProduct.objects.create(order=order, product=product, quantity=item['quantity'])
                product.stock -= item['quantity']
                product.save()


            order.total_price = total_price
            order.save()

            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)