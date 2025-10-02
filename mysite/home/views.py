from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from .models import *
import json
import traceback
from django.db.models import Avg, Q, Count, F, ExpressionWrapper, DecimalField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django_countries.fields import CountryField
from django import forms
from recommendation.utils import get_recommendations_for_user

class CountryForm(forms.Form):
      country = CountryField(blank_label='Country/Region').formfield()

# Create your views here.
def RegisternLogin(request):
    form = CreateUserForm()

    if request.user.is_authenticated:
        return redirect('home')  # Nếu đã đăng nhập thì không cần vào nữa

    show_login = False  # Mặc định hiển thị form đăng ký

    if request.method == "POST":
        if 'register' in request.POST:
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tạo tài khoản thành công. Bây giờ hãy đăng nhập.')
                show_login = True  # Sau khi đăng ký xong thì hiện login luôn
        elif 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Tài khoản hoặc mật khẩu không chính xác!')
                show_login = True  # Hiện lại login form

    context = {
        'form': form,
        'show_login': show_login,
    }
    return render(request, 'app/RegisnLogin.html', context)
def logoutdef(request):
    logout(request)
    return redirect('Login')


# View các trang
def Search(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    searched = request.GET.get('searched') or request.POST.get('searched', '')
    keys = Product.objects.filter(
        Q(name__icontains=searched) | Q(description__icontains=searched),
        is_active=True
    ) if searched else []

    categories = Category.objects.filter(is_active=True)    
    return render(request, 'app/search.html', {
        "searched": searched,
        "keys": keys,
        'cartItems': cartItems,
        'categories': categories
    })
from home.templatetags.price_filters import format_price
def search_suggestions(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=q, is_active=True)[:10]

    data = []
    for p in products:
        image_url = p.image.url if p.image else ''  # đảm bảo không lỗi .url
        old_price = float(p.price)
        new_price = float(p.get_discounted_price)

        data.append({
            'id': p.id,
            'name': p.name,
            'old_price': format_price(old_price) if new_price < old_price else None,
            'new_price': format_price(new_price),
            'image': image_url,
        })

    return JsonResponse(data, safe=False)

def home(request):
    # Giỏ hàng
    if request.user.is_authenticated:
        customer = request.user
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cartItems = 0

    # Danh mục
    categories = Category.objects.filter(is_active=True)

    # Lọc sản phẩm
    products_qs = Product.objects.filter(is_active=True)

    category_id = request.GET.get('category')
    if category_id:
        products_qs = products_qs.filter(categories__id=category_id)

    products_qs = products_qs[:1000]

    products = list(products_qs)
    for p in products:
        p.discounted_price = p.get_discounted_price

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products.sort(key=lambda x: x.discounted_price)
    elif sort == 'price_desc':
        products.sort(key=lambda x: x.discounted_price, reverse=True)
    elif sort == 'newest':
        products.sort(key=lambda x: x.date_created, reverse=True)
    elif sort == 'oldest':
        products.sort(key=lambda x: x.date_created)
    elif sort == 'discount_desc':
        products.sort(key=lambda x: x.price - x.discounted_price, reverse=True)
    elif sort == 'discount_asc':
        products.sort(key=lambda x: x.price - x.discounted_price)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    now = timezone.now()
    active_events = DiscountEvent.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('-start_date')
    main_event = active_events.first()

    # --- Gợi ý sản phẩm ---
    recommended_products = []
    if request.user.is_authenticated:
        top_item_ids = get_recommendations_for_user(request.user.id, top_n=6)
        recommended_products = Product.objects.filter(id__in=top_item_ids)

    context = {
        'products': page_obj.object_list,
        'cartItems': cartItems,
        'categories': categories,
        'page_obj': page_obj,
        'main_event': main_event,
        'recommended_products': recommended_products
    }
    return render(request, 'app/home.html', context)
def CategoryDetail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cartItems = 0

    categories = Category.objects.filter(is_active=True)
    active_categories = request.GET.get('cate_id')

    products = Product.objects.none()
    selected_category = None
    page_obj = None

    if active_categories:
        selected_category = get_object_or_404(Category, id=active_categories)
        products = Product.objects.filter(categories=active_categories, is_active=True)

        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'products': page_obj.object_list if page_obj else [],
        'active_categories': active_categories,
        'selected_category': selected_category,
        'cartItems': cartItems,
        'page_obj': page_obj
    }

    return render(request, 'app/category.html', context)
