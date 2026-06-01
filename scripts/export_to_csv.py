# -*- coding: utf-8 -*-
import os
import sys
import csv
from datetime import datetime

# Cấu hình hệ thống đường dẫn backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(project_dir, 'backend') if os.path.basename(project_dir) != 'backend' else project_dir

sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tours.models import Tour, Booking, Payment, Review, Revenue
from users.models import User

# Thư mục đích gom duy nhất tất cả các file export
OUTPUT_DIR = os.path.join(backend_dir, 'exported_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_csv(filename, rows, fields):
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fields, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[OK] {filename}: {len(rows)} records")
    except Exception as e:
        print(f"[LOI] {filename}: {str(e)}")

print("🚀 START EXPORT DATA...")

# 1. users.csv
try:
    users_data = []
    for u in User.objects.all():
        role = 'Admin' if (u.is_superuser or u.is_staff) else (getattr(u, 'role', 'Customer').capitalize())
        users_data.append({
            'id': u.id, 'role': role, 'is_active': u.is_active,
            'date_joined': u.date_joined.strftime('%Y-%m-%d %H:%M:%S') if u.date_joined else ''
        })
    write_csv('users.csv', users_data, ['id', 'role', 'is_active', 'date_joined'])
except Exception as e: print(f"[LOI] Users: {e}")

# 2. tours.csv
try:
    tours_data = []
    for t in Tour.objects.select_related('creator').prefetch_related('categories').all():
        cats = ",".join([c.name for c in t.categories.all()])
        tours_data.append({
            'id': t.id, 'creator_id': t.creator_id, 'title': t.title, 'price': float(t.price) if t.price else 0.0,
            'departure_date': str(t.departure_date), 'slots': t.slots, 'status': t.status if t.status else 'Active',
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S') if t.created_at else '', 'category_names': cats if cats else None
        })
    write_csv('tours.csv', tours_data, ['id', 'creator_id', 'title', 'price', 'departure_date', 'slots', 'status', 'created_at', 'category_names'])
except Exception as e: print(f"[LOI] Tours: {e}")

# 3. bookings.csv
try:
    bookings_data = []
    for b in Booking.objects.all():
        bookings_data.append({
            'id': b.id, 'user_id': b.user_id, 'tour_id': b.tour_id, 'number_of_people': b.number_of_people,
            'total_price': float(b.total_price) if b.total_price else 0.0, 'booking_date': str(b.booking_date) if b.booking_date else '',
            'status': b.status if b.status else 'Pending', 'created_at': b.created_at.strftime('%Y-%m-%d %H:%M:%S') if b.created_at else ''
        })
    write_csv('bookings.csv', bookings_data, ['id', 'user_id', 'tour_id', 'number_of_people', 'total_price', 'booking_date', 'status', 'created_at'])
except Exception as e: print(f"[LOI] Bookings: {e}")

# 4. payments.csv
try:
    payments_data = []
    for p in Payment.objects.all():
        payments_data.append({
            'id': p.id, 'booking_id': p.booking_id, 'amount': float(p.amount) if p.amount else 0.0,
            'payment_method': p.payment_method if p.payment_method else 'VNPay', 'status': p.status if p.status else 'SUCCESS',
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else ''
        })
    write_csv('payments.csv', payments_data, ['id', 'booking_id', 'amount', 'payment_method', 'status', 'created_at'])
except Exception as e: print(f"[LOI] Payments: {e}")

# 5. revenues.csv
try:
    revenues_data = []
    for r in Revenue.objects.all():
        revenues_data.append({
            'id': r.id, 'payment_id': r.payment_id, 'creator_id': r.creator_id, 'total_amount': float(r.total_amount) if r.total_amount else 0.0,
            'creator_share': float(r.creator_share) if r.creator_share else 0.0, 'admin_share': float(r.admin_share) if r.admin_share else 0.0,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ''
        })
    write_csv('revenues.csv', revenues_data, ['id', 'payment_id', 'creator_id', 'total_amount', 'creator_share', 'admin_share', 'created_at'])
except Exception as e: print(f"[LOI] Revenues: {e}")

# 6. reviews.csv
try:
    reviews_data = []
    for r in Review.objects.all():
        reviews_data.append({
            'id': r.id, 'user_id': r.user_id, 'tour_id': r.tour_id, 'rating': r.rating,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ''
        })
    write_csv('reviews.csv', reviews_data, ['id', 'user_id', 'tour_id', 'rating', 'created_at'])
except Exception as e: print(f"[LOI] Reviews: {e}")

print("🎉 EXPORT DONE! Check directory: backend/exported_data/")