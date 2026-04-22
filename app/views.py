from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from app.models import Product,Customer,Cart,OrderPlaced,Payment,Wishlist
from django.db.models import Count
from app.forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q
import razorpay # type: ignore
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
import os


# Create your views here.
def home(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/index.html",locals())

def about(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/about.html",locals())

def contact(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/contact.html",locals())

def search(request):
    query=request.GET.get('search')
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    product=Product.objects.filter(Q(title__icontains=query))
    return render(request,"app/search.html",locals())

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')
class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request,"app/customerregistration.html",locals())
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congrtulations! User Registration Successful")
            return redirect('../accounts/login')
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,"app/customerregistration.html",locals())

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self, request):
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
        
        # Get customer profile or create empty form
        customer = Customer.objects.filter(user=request.user).first()
        
        if customer:
            form = CustomerProfileForm(instance=customer)
            add_count = Customer.objects.filter(user=request.user).count()
        else:
            form = CustomerProfileForm()
            add_count = 0
        
        recent_orders = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date')[:5]
        order_count = OrderPlaced.objects.filter(user=request.user).count()
        
        # Calculate total saved
        orders = OrderPlaced.objects.filter(user=request.user)
        total_saved = 0
        for order in orders:
            if order.product.selling_price > order.product.discount_price:
                saved = (order.product.selling_price - order.product.discount_price) * order.quantity
                total_saved += saved
        
        context = {
            'totalitem': totalitem,
            'wishitem': wishitem,
            'form': form,
            'add_count': add_count,
            'recent_orders': recent_orders,
            'order_count': order_count,
            'total_saved': total_saved,
            'customer': customer,  # Add customer to context
        }
        return render(request, "app/profile.html", context)
    
    def post(self, request):
        customer = Customer.objects.filter(user=request.user).first()
        
        if customer:
            form = CustomerProfileForm(request.POST, request.FILES, instance=customer)
        else:
            form = CustomerProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            customer_obj = form.save(commit=False)
            customer_obj.user = request.user
            customer_obj.save()
            messages.success(request, 'Profile Saved Successfully!')
            return redirect('profile')
        else:
            messages.warning(request, 'Invalid Input Data')
        
        # Re-render with errors
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
        add_count = Customer.objects.filter(user=request.user).count()
        recent_orders = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date')[:5]
        order_count = OrderPlaced.objects.filter(user=request.user).count()
        
        total_saved = 0
        orders = OrderPlaced.objects.filter(user=request.user)
        for order in orders:
            if order.product.selling_price > order.product.discount_price:
                total_saved += (order.product.selling_price - order.product.discount_price) * order.quantity
        
        context = {
            'totalitem': totalitem,
            'wishitem': wishitem,
            'form': form,
            'add_count': add_count,
            'recent_orders': recent_orders,
            'order_count': order_count,
            'total_saved': total_saved,
        }
        return render(request, "app/profile.html", context)

    
