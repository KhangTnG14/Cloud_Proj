# -*- coding: utf-8 -*-
import os
import sys

# Ép hệ thống xuất text chuẩn hóa tránh lỗi hiển thị trên Terminal Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tours.models import Tour, Booking, Payment, Review, Revenue
from users.models import User

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'exported_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_csv(filename, rows, fields):
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        # 🔥 ĐÃ SỬA: Đổi từ 'utf-8' thành 'utf-8-sig' để tự động chèn ký hiệu BOM nhận diện tiếng Việt trên Excel Windows
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            # Ràng buộc dấu nháy kép cho các trường text chứa dấu phẩy như title, category_names
            writer = csv.DictWriter(f, fieldnames=fields, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[OK] {filename}: {len(rows)} records")
        return len(rows)
    except Exception as e:
        print(f"[LOI] Loi khi ghi file {filename}: {str(e)}")
        return 0

export_log = {}
print("[Pipeline] Bat dau trich xuat 6 file CSV bao mat theo dung Leader Schema...\n" + "="*50)

# --- 1.1. users.csv (Đã ẩn danh PII: Loại bỏ password, email, phone, username, avatar) ---
try:
    users_data = []
    for u in User.objects.all():
        if u.is_superuser or u.is_staff:
            role = 'Admin'
        elif getattr(u, 'role', '') == 'PROVIDER':
            role = 'Provider'
        else:
            role = 'Customer'
            
        users_data.append({
            'id': u.id,
            'role': role,
            'is_active': u.is_active,
            'date_joined': u.date_joined.strftime('%Y-%m-%d %H:%M:%S') if u.date_joined else '',
        })
    export_log['users'] = write_csv('users.csv', users_data, ['id', 'role', 'is_active', 'date_joined'])
except Exception as e:
    print(f"[LOI] Bang Users: {e}")
    export_log['users'] = 0

# --- 1.2. tours.csv ---
try:
    tours_data = []
    for t in Tour.objects.select_related('creator').prefetch_related('categories').all():
        cats = ",".join([c.name for c in t.categories.all()])
        tours_data.append({
            'id': t.id,
            'creator_id': t.creator_id,
            'title': t.title,
            'price': float(t.price) if t.price else 0.0, # Ép kiểu về DoubleType cho Spark
            'departure_date': str(t.departure_date),
            'slots': t.slots,
            'status': t.status if t.status else 'Active',
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S') if t.created_at else '',
            'category_names': cats if cats else None,
        })
    export_log['tours'] = write_csv('tours.csv', tours_data, 
        ['id', 'creator_id', 'title', 'price', 'departure_date', 'slots', 'status', 'created_at', 'category_names'])
except Exception as e:
    print(f"[LOI] Bang Tours: {e}")
    export_log['tours'] = 0

# --- 1.3. bookings.csv ---
try:
    bookings_data = []
    for b in Booking.objects.all():
        bookings_data.append({
            'id': b.id,
            'user_id': b.user_id,
            'tour_id': b.tour_id,
            'number_of_people': b.number_of_people,
            'total_price': float(b.total_price) if b.total_price else 0.0,
            'booking_date': str(b.booking_date) if b.booking_date else '',
            'status': b.status if b.status else 'Pending',
            'created_at': b.created_at.strftime('%Y-%m-%d %H:%M:%S') if b.created_at else '',
        })
    export_log['bookings'] = write_csv('bookings.csv', bookings_data,
        ['id', 'user_id', 'tour_id', 'number_of_people', 'total_price', 'booking_date', 'status', 'created_at'])
except Exception as e:
    print(f"[LOI] Bang Bookings: {e}")
    export_log['bookings'] = 0

# --- 1.4. payments.csv ---
try:
    payments_data = []
    for p in Payment.objects.all():
        payments_data.append({
            'id': p.id,
            'booking_id': p.booking_id,
            'amount': float(p.amount) if p.amount else 0.0,
            'payment_method': p.payment_method if p.payment_method else 'VNPay',
            'status': p.status if p.status else 'Success',
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else '',
        })
    export_log['payments'] = write_csv('payments.csv', payments_data,
        ['id', 'booking_id', 'amount', 'payment_method', 'status', 'created_at'])
except Exception as e:
    print(f"[LOI] Bang Payments: {e}")
    export_log['payments'] = 0

# --- 1.5. revenues.csv ---
try:
    revenues_data = []
    for r in Revenue.objects.all():
        revenues_data.append({
            'id': r.id,
            'payment_id': r.payment_id,
            'creator_id': r.creator_id,
            'total_amount': float(r.total_amount) if r.total_amount else 0.0,
            'creator_share': float(r.creator_share) if r.creator_share else 0.0,
            'admin_share': float(r.admin_share) if r.admin_share else 0.0,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else '',
        })
    export_log['revenues'] = write_csv('revenues.csv', revenues_data,
        ['id', 'payment_id', 'creator_id', 'total_amount', 'creator_share', 'admin_share', 'created_at'])
except Exception as e:
    print(f"[LOI] Bang Revenues: {e}")
    export_log['revenues'] = 0

# --- 1.6. reviews.csv (Đã ẩn danh bảo mật: Loại bỏ hoàn toàn trường văn bản dài content) ---
try:
    reviews_data = []
    for r in Review.objects.all():
        reviews_data.append({
            'id': r.id,
            'user_id': r.user_id,
            'tour_id': r.tour_id,
            'rating': r.rating,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else '',
        })
    export_log['reviews'] = write_csv('reviews.csv', reviews_data,
        ['id', 'user_id', 'tour_id', 'rating', 'created_at'])
except Exception as e:
    print(f"[LOI] Bang Reviews: {e}")
    export_log['reviews'] = 0

print("\n" + "="*50)
print("[XONG] Hoan tat quy trinh Pipeline xuat 6 file thô (Bronze Layer)!")
for table, count in export_log.items():
    print(f"   {table}.csv: {count} records")