
from orders.models import Product, Order
from rest_framework.serializers import ModelSerializer, Serializer, IntegerField, ListField, CharField, SerializerMethodField


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderProductRequestSerializer(Serializer):
    product = IntegerField(source='product.id')
    quantity = IntegerField()

class OrderProductSerializer(Serializer):
    name = CharField(source='product.name')
    quantity = IntegerField()
    product_subtotal = SerializerMethodField()

    def get_product_subtotal(self, obj):
        return obj.total_price

class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(source='orderproduct_set', many=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'total_price', 'status']

class OrderRequestSerializer(Serializer):
    products = ListField(child=OrderProductRequestSerializer(), allow_empty=False)
