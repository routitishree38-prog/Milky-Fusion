from django.contrib import admin
from app.models import Product,Customer,Cart,Payment,OrderPlaced,Wishlist
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import Group
# Register your models here.
@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display=['id','title','discount_price','category','product_image']
@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display=['id','user','name','locality','city','mobile']
@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display=['id','user','products','quantity']
    #for creating linkable product title in cart table [carts --> products]
    def products(self,obj):
        link=reverse("admin:app_product_change",args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link,obj.product.title)
@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display=['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','paid']
@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display=['id','user','customers','products','quantity','ordered_date','status','payments']
    #for creating linkable customer-name in orderplaced table [orderplaced --> customer]
    def customers(self,obj):
        link=reverse("admin:app_customer_change",args=[obj.customer.pk])
        return format_html('<a href="{}">{}</a>',link,obj.customer.name)
    #for creating linkable product title in orderplaced table [orderplaced --> products]
    def products(self,obj):
        link=reverse("admin:app_product_change",args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link,obj.product.title)
    #for creating linkable payments in orderplaced table [orderplaced --> payments]
    def payments(self,obj):
        link=reverse("admin:app_payment_change",args=[obj.payment.pk])
        return format_html('<a href="{}">{}</a>',link,obj.payment.razorpay_payment_id)
@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display=['id','user','products']
    #for creating linkable product title in wishlist table [wishlist --> products]
    def products(self,obj):
        link=reverse("admin:app_product_change",args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link,obj.product.title)
admin.site.unregister(Group)