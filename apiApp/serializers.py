from rest_framework import serializers
from apiApp.models import Product, Category, CartItem,Cart, Review, Wishlist  # ✅ Correct import
from django.contrib.auth import get_user_model  # ✅ Use get_user_model() to get the user model

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product  # ✅ Use actual model class
        fields = ["id", "name", "price", "slug", "image"]

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product  # ✅
        fields = ["id", "name", "description", "price", "slug", "image"]

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category  # ✅
        fields = ["id", "name", "slug", "image"]

class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category  # ✅
        fields = ["id", "name", "products", "image"]

class CartItemSerializer(serializers.ModelSerializer): 
    product = ProductListSerializer(read_only=True)  # Use ProductListSerializer for nested product details
    subtotal = serializers.SerializerMethodField()  # Custom field to calculate subtotal
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "subtotal"]
    
    def get_subtotal(self, cart_item):
        return cart_item.product.price * cart_item.quantity

class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(many=True, read_only=True)  # Use CartItemSerializer for nested cart items
    cart_total= serializers.SerializerMethodField()  # Custom field to calculate cart total
    class Meta:
        model = Cart # Use the actual Cart model
        fields = ["id", "cart_code", "cartitems", "cart_total"]  # Include cart_items in the fields

    def get_cart_total(self, cart):
        total = sum(item.product.price * item.quantity for item in cart.cartitems.all())
        return total

class CartStatSerializer(serializers.ModelSerializer):
    cart_quantity = serializers.SerializerMethodField()  # Custom field to calculate total quantity of items in the cart

    class Meta:
        model = Cart  # Use the actual Cart model
        fields = ["id", "cart_code", "cart_quantity"]  # Include cart_items in the fields

    def get_cart_quantity(self, cart):
        return sum(item.quantity for item in cart.cartitems.all())

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()  # Use the get_user_model() function to get the user model
        fields = ["id","first_name", "last_name","profile_picture_url"]  # Include relevant fields

class ReviewSerializer(serializers.ModelSerializer):
    user= UserSerializer(read_only=True)  # Use UserSerializer for nested user details
    class Meta:
        model = Review
        fields = ["id","user", "review", "rating", "updated", "created"]

class WishlistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    class Meta:
        model = Wishlist  # Assuming you want to use CartItem for wishlist items
        fields = ["id", "user","product", "created_at"]  # Include relevant fields






# from rest_framework import serializers

# class ProductListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = "apiApp.Product"
#         fields = ["id", "name" , "price", "slug", "image"]

# class ProductDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = "apiApp.Product"
#         fields = ["id", "name", "description", "price", "slug", "image",]

# class CategoryListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = "apiApp.Category"
#         fields = ["id", "name", "slug", "image"]

# class CategoryDetailSerializer(serializers.ModelSerializer):
#     products= ProductListSerializer(many=True, read_only=True)
#     class Meta:
#         model = "apiApp.Category"
#         fields = ["id", "name", "products", "image"]

