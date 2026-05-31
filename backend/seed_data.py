# -*- coding: utf-8 -*-
import os
import sys

# 🔥 ĐẶT BIẾN MÔI TRƯỜNG CHẶN SIGNAL NGAY ĐẦU TIÊN TRƯỚC KHI SETUP DJANGO
os.environ['SKIP_SIGNALS'] = 'yes'

import io
import time
import random
import subprocess
from decimal import Decimal
from datetime import date, timedelta, datetime

# Ép hệ thống xuất text chuẩn hóa định dạng UTF-8 tránh lỗi hiển thị trên Terminal Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── 1. KHỞI TẠO DJANGO MÔI TRƯỜNG ───────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import django
django.setup()

from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Khai báo Models hệ thống
from tours.models import Tour, Booking, Payment, Review, Category, Revenue
from users.models import User

print("="*60)
print("🚀 [SYSTEM] Kích hoạt cờ SKIP_SIGNALS = yes thành công.")
print("    ↳ Chặn toàn bộ Signal ngầm để tối ưu hóa nạp dữ liệu lớn.")
print("="*60)

# ── 2. KHỞI TẠO CÁC HÀM TRỢ GIÚP (HELPER FUNCTIONS) ───────────────────
print("Bắt đầu tạo dữ liệu giả...")

def random_date(start_date, end_date):
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    if start_date >= end_date:
        start_date = end_date - timedelta(days=1)
    delta = end_date - start_date
    return start_date + timedelta(days=random.randint(0, delta.days))

def random_datetime(start_date, end_date):
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    if start_date >= end_date:
        start_date = end_date - timedelta(days=1)
    d = random_date(start_date, end_date)
    return timezone.make_aware(datetime(
        d.year, d.month, d.day,
        random.randint(0, 23),
        random.randint(0, 59),
        random.randint(0, 59)
    ))

def fake_phone():
    prefix = random.choice([
        '090', '091', '092', '093', '094',
        '096', '097', '098', '032', '033',
        '034', '035', '036', '037', '038', '039'
    ])
    return prefix + ''.join([str(random.randint(0, 9)) for _ in range(7)])

START_DATE = date(2025, 1, 1)
END_DATE   = date(2027, 5, 31)

print("⏳ Đang chuẩn hóa mã hóa mật khẩu hệ thống...")
PRE_HASHED_PASSWORD = make_password('Test@123')

# ── 3. TIẾN TRÌNH NẠP DỮ LIỆU MẪU (SEED DATA GENERATION) ──────────────

# --- CATEGORIES ---
category_names = ['Biển', 'Núi', 'Văn hóa', 'Sang trọng', 'Mạo hiểm', 'Nghỉ dưỡng']
categories = []
for name in category_names:
    cat, _ = Category.objects.get_or_create(name=name)
    categories.append(cat)
print(f"[OK] {len(categories)} categories")

# --- PROVIDERS ---
print("⏳ Đang xử lý cấp tốc danh sách Providers...")
providers_to_create = []

for i in range(100):
    username = f'provider_{i+1}'
    joined   = random_datetime(START_DATE, END_DATE)
    phone    = fake_phone()

    user_queryset = User.objects.filter(username=username)
    if not user_queryset.exists():
        providers_to_create.append(User(
            username=username,
            email=f'provider{i+1}@tourgo.com',
            password=PRE_HASHED_PASSWORD,
            role='PROVIDER',
            is_active=True,
            date_joined=joined,
            phone=phone
        ))
    else:
        p = user_queryset.first()
        User.objects.filter(id=p.id).update(phone=phone, date_joined=joined, password=PRE_HASHED_PASSWORD)

if providers_to_create:
    User.objects.bulk_create(providers_to_create)

providers = list(User.objects.filter(role='PROVIDER'))
print(f"[OK] Đã nạp xong {len(providers)} providers!")

# --- CUSTOMERS ---
print("⏳ Đang xử lý cấp tốc danh sách Customers...")
customers_to_create = []

for i in range(100):
    username = f'customer_{i+1}'
    joined   = random_datetime(START_DATE, END_DATE)
    phone    = fake_phone()

    user_queryset = User.objects.filter(username=username)
    if not user_queryset.exists():
        customers_to_create.append(User(
            username=username,
            email=f'customer{i+1}@gmail.com',
            password=PRE_HASHED_PASSWORD,
            role='CUSTOMER',
            is_active=True,
            date_joined=joined,
            phone=phone
        ))
    else:
        u = user_queryset.first()
        User.objects.filter(id=u.id).update(phone=phone, date_joined=joined, password=PRE_HASHED_PASSWORD)

