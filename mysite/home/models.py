from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.utils.html import format_html
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from decimal import Decimal
import os
#Kiểm tra file có phải ảnh không
def validate_image_extension(file):
    ext = os.path.splitext(file.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Chỉ chấp nhận file ảnh (.jpg, .png, .gif)')

# Change Forms register
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1', 'password2']
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Bootstrap style
                'placeholder': field.label,
            })
# === Bảng thêm cho user ===
# # models.py
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)  # Số điện thoại
    avatar = models.FileField(upload_to='avatars/', blank=True, null=True,validators=[validate_image_extension])  # Hình đại diện
    address = models.TextField(blank=True, null=True)  # Địa chỉ

    def __str__(self):
        return f"{self.user.username}'s Profile"    
    @property
    def AvtUrl(self):
        try: 
            url = self.avatar.url
        except:
            url = ''
        return url
# === Các bảng phân loại sản phẩm ===
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
class ProductTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class Color(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hex_value = models.CharField(max_length=7, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class FinishType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class AgeRange(models.Model):
    description = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.description
# === Sản phẩm ===

#mapping sản phẩm tránh lỗi
class ProductMapping(models.Model):
    model_item_id = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.model_item_id} → {self.product.name}"
class Product(models.Model):
    name = models.CharField(max_length=200)  # ❌ BỎ null=True
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ❌ BỎ luôn null=True

    image = models.FileField(
        upload_to='products/',
        null=True,
        blank=True,
        validators=[validate_image_extension]
    )
    digital = models.BooleanField(default=False)

    description = models.TextField(null=True, blank=True)
    details_json = models.JSONField(null=True, blank=True)

    brand = models.ForeignKey(Brand, null=True, on_delete=models.SET_NULL)
    manufacturer = models.ForeignKey(Manufacturer, null=True, on_delete=models.SET_NULL)

    categories = models.ManyToManyField(Category, blank=True)
    tags = models.ManyToManyField(ProductTag, blank=True)
    color = models.ManyToManyField(Color, blank=True)

    finish_type = models.ForeignKey(FinishType, null=True, on_delete=models.SET_NULL)
    age_range = models.ForeignKey(AgeRange, null=True, on_delete=models.SET_NULL)

    average_rating = models.FloatField(default=0)
    rating_number = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    @property
    def ImageUrl(self):
        try: 
            url = self.image.url
        except:
            url = ''
        return url
    
    def update_rating(self):
        from django.db.models import Avg, Count
        stats = self.review_set.aggregate(avg=Avg('rating'), count=Count('id'))
        self.average_rating = round(stats['avg'] or 0, 1)
        self.rating_number = stats['count']
        self.save()

    @property
    def get_discounted_price(self):
        now = timezone.now()
        active_discounts = self.discounts.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-discount_percent')  # Lấy ưu đãi cao nhất nếu có nhiều

        if active_discounts.exists():
            discount = active_discounts.first().discount_percent
            return self.price * (Decimal(100) - discount) / Decimal(100)
        return self.price 
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.FileField(
        upload_to='product_img_description/',
        null=True,
        blank=True,
        validators=[validate_image_extension]
    )   
    def __str__(self):
        return f"Image for {self.product.name}"

    def image_preview(self):
        if self.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', self.image.url)
        return "No image"

    image_preview.short_description = "Preview"
class Order(models.Model):
    customer = models.ForeignKey(User,on_delete = models.SET_NULL,blank=True, null = True)
    name = models.CharField(max_length = 200, null = True)
    date_Order = models.DateField(auto_now_add = True)
    complete = models.BooleanField(default = False, null = True, blank = False)
    transaction_id = models.CharField(max_length = 200, null = True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_discounted_total for item in orderitems])
        return total
class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete = models.SET_NULL,blank=True, null = True)
    order = models.ForeignKey(Order,on_delete = models.SET_NULL,blank=True, null = True)
    quantity = models.IntegerField(default=0, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # Thời điểm giảm giá 
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discounted_price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def get_total(self):
        return Decimal(self.product.price) * self.quantity

    @property
    def get_discounted_total(self):
        return Decimal(self.product.get_discounted_price) * self.quantity

    @property
    def get_discount_amount(self):
        return self.get_total - self.get_discounted_total

    @property
    def get_saved_amount(self):
        return (self.product.price - self.product.get_discounted_price) * self.quantity
class ShippingAddress(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('amz', 'AmzLayter'),
        ('viettin', 'Viettinbank'),
    ]
    STATUS_CHOICES = [
        ('processing', 'Đang xử lý'),
        ('shipping', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('cancelled', 'Đã hủy'),
    ]
    customer = models.ForeignKey(User,on_delete = models.SET_NULL,blank=True, null = True)
    order = models.ForeignKey(Order,on_delete = models.CASCADE,blank=True, null = True)
    country = CountryField(blank_label='Country/Region', null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    apartmentaddress = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=10, null=True)
    note = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    shipping_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='shipping')  # ✅ Trạng thái mới
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.address
# === Danh sách yêu thích và Lịch sử cá nhân === 
class WishList(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

class BrowsingHistory(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

# === Tìm kiếm và Đánh giá ===
class SearchLog(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.product.name, self.customer.username) 
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='review_images/', validators=[validate_image_extension]) 
# === Sự kiện giảm giá
class DiscountEvent(models.Model):
    name = models.CharField(max_length=200)
    products = models.ManyToManyField(Product, related_name='discounts')
    discount_percent = models.PositiveIntegerField(help_text="Nhập phần trăm giảm, ví dụ 10 cho 10%")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def __str__(self):
        return f"{self.name} - {self.discount_percent}%"    
    
class FreeShippingCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def __str__(self):
        return self.code
