from rest_framework import serializers
from . import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ['slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.MenuItem
        fields = ['title', 'price', 'featured', 'category', 'category_id']


class UserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     style={
                                         'input_type': 'password',
                                         'placeholder': 'Password'
                                     })
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
    )

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password'))
        return super().create(validated_data)

    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'password', 'groups']


class CartSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=6,
                                     decimal_places=2,
                                     read_only=True)
    unit_price = serializers.DecimalField(max_digits=6,
                                          decimal_places=2,
                                          read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        menuitem_id = validated_data['menuitem_id']
        menuitem = get_object_or_404(models.MenuItem, id=menuitem_id)
        validated_data['unit_price'] = menuitem.price
        validated_data['user_id'] = self.context['request'].user.id
        cart = models.Cart.objects.filter(menuitem_id=menuitem.id,
                                          user_id=validated_data['user_id'])
        if cart:  # if the item is already in the user's cart, add up the quantity
            cart[0].quantity += validated_data['quantity']
            cart[0].save()
            return cart[0]
        return super().create(
            validated_data)  # if the item is not in, create new record

    class Meta:
        model = models.Cart
        fields = ['quantity', 'unit_price', 'price', 'menuitem_id', 'user_id']


class OrderItemSerializer(serializers.ModelSerializer):
    # order = OrderSerializer(read_only=True)

    class Meta:
        model = models.OrderItem
        fields = ['quantity', 'unit_price', 'price', 'menuitem_id']


class OrderSerializer(serializers.ModelSerializer):
    orderitems = serializers.SerializerMethodField(read_only=True,method_name='get_orderitem')
    delivery_crew_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = models.Order
        fields = [
            'orderitems', 'user', 'delivery_crew','delivery_crew_id', 'status', 'total', 'date',
            'id'
        ]
        extra_kwargs = {
            'user':{'read_only':True},
            'total':{'read_only':True},
            'date':{'read_only':True},
            'id':{'read_only':True}
        }
    def get_orderitem(self, obj):
        orderitems = models.OrderItem.objects.filter(order=obj)
        print(orderitems)
        return OrderItemSerializer(orderitems, many=True).data