def Myshop(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    
    categories = Category.objects.filter(is_active = True)
    products = Product.objects.filter(is_active=True).order_by('id')

    paginator = Paginator(products, 12)  # Hiển thị 12 sản phẩm mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'products': page_obj.object_list,
                'cartItems':cartItems,
                'categories': categories,
                'page_obj': page_obj }
    return render(request, 'app/shop.html', context)

def ProductDetail(request):
    # --- Giỏ hàng ---
    if request.user.is_authenticated:
        customer = request.user
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        items = []
        cartItems = order['get_cart_items']

    # --- Lấy sản phẩm ---
    product = None
    quantity = 0
    id = request.GET.get('id', '')
    products = Product.objects.filter(is_active=True, id=id)

    if products.exists():
        product = products.first()

    # --- Danh sách yêu thích ---
    user_wishlist = []
    if request.user.is_authenticated:
        user_wishlist = [
            w.product for w in WishList.objects.filter(customer=request.user)
        ]

    # --- Lịch sử xem + số lượng trong giỏ ---
    if request.user.is_authenticated and product:
        order_item = order.orderitem_set.filter(product=product).first()
        if order_item:
            quantity = order_item.quantity

        history, created = BrowsingHistory.objects.get_or_create(
            customer=request.user,
            product=product,
            defaults={'viewed_at': now()}
        )
        if not created:
            history.viewed_at = now()
            history.save()

    # --- Đánh giá & sản phẩm liên quan ---
    if product:
        category_related = product.categories.all()
        related_products = Product.objects.filter(
            categories__in=category_related
        ).exclude(id=product.id).distinct()[:4]

        reviews = Review.objects.filter(product=product).order_by('-date_added')
    
        if reviews.exists():
            product.update_rating()  # Chỉ cập nhật nếu có ít nhất 1 đánh giá
            average_rating = product.average_rating
            review_count = product.rating_number
        else:
            average_rating = product.average_rating or 0
            review_count = product.rating_number or 0
    else:
        category_related = []
        related_products = []
        reviews = []
        review_count = 0
        average_rating = 0

    # --- Danh sách danh mục ---
    categories = Category.objects.filter(is_active=True)

    # --- Context để gửi qua template ---
    context = {
        'products': products,
        'cartItems': cartItems,
        'items': items,
        'quantity': quantity,
        'categories': categories,
        'review': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'related_products': related_products,
        'user_wishlist': user_wishlist,
    }

    return render(request, 'app/product.html', context)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

        for item in items:
            item.discounted_price = item.product.get_discounted_price
            item.total_discounted = item.quantity * item.discounted_price

        discounted_total = sum(item.total_discounted for item in items)
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
        discounted_total = 0
    categories = Category.objects.filter(is_active = True)
    context = {'items': items,
                'order': order,
                'cartItems':cartItems,
                'categories':categories,
                'discounted_total': discounted_total}
    return render(request,'app/cart.html',context)

def checkout(request):
    categories = Category.objects.filter(is_active=True)

    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to proceed to checkout.")
        return redirect('login')

    form = CountryForm()
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items

    order_success = False  # 👈 Cờ kiểm tra đơn hàng thành công

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        full_name = f"{first_name} {last_name}"
        address = request.POST.get('address', '')
        city = request.POST.get('city')
        state = request.POST.get('state', '')
        apartmentaddress = request.POST.get('apartmentaddress', '')
        phone = request.POST.get('phone')
        country = request.POST.get('country')
        payment_method = request.POST.get('payment_method')
        note = request.POST.get('note', '')

        # Kiểm tra các trường bắt buộc
        if not all([email, full_name, city, phone, country, payment_method]):
            messages.error(request, "❌ Please fill in all required fields.")
        else:
            # Lưu thông tin địa chỉ giao hàng
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=address,
                city=city,
                state=state,
                phone=phone,
                country=country,
                apartmentaddress=apartmentaddress,
                payment_method=payment_method,
                note=note
            )

            # Hoàn tất đơn hàng nếu chọn thanh toán Cash
            if payment_method == "cash":
                order.complete = True   
                order.note = note
                order.save()
                order_success = True  # ✅ Gắn cờ hiển thị thông báo

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'categories': categories,
        'country_form': form,
        'order_success': order_success if 'order_success' in locals() else False,
    }
    return render(request, 'app/checkout.html', context)