if customers_to_create:
    User.objects.bulk_create(customers_to_create)

customers = list(User.objects.filter(role='CUSTOMER'))
print(f"[OK] Đã nạp xong {len(customers)} customers!")

# --- TOURS ---
destinations = [
    ('Đà Lạt',          11.9404, 108.4583),
    ('Đà Nẵng',         16.0544, 108.2022),
    ('Phú Quốc',        10.2899, 103.9840),
    ('Nha Trang',       12.2451, 109.1943),
    ('Hà Nội',          21.0285, 105.8542),
    ('Hội An',          15.8800, 108.3380),
    ('Vũng Tàu',        10.3461, 107.0843),
    ('Sapa',            22.3364, 103.8438),
    ('Hạ Long',         20.9101, 107.1839),
    ('Huế',             16.4637, 107.5909),
    ('Cần Thơ',         10.0452, 105.7469),
    ('Mũi Né',          10.9333, 108.2833),
    ('Quy Nhơn',        13.7830, 109.2197),
    ('Tây Ninh',        11.3100, 106.0983),
    ('Buôn Ma Thuột',   12.6667, 108.0500),
    ('Pleiku',          13.9833, 108.0000),
    ('Kon Tum',         14.3544, 107.9922),
    ('Quảng Ninh',      21.0064, 107.2925),
    ('Ninh Bình',       20.2506, 105.9745),
    ('Biên Hòa',        10.9574, 106.8426),
]

tour_prefixes = [
    'Khám phá', 'Tham quan', 'Nghỉ dưỡng', 'Phiêu lưu',
    'Du lịch', 'Hành trình', 'Trải nghiệm', 'Tour cao cấp'
]
tour_suffixes = ['2N1Đ', '3N2Đ', '4N3Đ', '5N4Đ', '1 ngày', 'cuối tuần']
prices = [
    150000, 250000, 350000, 500000, 750000,
    1000000, 1500000, 2000000, 3000000, 5000000,
    7000000, 10000000
]

tours = []
print("⏳ Đang khởi tạo 200 Tours...")
for i in range(200):
    dest      = random.choice(destinations)
    provider  = random.choice(providers)
    created   = random_datetime(START_DATE, END_DATE)
    departure = created.date() + timedelta(days=random.randint(7, 180))
    price     = Decimal(random.choice(prices))
    prefix    = random.choice(tour_prefixes)
    suffix    = random.choice(tour_suffixes)

    # 🔥 ĐÃ TỐI ƯU: Gán trực tiếp created_at vào câu lệnh create
    tour = Tour.objects.create(
        title=f'{prefix} {dest[0]} {suffix}',
        address=dest[0],
        price=price,
        departure_date=departure,
        slots=random.randint(5, 50),
        latitude=dest[1]  + random.uniform(-0.05, 0.05),
        longitude=dest[2] + random.uniform(-0.05, 0.05),
        description=(
            f'Tour {prefix.lower()} {dest[0]} {suffix}. '
            f'Chương trình tham quan các địa danh nổi tiếng. '
            f'Bao gồm ăn uống, di chuyển và hướng dẫn viên.'
        ),
        image_url='https://images.unsplash.com/photo-1507525428034-b723cf961d3e',
        status=random.choice(['approved', 'approved', 'approved', 'pending']),
        creator=provider,
        created_at=created
    )
    
    tour.categories.set(random.sample(categories, random.randint(1, 3)))
    tours.append(tour)
print(f"[OK] {len(tours)} tours")

# --- BOOKINGS + PAYMENTS ---
statuses        = ['confirmed', 'confirmed', 'confirmed', 'pending', 'cancelled']
payment_methods = ['VNPAY', 'CASH', 'BANK_TRANSFER']
booking_count   = 0
payment_count   = 0

