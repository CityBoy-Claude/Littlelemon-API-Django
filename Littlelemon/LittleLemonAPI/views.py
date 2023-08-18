from django.contrib.auth.models import Group, User
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import (BasePermission, IsAdminUser,
                                        IsAuthenticated)

from . import models, serializers
from rest_framework.response import Response
# Create your views here.
group_mapping = {'manager': 'Manager', 'delivery-crew': 'Delivery crew'}


class isManagerOrAdmin(BasePermission):

    def has_permission(self, request, view):
        if request.user:
            return request.user.groups.filter(
                name='Manager') or request.user.is_staff
        return False

class canPatchOrderDetail(BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return request.user.groups.filter(
                name='Delivery crew') or request.user.groups.filter(
                name='Manager') or request.user.is_staff
        return False


class CategoryView(generics.ListCreateAPIView):
    '''
    endpoint: /api/category
    GET, POST for manager/admin. List/Create categories.
    '''
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [isManagerOrAdmin]


class MenuItemsListView(generics.ListCreateAPIView):
    '''
    endpoint: /api/menu-items/{menuItem}
    GET for all users. List allsingle menu items.
    POST for manager/admin. Create new menu item.
    '''

    def get_serializer_class(self):
        return serializers.MenuItemSerializer

    def get_queryset(self):
        items=models.MenuItem.objects.all()
        # filters
        category_name=self.request.query_params.get('category')
        to_price=self.request.query_params.get('to_price')
        from_price=self.request.query_params.get('from_price')
        if category_name:
            items=items.filter(category__title=category_name)
        if to_price:
            items=items.filter(price__lte=to_price)
        if from_price:
            items=items.filter(price__gte=from_price)
        # ordering
        ordering=self.request.query_params.get('ordering')
        if ordering:
            ordering_fields=ordering.split(",")
            items = items.order_by(*ordering_fields)
        return items

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [isManagerOrAdmin()]


class MenuItemsDetailView(generics.RetrieveUpdateDestroyAPIView):
    '''
    endpoint: /api/menu-items/{menuItem}
    GET for all users. Lists single menu item
    PUT, PATCH, DELETE for manager/admin. Updates/Deletes single menu item.
    '''

    def get_serializer_class(self):
        return serializers.MenuItemSerializer

    def get_queryset(self):
        return models.MenuItem.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [isManagerOrAdmin()]


class GroupMemberListView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        return serializers.UserSerializers

    def get_queryset(self):
        group_name = self.kwargs['group_name']
        if group_name not in group_mapping:
            raise NotFound
        group = get_object_or_404(Group, name=group_mapping[group_name])
        return group.user_set.all()

    def create(self, request, *args, **kwargs):
        group_name = self.kwargs['group_name']
        if group_name not in group_mapping:
            raise NotFound
        group = get_object_or_404(Group, name=group_mapping[group_name])
        res = super().create(request, *args, **kwargs)
        if res.status_code != status.HTTP_201_CREATED:
            return res
        group.user_set.add(
            get_object_or_404(User, username=res.data['username']))
        return res

    def get_permissions(self):
        return [isManagerOrAdmin()]


class GroupMemberDeleteView(generics.DestroyAPIView):

    def get_serializer_class(self):
        return serializers.MenuItemSerializer

    def get_queryset(self):
        group_name = self.kwargs['group_name']
        if group_name not in group_mapping:
            raise NotFound
        group = get_object_or_404(Group, name=group_mapping[group_name])
        return group.user_set.all()

    def delete(self, request, *args, **kwargs):
        group_name = self.kwargs['group_name']
        if group_name not in group_mapping:
            raise NotFound
        group = get_object_or_404(Group, name=group_mapping[group_name])
        res = super().delete(request, *args, **kwargs)
        if res.status_code != status.HTTP_204_NO_CONTENT:
            return res
        res.status_code = status.HTTP_200_OK
        return res

    def get_permissions(self):
        return [isManagerOrAdmin()]


class CartManageView(generics.ListCreateAPIView, generics.DestroyAPIView):
    '''
    endpoint: /api/cart/menu-items
    GET, POST, DELETE for authenticated users
    '''

    def get_serializer_class(self):
        return serializers.CartSerializer

    def get_queryset(self):
        user = self.request.user
        return models.Cart.objects.filter(user_id=user.id)

    def destroy(self, request, *args, **kwargs):
        '''
        Deletes all menu items created by the current user
        '''
        cart_items = self.get_queryset()
        for instance in cart_items:
            self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    def get_permissions(self):
        return [IsAuthenticated()]


class OrderListCreateView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        return serializers.OrderSerializer

    def get_queryset(self):
        user=self.request.user
        user_groups = user.groups
        if user_groups.filter(name='Manager').exists():
            return models.Order.objects.all()
        if user_groups.filter(name='Delivery crew').exists():
            return models.Order.objects.filter(delivery_crew=user.id)
        return models.Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        request.data['user'] = user.id
        request.data['total'] = 0
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        cart_items = models.Cart.objects.filter(user_id=user.id)
        if not cart_items:
            return Response(status=status.HTTP_404_NOT_FOUND)
        total_price = 0
        for cart_item in cart_items:
            total_price += cart_item.price
            order_item = models.OrderItem(order=order,
                                          menuitem=cart_item.menuitem,
                                          quantity=cart_item.quantity,
                                          unit_price=cart_item.unit_price,
                                          price=cart_item.price)
            order_item.save()
            cart_item.delete()
        serializer = self.get_serializer(order,
                                         data={'total': total_price},
                                         partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(serializer.data))

    def get_permissions(self):
        return [IsAuthenticated()]


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_serializer_class(self):
        return serializers.OrderSerializer

    def get_queryset(self):
        return models.Order.objects.all()

    def get_object(self):
        # Manager can access to all order
        if self.request.user.groups.filter(name='Manager').exists():
            return super().get_object()
        order = super().get_object()
        # Customer or Delivery crew can only access to the related order
        if order.user == self.request.user or order.delivery_crew == self.request.user:
            return order
        else:
            raise PermissionDenied

    def delete(self, request, *args, **kwargs):
        orderitems = models.OrderItem.objects.filter(
            order_id=self.get_object().id)
        for orderitem in orderitems:
            orderitem.delete()
        return super().delete(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        if 'delivery_crew_id' in request.data.keys():
            if self.request.user.groups.filter(name='Manager').exists():
                delivery_crew_id = request.data.get('delivery_crew_id')
                print(User.objects.get(pk=delivery_crew_id))
                if not User.objects.get(pk=delivery_crew_id).groups.filter(name='Delivery crew').exists():
                    return HttpResponseBadRequest()
            else:
                return HttpResponseForbidden()
        return super().patch(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method=='PATCH':
            print('patch')
            return [canPatchOrderDetail()]
        return [isManagerOrAdmin()]
