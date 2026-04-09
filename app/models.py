from django.db import models
from django.contrib.auth.models import User

# Create your models here.
CATEGORY_CHOICES=[
    ('CR','Curd'),
    ('ML','Milk'),
    ('LS','Lassi'),
    ('MS','Milkshake'),
    ('PN','Paneer'),
    ('GH','Ghee'),
    ('CZ','Cheese'),
    ('IC','Ice-Creams'),
]
STATE_CHOICES=[
    ('Andaman Nocobar Island','Andaman Nocobar Island'),
    ('Andhra Pradesh','Andhra Pradesh'),
    ('Arunachal Pradesh','Arunachal Pradesh'),
    ('Asam','Asam'),
    ('Bihar','Bihar'),
    ('Chandigarh','Chandigarh'),
    ('Chhatichgarh','Chhatichgarh'),
    ('Dadra & Nagar Haveli','Dadra & Nagar Haveli'),
    ('Dama & Due','Dama & Due'),
    ('Delhi','Delhi'),
    ('Goa','Goa'),
    ('Gujurat','Gujurat'),
    ('Haryana','Haryana'),
    ('Himanchal Pradesh','Himanchal Pradesh'),
    ('jammu & Kashmir','jammu & Kashmir'),
    ('Jharakhand','Jharakhand'),
    ('Karnatak','Karnatak'),
    ('Keral','Keral'),
    ('lakshadweep','lakshadweep'),
    ('Madhya Pradesh','Madhya Pradesh'),
    ('Maharastra','Maharastra'),
    ('Manipur','Manipur'),
    ('Meghalaya','Meghalaya'),
    ('Mizoram','Mizoram'),
    ('Nagaland','Nagaland'),
    ('Odisha','Odisha'),
    ('Pundicherry','Pundicherry'),
    ('Panjab','Panjab'),
    ('Rajasthan','Rajasthan'),
    ('Sikkim','Sikkim'),
    ('tamil Nadu','tamil Nadu'),
    ('Telengana','Telengana'),
    ('Tripura','Tripura'),
    ('Utarakhand','Utarakhand'),
    ('Uttar Pradesh','Uttar Pradesh'),
    ('West Bengal','West Bengal'),
]
STATUS_CHOICES=(
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered'),
    ('Canceled','Canceled'),
    ('Pending','Pending'),
)
class Product(models.Model):
    title=models.CharField(max_length=100)
    selling_price=models.FloatField()
    discount_price=models.FloatField()
    description=models.TextField()
    composition=models.TextField(default='')
    prodapp=models.TextField(default='')
    category=models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image=models.ImageField(upload_to='product')
    def __str__(self):
        return self.title
class Customer(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    locality=models.CharField(max_length=200)
    city=models.CharField(max_length=200)
    mobile=models.IntegerField(default=0)
    state=models.CharField(choices=STATE_CHOICES,max_length=100)
    email=models.EmailField()
    def __str__(self):
        return self.name
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    @property
    def total_cost(self):
        return self.quanitty*self.product.discount_price
class Payment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    amount=models.FloatField()
    razorpay_order_id=models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status=models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id=models.CharField(max_length=100,blank=True,null=True)
    paid=models.BooleanField(default=False)
class OrderPlaced(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    ordered_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default="Pending")
    payment=models.ForeignKey(Payment,on_delete=models.CASCADE,default="")
    @property
    def total_cost(self):
        return self.quantity*self.product.discount_price
class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)