print("⏳ Đang khởi tạo 500 Bookings & Payments...")
for i in range(500):
    customer     = random.choice(customers)
    tour         = random.choice(tours)
    num_people   = random.randint(1, 5)
    status       = random.choice(statuses)
    book_created = random_datetime(START_DATE, min(END_DATE, tour.departure_date))

    try:
        # 🔥 ĐÃ TỐI ƯU: Gán trực tiếp created_at vào Booking
        booking = Booking.objects.create(
            user=customer,
            tour=tour,
            number_of_people=num_people,
            total_price=tour.price * num_people,
            booking_date=tour.departure_date,
            status=status,
            created_at=book_created
        )
        booking_count += 1

        if status == 'confirmed':
            transaction_code = f'TXN{booking.id}{int(time.time() * 1000)}{random.randint(100, 999)}'
            vnp_txn_ref      = f'VNP{booking.id}{int(time.time() * 1000)}{random.randint(100, 999)}'

            # 🔥 ĐÃ TỐI ƯU: Gán trực tiếp created_at vào Payment, loại bỏ hoàn toàn lệnh .update()
            p = Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                payment_method=random.choice(payment_methods),
                status='SUCCESS',
                transaction_code=transaction_code,
                vnp_txn_ref=vnp_txn_ref,
                created_at=book_created
            )
            payment_count += 1

    except Exception as e:
        print(f'[SKIP] Booking {i+1} loi: {e}')
        continue

print(f"[OK] {booking_count} bookings")
print(f"[OK] {payment_count} payments")

# --- REVENUES ---
print("⏳ Đang tính toán đồng bộ hóa bảng phân hệ Doanh thu (Revenue)...")
revenue_count = 0
success_payments = Payment.objects.filter(status='SUCCESS').select_related('booking__tour__creator')

for payment in success_payments:
    if not Revenue.objects.filter(payment_id=payment.id).exists():
        try:
            total_amount = payment.amount
            creator_share = total_amount * Decimal('0.90')
            admin_share   = total_amount * Decimal('0.10')
            creator       = payment.booking.tour.creator

            # 🔥 ĐÃ TỐI ƯU: Gán trực tiếp created_at vào Revenue
            rev = Revenue.objects.create(
                payment_id=payment.id,
                creator_id=creator.id,
                total_amount=total_amount,
                creator_share=creator_share,
                admin_share=admin_share,
                created_at=payment.created_at
            )
            revenue_count += 1
        except Exception as rev_err:
            continue

print(f"[OK] Đã xử lý và bổ sung {revenue_count} bản ghi doanh thu mới vào bảng Revenue!")

# --- REVIEWS ---
review_contents = [
    'Tour rất tuyệt vời, sẽ quay lại!',
    'Hướng dẫn viên nhiệt tình, chu đáo.',
    'Phong cảnh đẹp, dịch vụ tốt.',
    'Rất hài lòng với chuyến đi này.',
    'Giá cả hợp lý, chất lượng tốt.',
    'Trải nghiệm khó quên.',
    'Mọi thứ đều rất chu đáo.',
    'Tour chuẩn, đúng giờ giấc.',
    'Dịch vụ ăn uống ngon.',
    'Khách sạn đẹp, sạch sẽ.',
]

review_count = 0
confirmed_bookings = list(
    Booking.objects.filter(status='confirmed').select_related('user', 'tour')
)
random.shuffle(confirmed_bookings)

print("⏳ Đang khởi tạo các Reviews chọn lọc...")
for b in confirmed_bookings[:150]:
    if not Review.objects.filter(user=b.user, tour=b.tour).exists():
        try:
            review_date = random_datetime(
                b.tour.departure_date,
                min(b.tour.departure_date + timedelta(days=30), END_DATE)
            )
            # 🔥 ĐÃ TỐI ƯU: Gán trực tiếp created_at vào Review
            r = Review.objects.create(
                user=b.user,
                tour=b.tour,
                rating=random.randint(3, 5),
                content=random.choice(review_contents),
                created_at=review_date
            )
            review_count += 1
        except Exception as e:
            print(f'[SKIP] Review loi: {e}')
            continue

print(f"[OK] {review_count} reviews")

# ── 4. GỌI ĐỒNG BỘ QUA SUBPROCESS ĐÚNG 1 LẦN DUY NHẤT Ở CUỐI ──────
if 'SKIP_SIGNALS' in os.environ:
    del os.environ['SKIP_SIGNALS']

print("\n" + "="*50)
print("📊 [PIPELINE] Khởi chạy tiến trình xuất dữ liệu đồng bộ sang exported_data/...")
try:
    subprocess.run([sys.executable, "export_to_csv.py"], check=True)
except Exception as csv_error:
    print(f"⚠️ [CẢNH BÁO] Không thể kích hoạt tự động file export_to_csv.py: {csv_error}")

print("\n" + "="*50)
print("[XONG] Quy trình nạp và xuất dữ liệu hoàn tất siêu tốc và hoàn hảo!")
print("="*50)