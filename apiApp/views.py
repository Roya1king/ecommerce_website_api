import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product,Cart,CartItem, Review, Wishlist,OrderItem,Order
from .serializers import CategoryDetailSerializer, CategoryListSerializer, ProductListSerializer, ProductDetailSerializer,CartSerializer, ReviewSerializer, WishlistSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY
# endpoint_secret = settings.WEBHOOK_SECRET

User=get_user_model()
 
@api_view(['GET'])
def product_list(request):
    products=Product.objects.filter(featured=True)
    serializers=ProductListSerializer(products, many=True)
    return Response(serializers.data)

@api_view(['GET'])
def product_detail(request, slug):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
    
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)

@api_view(['Get'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_detail(request, slug):
    try:
        category = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)
    
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)

@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.GET.get('cart_code')
    product_id = request.GET.get('product_id')

    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    product= Product.objects.get(id=product_id)

    cartitem,_=CartItem.objects.get_or_create(cart=cart, product=product, quantity=1)
    cartitem.quantity = 1
    cartitem.save()

    serializer= CartSerializer(cart)
    return Response(serializer.data)

@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id= request.GET.get('item_id')
    quantity= request.GET.get('quantity')
    quantity= int(quantity) if quantity else 1

    cartitem=CartItem.objects.get(id=int(cartitem_id))
    cartitem.quantity=quantity
    cartitem.save()

    serilizer=CartSerializer(cartitem.cart)
    return Response({"data":serilizer.data, "message":"Cart item quantity updated successfully"})

@api_view(['DELETE'])
def delete_cartitem(request, pk):
    try:
        cartitem = CartItem.objects.get(id=pk)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=404)

    cartitem.delete()
    return Response({"message": "Cart item deleted successfully"}, status=204)

@api_view(['POST'])
def add_review(request):
    product_id=request.data.get('product_id')
    email=request.data.get('email')
    rating=request.data.get('rating')
    review_text=request.data.get('review')
    if not all([product_id, email, rating, review_text]):
        return Response({"error": "All fields are required"}, status=400)
    product=Product.objects.get(id=product_id)
    user= User.objects.get(email=email)

    if Review.objects.filter(product=product, user=user).exists():
        return Response({"error": "You have already reviewed this product"}, status=400)

    review= product.reviews.create(product=product, user=user, rating=rating, review=review_text)
    serilizer= ReviewSerializer(review)
    return Response(serilizer.data)

@api_view(['PUT'])
def update_review(request,pk):
    review=Review.objects.get(id=pk)
    rating = request.data.get('rating')
    review_text = request.data.get('review')

    if not all([pk, rating, review_text]):
        return Response({"error": "All fields are required"}, status=400)

    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)

    review.rating = rating
    review.review = review_text
    review.save()

    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_review(request, pk):
    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)

    review.delete()
    return Response({"message": "Review deleted successfully"}, status=204)


@api_view(['POST'])
def add_to_wishlist(request):
    email = request.data.get("email")
    product_id = request.data.get("product_id")

    # Validate inputs
    if not email or not product_id:
        return Response({"detail": "Email and product_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, email=email)
    product = get_object_or_404(Product, id=product_id)

    # Check if already in wishlist
    wishlist_item = Wishlist.objects.filter(user=user, product=product).first()
    if wishlist_item:
        wishlist_item.delete()
        return Response({"detail": "Wishlist item removed."}, status=status.HTTP_200_OK)

    # Create new wishlist item
    new_wishlist = Wishlist.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def product_search(request):
    query = request.query_params.get('query', '').strip()
    if not query:
        return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query) )
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_checkout_session(request):
    cart_code = request.data.get("cart_code")
    email = request.data.get("email")
    cart = Cart.objects.get(cart_code=cart_code)
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email= email,
            payment_method_types=['card'],


            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item.product.name},
                        'unit_amount': int(item.product.price * 100),  # Amount in cents
                    },
                    'quantity': item.quantity,
                }
                for item in cart.cartitems.all()
            ] + [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'VAT Fee'},
                        'unit_amount': 500,  # $5 in cents
                    },
                    'quantity': 1,
                }
            ],


           
            mode='payment',
            # success_url="http://localhost:3000/success",
            # cancel_url="http://localhost:3000/cancel",

            success_url="https://next-shop-self.vercel.app/success",
            cancel_url="https://next-shop-self.vercel.app/failed",
            metadata = {"cart_code": cart_code}
        )
        return Response({'data': checkout_session})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@csrf_exempt
def my_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  if (
    event['type'] == 'checkout.session.completed'
    or event['type'] == 'checkout.session.async_payment_succeeded'
  ):
    session = event['data']['object']
    cart_code = session.get("metadata", {}).get("cart_code")

    fulfill_checkout(session, cart_code)


  return HttpResponse(status=200)

def fulfill_checkout(session, cart_code):
    
    order = Order.objects.create(stripe_checkout_id=session["id"],
        amount=session["amount_total"],
        currency=session["currency"],
        customer_email=session["customer_email"],
        status="Paid")
    

    print(session)


    cart = Cart.objects.get(cart_code=cart_code)
    cartitems = cart.cartitems.all()

    for item in cartitems:
        orderitem = OrderItem.objects.create(order=order, product=item.product, 
                                             quantity=item.quantity)
    
    cart.delete()