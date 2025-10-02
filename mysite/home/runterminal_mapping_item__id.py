import pandas as pd
import re
import unicodedata
from django.db import IntegrityError
from home.models import Product, ProductMapping

# === Hàm chuẩn hoá tên (normalize) ===
def normalize_name(name: str) -> str:
    """Chuẩn hoá tên sản phẩm: bỏ dấu, ký tự đặc biệt, viết thường."""
    if not name:
        return ""
    name = name.lower()
    name = unicodedata.normalize('NFD', name)
    name = name.encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# === Đọc file dataset CSV ===
csv_path = r"D:/My Study/2026/Đồ án/Đồ án Cuối/Dataset/amazon_review_100k_clear.csv"
df = pd.read_csv(csv_path, encoding="ISO-8859-1")

# === Lookup {normalized_name: product} để tăng tốc ===
product_lookup = {
    normalize_name(p.name): p
    for p in Product.objects.all()
}

print(f"🔎 Tổng số product trong DB: {len(product_lookup)}")
print(f"📄 Tổng số record trong file CSV: {len(df)}")

created, updated, skipped = 0, 0, 0

# === Xử lý từng dòng dataset ===
for idx, row in df.iterrows():
    item_id = str(row.get("item_id", "")).strip()
    title = str(row.get("title", "")).strip()

    if not item_id or not title:
        skipped += 1
        continue

    normalized_title = normalize_name(title)
    product = product_lookup.get(normalized_title)

    if not product:
        skipped += 1
        continue

    try:
        obj, is_created = ProductMapping.objects.update_or_create(
            model_item_id=item_id,
            defaults={"product": product}
        )
        if is_created:
            created += 1
        else:
            updated += 1
    except IntegrityError:
        skipped += 1

    # Log mỗi 500 record để dễ theo dõi
    if idx % 500 == 0 and idx > 0:
        print(f"➡ Đã xử lý {idx}/{len(df)} record...")

# === Kết quả cuối cùng ===
print("==== ✅ DONE ====")
print(f"🆕 Mapping created: {created}")
print(f"♻ Mapping updated: {updated}")
print(f"⏩ Skipped: {skipped}")
