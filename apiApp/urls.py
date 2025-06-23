from django.urls import path
from . import views


urlpatterns = [
    path('product_list/', views.product_list, name='product-list'),
    path('products/<slug:slug>/', views.product_detail, name='product-detail'),
    path('categories_list/', views.category_list, name='category-list'),
    path('categories/<slug:slug>/', views.category_detail, name='category-detail'),
    path('add_to_cart/', views.add_to_cart, name='add-to-cart'),
    path('update_cartitem_quantity/', views.update_cartitem_quantity, name='update-cartitem-quantity'),
    path('add_review/', views.add_review, name='add-review'),
    path('update_review/<int:pk>/', views.update_review, name='update-review'),
    path('delete_review/<int:pk>/', views.delete_review, name='delete-review'),
    path('delete_cartitem/<int:pk>/', views.delete_cartitem, name='delete-cartitem'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add-to-wishlist'),
    path('search', views.product_search, name='search'),
    path('create_checkout_session/',views.create_checkout_session,name='create_checkout_session'),
    path('webhook/', views.my_webhook_view, name='webhook'),
]


# 4:05