def account(request):
    if not request.user.is_authenticated:
        categories = Category.objects.filter(is_active=True)
        return render(request, 'app/account.html', {
            'cartItems': 0,
            'categories': categories,
            'orders': [],
            'wishlist': [],
            'user_wishlist': [],
            'shipping_addresses': [],
            'wishlist_page_obj': [],
            'order_page_obj': [],
            'history_page_obj': [],
            'profile': None,
        })

    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.select_related('product')
    cartItems = order.get_cart_items

    wishlist = WishList.objects.filter(customer=customer).select_related('product')
    user_wishlist = [w.product for w in wishlist]

    orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_Order')
    shipping_records = ShippingAddress.objects.filter(order__in=orders)
    shipping_map = {ship.order_id: ship for ship in shipping_records}

    # Gắn trạng thái giao hàng vào mỗi đơn
    for o in orders:
        shipping = shipping_map.get(o.id)
        o.shipping_status = shipping.shipping_status if shipping else 'unknown'
        o.shipping = shipping

    # Sắp xếp đơn: chưa giao hàng trước, trong nhóm thì theo ngày giảm dần
    sorted_orders = sorted(orders, key=lambda o: (o.shipping_status == 'delivered', -o.date_Order.toordinal()))

    # PHÂN TRANG đơn hàng
    order_page_number = request.GET.get('order_page')
    order_paginator = Paginator(sorted_orders, 2)
    order_page_obj = order_paginator.get_page(order_page_number)

    # PHÂN TRANG wishlist
    wishlist_page_number = request.GET.get('wishlist_page')
    wishlist_paginator = Paginator(wishlist, 4)
    wishlist_page_obj = wishlist_paginator.get_page(wishlist_page_number)

    # PHÂN TRANG lịch sử
    history = BrowsingHistory.objects.filter(customer=customer).select_related('product').order_by('-viewed_at')
    history_page_number = request.GET.get('history_page')
    history_paginator = Paginator(history, 4)
    history_page_obj = history_paginator.get_page(history_page_number)

    # Danh mục và profile
    categories = Category.objects.filter(is_active=True)
    profile = customer.profile

    # Lấy tất cả các sản phẩm trong wishlist và history (có thể thêm orders nếu muốn)
    all_products = set()

    if 'wishlist' in locals():
        all_products |= set([w.product for w in wishlist])

    if 'history' in locals():
        all_products |= set([h.product for h in history])

    # Tính rating cho từng sản phẩm
    for product in all_products:
        stats = Review.objects.filter(product=product).aggregate(
            avg=Avg('rating'),
            count=Count('id')
    )
    product.average_rating = round(stats['avg'] or 0, 1)
    product.rating_number = stats['count']
    context = {
        'profile': profile,
        'cartItems': cartItems,
        'categories': categories,
        'wishlist': wishlist,
        'user_wishlist': user_wishlist,
        'history': history,
        'orders': orders,
        'shipping_addresses': shipping_records,
        'wishlist_page_obj': wishlist_page_obj,
        'history_page_obj': history_page_obj,
        'order_page_obj': order_page_obj,
        'show_success_modal': True,
    }
    return render(request, 'app/account.html', context)

def order_detail(request, order_id):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    categories = Category.objects.filter(is_active=True)
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    shipping = ShippingAddress.objects.filter(order=order).first()
    items = order.orderitem_set.select_related('product')


     # ✅ Lấy danh sách đánh giá của người dùng cho các sản phẩm trong đơn hàng
    product_ids = [item.product.id for item in items]
    reviews = Review.objects.filter(customer=request.user, product_id__in=product_ids)

    # Tạo dict để tra nhanh: {product_id: review}
    review_map = {review.product.id: review for review in reviews}


    if request.method == 'POST':
        submitted_review = False  # 👈 Flag kiểm tra có đánh giá nào được gửi không
        for item in items:
            if item.product.id in review_map:
                continue
            rating = request.POST.get(f'rating_{item.product.id}')
            comment = request.POST.get(f'comment_{item.product.id}')
            images = request.FILES.getlist(f'images_{item.product.id}')
            if rating and comment:
                review = Review.objects.create(
                    customer=request.user,
                    product=item.product,
                    rating=rating,
                    comment=comment,
                )

                for img in images:
                     ReviewImage.objects.create(review=review, image=img)
                item.product.update_rating()
                submitted_review = True  # ✅ Đã có ít nhất 1 đánh giá

        if submitted_review:
            request.session['show_success_modal'] = True
            request.session['message'] = "Cảm ơn bạn đã đánh giá sản phẩm!"
        else:
            messages.warning(request, "Vui lòng điền đầy đủ đánh giá trước khi gửi.")

        return redirect(reverse('account') + '?history_page=1#myOrder')

    context = {
        'order': order,
        'shipping': shipping,
        'items': items,
        'cartItems':cartItems,
        'categories':categories,
    }
    return render(request, 'app/order_detail.html', context)

