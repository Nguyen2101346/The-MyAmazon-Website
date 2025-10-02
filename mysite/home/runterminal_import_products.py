import pandas as pd
import ast
from django.db import IntegrityError, InterfaceError, transaction
from home.models import Product, Brand, Manufacturer, Color, FinishType, Category

# === Làm sạch chuỗi ===
def clean_str(value):
    try:
        s = str(value).strip()
        if not s or s.lower() in ["", "nan", "null", "none"]:
            return None
        return s
    except Exception:
        return None

# === Đọc file CSV ===
df = pd.read_csv('D:/My Study/2026/Đồ án/Đồ án Cuối/Dataset/amazon_review_100k_clear.csv')
df = df.drop_duplicates(subset='item_id')

created = 0
updated = 0
skipped = 0

for _, row in df.iterrows():
    try:
        title = clean_str(row.get('title'))
        if not title:
            skipped += 1
            continue

        details_raw = row.get('details')
        if pd.isnull(details_raw) or not str(details_raw).strip().startswith("{"):
            skipped += 1
            continue

        try:
            details = ast.literal_eval(details_raw)
        except Exception:
            skipped += 1
            continue

        # === Trích dữ liệu ===
        brand_name = clean_str(details.get('Brand'))
        manufacturer_name = clean_str(details.get('Manufacturer'))
        color_raw = clean_str(details.get('Color'))
        finish_type_raw = clean_str(details.get('Finish Type'))

        # === Tạo hoặc lấy liên kết ===
        brand = None
        if brand_name:
            try:
                brand = Brand.objects.get(name=brand_name)
            except Brand.DoesNotExist:
                try:
                    brand = Brand.objects.create(name=brand_name)
                except IntegrityError:
                    brand = Brand.objects.get(name=brand_name)

        manufacturer = None
        if manufacturer_name:
            try:
                manufacturer = Manufacturer.objects.get(name=manufacturer_name)
            except Manufacturer.DoesNotExist:
                try:
                    manufacturer = Manufacturer.objects.create(name=manufacturer_name)
                except IntegrityError:
                    manufacturer = Manufacturer.objects.get(name=manufacturer_name)

        finish_type = None
        if finish_type_raw:
            try:
                finish_type = FinishType.objects.get(name=finish_type_raw)
            except FinishType.DoesNotExist:
                try:
                    finish_type = FinishType.objects.create(name=finish_type_raw)
                except IntegrityError:
                    finish_type = FinishType.objects.get(name=finish_type_raw)

        # === Kiểm tra sản phẩm đã tồn tại ===
        product = Product.objects.filter(name=title).first()

        if not product:
            product = Product.objects.create(
                name=title,
                price=0,
                description='',
                details_json=details,
                brand=brand,
                manufacturer=manufacturer,
                finish_type=finish_type
            )
            created += 1
        else:
            changed = False
            if not product.brand and brand:
                product.brand = brand
                changed = True
            if not product.manufacturer and manufacturer:
                product.manufacturer = manufacturer
                changed = True
            if not product.finish_type and finish_type:
                product.finish_type = finish_type
                changed = True
            if changed:
                product.save()
                updated += 1

       # === Gắn tất cả màu nếu có (bỏ qua trùng lặp hoặc lỗi) ===
        if color_raw:
            color_names = [c.strip() for c in color_raw.split(',') if c.strip()]
            for color_name in color_names:
                color_obj = None
                try:
                    color_obj = Color.objects.get(name=color_name)
                except Color.DoesNotExist:
                    try:
                        color_obj = Color.objects.create(name=color_name)
                    except Exception as e:
                        print(f"[⚠️] Không thể tạo màu '{color_name}' (item_id {row.get('item_id')}): {type(e).__name__} - {e}")
                        continue  # bỏ qua màu lỗi

                # Chỉ add nếu product chưa có
                if color_obj:
                    try:
                        if not product.color.filter(pk=color_obj.pk).exists():
                            product.color.add(color_obj)
                    except Exception as e:
                        print(f"[⚠️] Không thể gán màu '{color_name}' cho sản phẩm (item_id {row.get('item_id')}): {type(e).__name__} - {e}")
                        continue

        # === Gắn Category từ Finish Type ===
        if finish_type_raw:
            for cat_name in [c.strip() for c in finish_type_raw.split(',') if c.strip()]:
                try:
                    category = Category.objects.get(name=cat_name)
                except Category.DoesNotExist:
                    try:
                        category = Category.objects.create(name=cat_name)
                    except IntegrityError:
                        category = Category.objects.get(name=cat_name)
                product.categories.add(category)

    except IntegrityError as e:
        print(f"[⛔] item_id {row.get('item_id')}: IntegrityError - {e}")
    except InterfaceError as e:
        transaction.rollback()
        print(f"[❌] item_id {row.get('item_id')}: InterfaceError - {e}")
        skipped += 1
    except Exception as e:
        print(f"[❌] item_id {row.get('item_id')}: {type(e).__name__} - {e}")
        skipped += 1

# === Tổng kết ===
print("\n🎯 KẾT THÚC:")
print(f"[✅] Đã tạo mới      : {created}")
print(f"[♻️] Đã cập nhật     : {updated}")
print(f"[⏩] Bỏ qua           : {skipped}")

