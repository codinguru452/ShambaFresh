from django.db import models
from django.conf import settings

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Seeds', 'Seeds'), ('Fertilizers', 'Fertilizers'), ('Crop Protection', 'Crop Protection'),
        ('Animal Health', 'Animal Health'), ('Animal Feeds', 'Animal Feeds'), ('Grains', 'Grains'),
        ('Farm Tools', 'Farm Tools'),
    ]
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-featured', 'name']

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')]
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    delivery_address = models.TextField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='PENDING')
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, db_index=True)
    mpesa_merchant_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt = models.CharField(max_length=30, blank=True)
    mpesa_result_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} - {self.customer_name}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=160)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'
