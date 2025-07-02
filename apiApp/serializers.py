from rest_framework import serializers
from apiApp.models import CustomerAddress, Order, OrderItem, Product, Category, CartItem,Cart, ProductRating, Review, Wishlist  # ✅ Correct import
from django.contrib.auth import get_user_model  # ✅ Use get_user_model() to get the user model

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product  # ✅ Use actual model class
        fields = ["id", "name", "price", "slug", "image"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username", "first_name", "last_name", "profile_picture_url"]

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review 
        fields = ["id", "user", "rating", "review", "created", "updated"]


class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating 
        fields =[ "id", "average_rating", "total_reviews"]

class ProductDetailSerializer(serializers.ModelSerializer):

    reviews = ReviewSerializer(read_only=True, many=True)
    rating = ProductRatingSerializer(read_only=True)
    poor_review = serializers.SerializerMethodField()
    fair_review = serializers.SerializerMethodField()
    good_review = serializers.SerializerMethodField()
    very_good_review = serializers.SerializerMethodField()
    excellent_review = serializers.SerializerMethodField()

    similar_products = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ["id", "name", "description", "slug", "image", "price", "reviews", "rating", "similar_products", "poor_review", "fair_review", "good_review",
                  "very_good_review", "excellent_review"]

    def get_similar_products(self, product):
        products = Product.objects.filter(category=product.category).exclude(id=product.id)
        serializer = ProductListSerializer(products, many=True)
        return serializer.data
    
    def get_poor_review(self, product):
        poor_review_count = product.reviews.filter(rating=1).count()
        return poor_review_count
    
    def get_fair_review(self, product):
        fair_review_count = product.reviews.filter(rating=2).count()
        return fair_review_count
    
    def get_good_review(self, product):
        good_review_count = product.reviews.filter(rating=3).count()
        return good_review_count
    
    def get_very_good_review(self, product):
        very_good_review_count = product.reviews.filter(rating=4).count()
        return very_good_review_count
    
    def get_excellent_review(self, product):
        excellent_review_count = product.reviews.filter(rating=5).count()
        return excellent_review_count

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
        model = get_user_model()
        fields = ["id", "email", "username", "first_name", "last_name", "profile_picture_url"]

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

class SimpleCartSerializer(serializers.ModelSerializer):
    num_of_items = serializers.SerializerMethodField()
    class Meta:
        model = Cart 
        fields = ["id", "cart_code", "num_of_items"]

    def get_num_of_items(self, cart):
        num_of_items = sum([item.quantity for item in cart.cartitems.all()])
        return num_of_items

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id", "quantity", "product"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True, many=True)
    class Meta:
        model = Order 
        fields = ["id", "stripe_checkout_id", "amount", "items", "status", "created_at"]

class CustomerAddressSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    class Meta:
        model = CustomerAddress
        fields = "__all__"




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