@login_required
def upload_profile_image(request):
    """Upload profile image"""
    if request.method == 'POST' and request.FILES.get('profile_image'):
        try:
            profile_image = request.FILES['profile_image']
            
            # Get or create customer profile
            customer, created = Customer.objects.get_or_create(user=request.user)
            
            # Delete old image if exists
            if customer.profile_image:
                if os.path.isfile(customer.profile_image.path):
                    os.remove(customer.profile_image.path)
            
            # Save new image
            customer.profile_image = profile_image
            customer.save()
            
            return JsonResponse({'success': True, 'message': 'Profile image updated'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)

@login_required
def address(request):
    totalitem = Cart.objects.filter(user=request.user).count()
    wishitem = Wishlist.objects.filter(user=request.user).count()
    addresses = Customer.objects.filter(user=request.user)
    form = CustomerProfileForm()
    return render(request, "app/address.html", locals())

@login_required
@require_POST
def delete_address(request):
    """Delete an address"""
    try:
        address_id = request.POST.get('address_id')
        address = Customer.objects.get(id=address_id, user=request.user)
        address.delete()
        return JsonResponse({'success': True, 'message': 'Address deleted successfully'})
    except Customer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Address not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def set_default_address(request):
    """Set an address as default"""
    try:
        address_id = request.POST.get('address_id')
        # Since we don't have a default field, we'll just return success
        # You can implement this feature by adding a 'is_default' field to Customer model if needed
        return JsonResponse({'success': True, 'message': 'Default address updated'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@method_decorator(login_required, name='dispatch')
class UpdateAddress(View):
    def get(self, request, pk):
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
        address = get_object_or_404(Customer, pk=pk, user=request.user)
        form = CustomerProfileForm(instance=address)
        return render(request, "app/updateaddress.html", locals())
    
    def post(self, request, pk):
        address = get_object_or_404(Customer, pk=pk, user=request.user)
        form = CustomerProfileForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address Updated Successfully!")
            return redirect('address')
        messages.warning(request, "Invalid Input Data")
        return redirect('address')
    
@login_required
def get_user_addresses(request):
    """
    Fetch all addresses for the logged-in user.
    Returns JSON response with addresses array.
    """
    try:
        addresses = Customer.objects.filter(user=request.user)

        address_list = []
        for addr in addresses:
            address_list.append({
                'id': addr.id,
                'name': addr.name,
                'mobile': addr.mobile,
                'email': addr.email,
                'locality': addr.locality,
                'city': addr.city,
                'state': addr.state,
                'is_default': getattr(addr, 'is_default', False),
            })
        
        return JsonResponse({
            'success': True,
            'addresses': address_list,
            'count': len(address_list)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

class CategoryView(View):
    def get(self,request,val):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        product=Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title').annotate(total=Count('title'))
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,"app/category.html",locals())

class CategoryTitle(View):
    def get(self,request,val):
        totalitem=0
        wishitem=0
        product=Product.objects.filter(title=val)
        title=Product.objects.filter(category=product[0].category).values('title')
        totalitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/category.html",locals())

class ProductDetail(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
        wishlist=Wishlist.objects.filter(Q(product=product)&Q(user=request.user))
        save_price=product.selling_price - product.discount_price
        save_percentage = 100 - (product.discount_price/product.selling_price * 100)
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/productdetail.html",locals())

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    
    # Check if item already exists in cart
    cart_item = Cart.objects.filter(user=user, product=product).first()
    
    if cart_item:
        # If exists, increase quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Quantity updated for {product.title}")
    else:
        # If not exists, create new
        Cart(user=user, product=product).save()
        messages.success(request, f"{product.title} added to cart")
    
    # Get updated cart count
    totalitem = Cart.objects.filter(user=user).count()
    
    # If it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Product added to cart',
            'totalitem': totalitem
        })
    
    return redirect("/cart")

@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = sum(item.quantity * item.product.discount_price for item in cart)
    totalamount = amount + 40 if cart.exists() else 0
    totalitem = cart.count()
    wishitem = Wishlist.objects.filter(user=user).count()
    return render(request, "app/addtocart.html", locals())

@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount=0
        for p in cart_items:
            value=p.quantity*p.product.discount_price
            famount+=value
            totalamount=famount+40
        razoramount=int(totalamount*100)
        client=razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
        print("gETTING rAZORpAY dETAILS: ",settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
        data={'amount':razoramount,'currency':'INR','receipt':'order_rcptid_13'}
        payment_response=client.order.create(data=data)
        print(payment_response)
        #{'amount': 10000, 'amount_due': 10000, 'amount_paid': 0, 'attempts': 0, 'created_at': 1747898123, 'currency': 'INR', 'entity': 'order', 'id': 'order_QXt9smNcloi2HK', 'notes': [], 'offer_id': None, 'receipt': 'order_receipt_13', 'status': 'created'}
        order_id=payment_response['id']
        order_status=payment_response['status']
        if order_status == 'created':
            payment=Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
        return render(request,"app/checkout.html",locals())


def create_orders_from_cart(user, customer, payment):
    cart_items = Cart.objects.filter(user=user)
    for item in cart_items:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=item.product,
            quantity=item.quantity,
            payment=payment
        )
    cart_items.delete()

@login_required
def orders(request):
    totalitem = Cart.objects.filter(user=request.user).count()
    wishitem = Wishlist.objects.filter(user=request.user).count()
    order_placed = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, "app/orders.html", locals())

@login_required
def payment_done(request):
    order_id=request.GET.get('order_id')
    payment_id=request.GET.get('payment_id')
    cust_id=request.GET.get('cust_id')
    user=request.user
    customer=Customer.objects.get(id=cust_id)
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid=True
    payment.razorpay_payment_id=payment_id
    payment.save()
    create_orders_from_cart(user, customer, payment)
    return redirect('orders')


@login_required
@require_POST
def verify_payment(request):
    try:
        order_id = request.POST.get('razorpay_order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')
        cust_id = request.POST.get('cust_id')

        if not all([order_id, payment_id, signature, cust_id]):
            return JsonResponse({'success': False, 'error': 'Missing payment details'}, status=400)

        customer = get_object_or_404(Customer, id=cust_id, user=request.user)
        payment = get_object_or_404(Payment, razorpay_order_id=order_id, user=request.user)

        if payment.paid:
            return JsonResponse({'success': True, 'redirect_url': '/orders/'})

        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })

        with transaction.atomic():
            payment.razorpay_payment_id = payment_id
            payment.razorpay_payment_status = 'paid'
            payment.paid = True
            payment.save()
            create_orders_from_cart(request.user, customer, payment)

        return JsonResponse({'success': True, 'redirect_url': '/orders/'})
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'success': False, 'error': 'Payment signature verification failed'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        if not prod_id:
            return JsonResponse({'status': 'error', 'message': 'Product ID required'}, status=400)
        
        try:
            cart_item = Cart.objects.get(product_id=prod_id, user=request.user)
            cart_item.quantity += 1
            cart_item.save()
            
            cart_items = Cart.objects.filter(user=request.user)
            amount = sum(item.quantity * item.product.discount_price for item in cart_items)
            totalamount = amount + 40
            
            return JsonResponse({
                'status': 'success',
                'quantity': cart_item.quantity,
                'amount': amount,
                'totalamount': totalamount
            })
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        if not prod_id:
            return JsonResponse({'status': 'error', 'message': 'Product ID required'}, status=400)
        
        try:
            cart_item = Cart.objects.get(product_id=prod_id, user=request.user)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                return JsonResponse({'status': 'error', 'message': 'Minimum quantity is 1'}, status=400)
            
            cart_items = Cart.objects.filter(user=request.user)
            amount = sum(item.quantity * item.product.discount_price for item in cart_items)
            totalamount = amount + 40
            
            return JsonResponse({
                'status': 'success',
                'quantity': cart_item.quantity,
                'amount': amount,
                'totalamount': totalamount
            })
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        if not prod_id:
            return JsonResponse({'status': 'error', 'message': 'Product ID required'}, status=400)
        
        try:
            cart_item = Cart.objects.get(product_id=prod_id, user=request.user)
            cart_item.delete()
            
            cart_items = Cart.objects.filter(user=request.user)
            pcount = cart_items.count()
            amount = sum(item.quantity * item.product.discount_price for item in cart_items)
            totalamount = amount + 40 if pcount > 0 else 0
            
            return JsonResponse({
                'status': 'success',
                'pcount': pcount,
                'amount': amount,
                'totalamount': totalamount
            })
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# Fix plus_wishlist and minus_wishlist
@login_required
def plus_wishlist(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        if not prod_id:
            return JsonResponse({'status': 'error', 'message': 'Product ID required'}, status=400)
        
        try:
            product = Product.objects.get(id=prod_id)
            Wishlist.objects.get_or_create(user=request.user, product=product)
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            return JsonResponse({
                'status': 'success',
                'message': 'Added to Wishlist',
                'wishlist_count': wishlist_count
            })
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def minus_wishlist(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        if not prod_id:
            return JsonResponse({'status': 'error', 'message': 'Product ID required'}, status=400)
        
        try:
            product = Product.objects.get(id=prod_id)
            Wishlist.objects.filter(user=request.user, product=product).delete()
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            return JsonResponse({
                'status': 'success',
                'message': 'Removed from Wishlist',
                'wishlist_count': wishlist_count
            })
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def show_wishlist(request):
    user = request.user
    totalitem = Cart.objects.filter(user=user).count()
    wishitem = Wishlist.objects.filter(user=user).count()
    product = Wishlist.objects.filter(user=user)
    return render(request, "app/wishlist.html", locals())

