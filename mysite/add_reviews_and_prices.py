# add_reviews_and_prices.py (đặt cùng thư mục với manage.py)
import os
import django
import random

# ✅ Cấu hình môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from django.contrib.auth.models import User
from home.models import Product, Review

# ✅ Lấy user đã tạo
usernames = ['koiking1', 'koiking2', 'koiking3']
users = []
for name in usernames:
    try:
        users.append(User.objects.get(username=name))
    except User.DoesNotExist:
        print(f"[⚠️] Không tìm thấy user '{name}'.")

created_reviews = 0
updated_prices = 0

products = Product.objects.all()

for product in products:
    # ✅ Tạo review nếu chưa có
    if product.average_rating and product.review_set.count() == 0 and len(users) == 3:
        avg = product.average_rating
        base = int(avg)
        total = round(avg * 3)
        ratings = [base, base, base]
        for i in range(total - base * 3):
            ratings[i] += 1

        comments = [
            "Sản phẩm tuyệt vời và đúng như mô tả.",
            "Rất hài lòng với chất lượng và dịch vụ.",
            "Giao hàng nhanh và đóng gói cẩn thận."
        ]

        for i in range(3):
            Review.objects.create(
                customer=users[i],
                product=product,
                rating=ratings[i],
                comment=comments[i]
            )
            created_reviews += 1

    # ✅ Cập nhật giá nếu = 0
    if product.price == 0:
        product.price = random.randint(300, 3000)
        product.save()
        updated_prices += 1

# ✅ Tổng kết
print(f"✅ Đã tạo {created_reviews} review.")
print(f"💵 Đã cập nhật giá cho {updated_prices} sản phẩm.")
