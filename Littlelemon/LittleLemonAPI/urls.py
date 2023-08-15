from . import views
from django.urls import path

app_name = 'LittleLemonAPI'
urlpatterns = [
    path('category', views.CategoryView.as_view()),
    # Menu-items endpoints
    path('menu-items', views.MenuItemsListView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemsDetailView.as_view()),
    # User group management endpoints
    path('groups/<str:group_name>/users', views.GroupMemberListView.as_view()),
    path('groups/<str:group_name>/users/<int:pk>',
         views.GroupMemberDeleteView.as_view()),
    # Cart management endpoints
    path('cart/menu-items', views.CartManageView.as_view()),
    # Order management endpoints
    path('orders', views.OrderListCreateView.as_view()),
    path('orders/<int:pk>', views.OrderDetailView.as_view())
]