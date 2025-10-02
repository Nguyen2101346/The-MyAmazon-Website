from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
# ======================== 1. THÔNG TIN NGƯỜI DÙNG ========================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'avatar_preview', 'address']
    readonly_fields = ['avatar_preview']

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height:100px;border-radius:50%;"/>', obj.avatar.url)
        return "Không có ảnh"
    avatar_preview.short_description = "Ảnh đại diện"


# ======================== 2. PHÂN LOẠI SẢN PHẨM ========================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']

@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']  # 👈 thêm vào

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_value', 'is_active']
    search_fields = ['name']  # 👈 thêm vào

@admin.register(FinishType)
class FinishTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']  # 👈 thêm vào

@admin.register(AgeRange)
class AgeRangeAdmin(admin.ModelAdmin):
    list_display = ['description', 'is_active']
    search_fields = ['description']  # 👈 thêm vào


# ======================== 3. SẢN PHẨM ========================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'image_preview']
    readonly_fields = ['image_preview']    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'price', 'average_rating', 'rating_number', 'is_active', 'image_preview']
    readonly_fields = ['image_preview', 'average_rating', 'rating_number']

    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'image', 'image_preview', 'digital', 'description', 'details_json')
        }),
        ('Liên kết', {
            'fields': ('brand', 'manufacturer', 'categories', 'tags', 'color', 'finish_type', 'age_range')
        }),
        ('Thông tin đánh giá', {
            'fields': ('average_rating', 'rating_number')
        }),
    )

    filter_horizontal = ['categories', 'tags', 'color']
    autocomplete_fields = ['brand', 'manufacturer', 'finish_type', 'age_range']
    inlines = [ProductImageInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 150px;"/>', obj.image.url)
        return "Chưa có ảnh"
    image_preview.short_description = "Xem trước ảnh"

# ======================== 4. ĐƠN HÀNG & VẬN CHUYỂN ========================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'date_added']
    list_filter = ['order', 'product']
# === Inline: Hiển thị sản phẩm trong 1 đơn hàng ===
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'get_price']

    def get_price(self, obj):
        return f"{obj.get_discounted_total:,.0f} VND"
    get_price.short_description = "Tổng tiền"
# === Quản lý Order ===
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'order_items_count', 'get_cart_total']
    inlines = [OrderItemInline]

    def order_items_count(self, obj):
        count = obj.orderitem_set.count()
        url = (
            reverse("admin:home_orderitem_changelist") + f"?order__id__exact={obj.id}"
        )
        return format_html('<a href="{}">{} món</a>', url, count)
    order_items_count.short_description = "Số món đã mua"

    def get_cart_total(self, obj):
        return f"{obj.get_cart_total:,.0f} VND"
    get_cart_total.short_description = "Tổng tiền"

# === Quản lý ShippingAddress ===
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['address', 'customer', 'order_link']

    def order_link(self, obj):
        if obj.order:
            url = reverse("admin:home_order_change", args=[obj.order.id])
            return format_html('<a href="{}">Xem đơn hàng #{}</a>', url, obj.order.id)
        return "-"
    order_link.short_description = "Đơn hàng liên kết"  


# ======================== 5. ĐÁNH GIÁ - LỊCH SỬ - WISHLIST ========================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'rating', 'date_added']
    list_filter = ['rating']

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ['review', 'image']

@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'date_added']

@admin.register(BrowsingHistory)
class BrowsingHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'viewed_at']

@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ['customer', 'query', 'date_added']


# ======================== 6. GIẢM GIÁ & FREESHIP ========================
@admin.register(DiscountEvent)
class DiscountEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_percent', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    filter_horizontal = ['products']

@admin.register(FreeShippingCode)
class FreeShippingCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'min_order_amount', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
