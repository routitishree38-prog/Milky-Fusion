from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from app.forms import LoginForm, MyPasswordResetForm,MyPasswordChangeForm,MySetPasswordForm
from django.contrib import admin

urlpatterns=[
    path('',views.home,name='home'),
    path('category/<slug:val>',views.CategoryView.as_view(),name="category"),
    path('category-title/<val>',views.CategoryTitle.as_view(),name="category-title"),
    path('product-detail/<int:pk>',views.ProductDetail.as_view(),name="product-detail"),
    path('about/',views.about,name="about"),
    path('contact/',views.contact,name="contact"),
    path('search/',views.search,name="search"),
    path('profile/',views.ProfileView.as_view(),name='profile'),
    path('upload-profile-image/', views.upload_profile_image, name='upload_profile_image'),
    path('address/',views.address,name='address'),
    path('get-addresses/', views.get_user_addresses, name='get_addresses'),
    path('updateaddress/<int:pk>',views.UpdateAddress.as_view(),name="update-address"),
    path('delete-address/', views.delete_address, name='delete_address'),
    path('set-default-address/', views.set_default_address, name='set_default_address'),
    path('add-to-cart/',views.add_to_cart,name="add-to-cart"),
    path('cart/',views.show_cart,name="showcart"),
    path('wishlist/',views.show_wishlist,name="showwishlist"),
    path('checkout/',views.checkout.as_view(),name="checkout"),
    path('paymentdone/',views.payment_done,name='paymentdone'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('orders/',views.orders,name="orders"),
    path('pluscart/',views.plus_cart),
    path('minuscart/',views.minus_cart),
    path('removecart/',views.remove_cart),
    path('pluswishlist/',views.plus_wishlist),
    path('minuswishlist/',views.minus_wishlist),
    
    #login authentication
    path('registration/',views.CustomerRegistrationView.as_view(),name="registration"),
    path('accounts/login/',auth_view.LoginView.as_view(template_name="app/login.html",authentication_form=LoginForm),name="login"),
    path('passwordchange/',auth_view.PasswordChangeView.as_view(template_name="app/passwordchange.html",form_class=MyPasswordChangeForm,success_url="/passwordchangedone"),name="passwordchange"),
    path('passwordchangedone/',auth_view.PasswordChangeDoneView.as_view(template_name="app/passwordchangedone.html"),name="passwordchangedone"),
    path('password-reset/',auth_view.PasswordResetView.as_view(template_name="app/passwordreset.html",form_class=MyPasswordResetForm),name='password_reset'),
    path('password-reset/done/',auth_view.PasswordResetDoneView.as_view(template_name="app/passwordresetdone.html"),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_view.PasswordResetConfirmView.as_view(template_name="app/passwordresetconfirm.html",form_class=MySetPasswordForm),name='password_reset_confirm'),
    path('password-reset-complete/',auth_view.PasswordResetCompleteView.as_view(template_name="app/passwordresetcomplete.html"),name='password_reset_complete'),
    path('logout/', views.user_logout, name='logout'),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

admin.site.site_header="Milky Fusion"
admin.site.site_title="Milky Fusion"
admin.site.site_index_title="Welcome to Milky Fusion"