def confirm_received(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    shipping = ShippingAddress.objects.filter(order=order).first()

    if shipping:
        shipping.shipping_status = 'delivered'
        shipping.save()
        messages.success(request, "Cảm ơn bạn đã nhận sản phẩm! Hãy đánh giá sản phẩm để giúp chúng tôi biết trải nghiệm của bạn về sản phẩm nhé!.")
    else:
        messages.error(request, "Không tìm thấy thông tin giao hàng.")

    return redirect('order', order_id=order.id)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = customer, complete = False)
    orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)
    
    removed = False
    if action == 'add':
        orderItem.quantity += 1
    elif action == 'minus':
        orderItem.quantity -= 1

    if orderItem.quantity <= 0 or action == 'remove':
        orderItem.delete()
        removed = True
    else:
        orderItem.save()
    try:    
        return JsonResponse({
            'message': 'updated',
            'quantity': orderItem.quantity if not removed else 0,
            'itemTotal': float(orderItem.get_discounted_total) if not removed else 0,
            'savedAmount': float(orderItem.get_saved_amount) if not removed else 0,  # 👈 thêm dòng này
            'cartTotalItems': order.get_cart_items,
            'orderTotal': float(order.get_cart_total),  # nhớ () nếu là method
            'removed': removed,
            'productId': productId,
        }, safe=False)
    except Exception as e:
        traceback.print_exc()  # Ghi rõ lỗi trong terminal
        return JsonResponse({'error': str(e)}, status=500)


def updateProduct(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        productId = data.get('productId')
        quantity = int(data.get('quantity', 1))
        
        customer = request.user
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        orderItem.quantity += quantity
        orderItem.save()


        return JsonResponse({
            'message': 'updated',
            'quantity': orderItem.quantity,
            'itemTotal': float(orderItem.get_total),
            'cartTotalItems': order.get_cart_items,
            'orderTotal': float(order.get_cart_total),
            'productId': productId,
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        profile = user.profile  # đảm bảo đã có Profile

        # Lấy dữ liệu từ form
        first_name = request.POST.get('InputFirstName') or ''
        last_name = request.POST.get('InputLastName') or ''
        email = request.POST.get('email')
        username = request.POST.get('username')
        phone = request.POST.get('InputPhone')
        address = request.POST.get('InputAddress')

        # Cập nhật User
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        user.save()

        # Cập nhật Profile
        profile.phone = phone
        profile.address = address
          # ✅ Xử lý ảnh đại diện
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()

        messages.success(request, "Cập nhật thông tin thành công.")
        return redirect('account')  # đổi tên nếu bạn dùng khác

    return redirect('account') 
@login_required
def browsing_history_view(request):
    history = (
        BrowsingHistory.objects
        .filter(customer=request.user)
        .select_related('product')
        .order_by('-viewed_at')
    )

    # (Optional) Lọc trùng nếu cần: dùng distinct hoặc group
    # history = history.distinct('product')

    context = {
        'history': history,
    }
    return render(request, 'app/browsing_history.html', context) # fallback nếu không phải POST

@csrf_exempt
def add_to_wishlist(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = Product.objects.filter(id=product_id).first()

        if product:
            wishlist, created = WishList.objects.get_or_create(
                customer=request.user,
                product=product
            )

            if not created:
                wishlist.delete()
                return JsonResponse({'status': 'removed'})

            return JsonResponse({'status': 'added'})

    return JsonResponse({'status': 'error'})

