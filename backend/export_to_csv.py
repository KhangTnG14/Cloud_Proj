import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tours.models import Tour, Booking, Payment, Review
from users.models import User

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'exported_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_csv(filename, rows, fields):
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[OK] {filename}: {len(rows)} records")
        return len(rows)
    except Exception as e:
        print(f"[LOI] Loi khi ghi file {filename}: {str(e)}")
        return 0

export_log = {}
print("[Pipeline] Dang trich xuat du lieu...\n" + "="*50)

# --- USERS ---
try:
    users_data = []
    for u in User.objects.all():
        if u.is_superuser or u.is_staff:
            role = 'admin'
        elif u.role == 'PROVIDER':
            role = 'provider'
        else:
            role = 'customer'
        if u.is_superuser or u.is_staff:
            user_status = 'Active'
        elif u.is_active:
            user_status = 'Active'
        else:
            user_status = 'Banned'
        users_data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email or '',
            'role': role,
            'status': user_status,
            'is_staff': u.is_staff,
            'is_superuser': u.is_superuser,
            'date_joined': str(u.date_joined),
        })
    export_log['users'] = write_csv('users.csv', users_data,
        ['id', 'username', 'email', 'role', 'status',
         'is_staff', 'is_superuser', 'date_joined'])
except Exception as e:
    print(f"[LOI] Bang Users: {e}")
    export_log['users'] = 0

# --- TOURS ---
try:
    tours_data = []
    for t in Tour.objects.select_related('creator').prefetch_related('categories').all():
        cats = ",".join([c.name for c in t.categories.all()])
        tours_data.append({
            'id': t.id,
            'creator_id': t.creator_id,
            'creator_name': t.creator.username if t.creator else '',
            'title': t.title,
            'address': t.address or '',
            'price': t.price,
            'departure_date': str(t.departure_date),
            'slots': t.slots,
            'status': t.status,
            'created_at': str(t.created_at),
            'category_names': cats,
        })
    export_log['tours'] = write_csv('tours.csv', tours_data,
        ['id', 'creator_id', 'creator_name', 'title', 'address',
         'price', 'departure_date', 'slots', 'status',
         'created_at', 'category_names'])
except Exception as e:
    print(f"[LOI] Bang Tours: {e}")
    export_log['tours'] = 0

# --- BOOKINGS ---
try:
    bookings_data = []
    for b in Booking.objects.select_related('user', 'tour').all():
        bookings_data.append({
            'id': b.id,
            'user_id': b.user_id,
            'username': b.user.username if b.user else '',
            'tour_id': b.tour_id,
            'tour_title': b.tour.title if b.tour else '',
            'number_of_people': b.number_of_people,
            'total_price': b.total_price,
            'booking_date': str(b.booking_date),
            'status': b.status,
            'created_at': str(b.created_at),
        })
    export_log['bookings'] = write_csv('bookings.csv', bookings_data,
        ['id', 'user_id', 'username', 'tour_id', 'tour_title',
         'number_of_people', 'total_price', 'booking_date',
         'status', 'created_at'])
except Exception as e:
    print(f"[LOI] Bang Bookings: {e}")
    export_log['bookings'] = 0

# --- PAYMENTS ---
try:
    payments_data = []
    for p in Payment.objects.select_related(
        'booking', 'booking__user', 'booking__tour'
    ).all():
        payments_data.append({
            'id': p.id,
            'booking_id': p.booking_id,
            'username': p.booking.user.username if p.booking and p.booking.user else '',
            'tour_title': p.booking.tour.title if p.booking and p.booking.tour else '',
            'amount': p.amount,
            'payment_method': p.payment_method or '',
            'status': p.status,
            'transaction_code': p.transaction_code or '',
            'created_at': str(p.created_at),
        })
    export_log['payments'] = write_csv('payments.csv', payments_data,
        ['id', 'booking_id', 'username', 'tour_title',
         'amount', 'payment_method', 'status',
         'transaction_code', 'created_at'])
except Exception as e:
    print(f"[LOI] Bang Payments: {e}")
    export_log['payments'] = 0

# --- REVIEWS ---
try:
    reviews_data = []
    for r in Review.objects.select_related('user', 'tour').all():
        reviews_data.append({
            'id': r.id,
            'user_id': r.user_id,
            'username': r.user.username if r.user else '',
            'tour_id': r.tour_id,
            'tour_title': r.tour.title if r.tour else '',
            'rating': r.rating,
            'content': r.content or '',
            'created_at': str(r.created_at),
        })
    export_log['reviews'] = write_csv('reviews.csv', reviews_data,
        ['id', 'user_id', 'username', 'tour_id', 'tour_title',
         'rating', 'content', 'created_at'])
except Exception as e:
    print(f"[LOI] Bang Reviews: {e}")
    export_log['reviews'] = 0

print("\n" + "="*50)
print("[XONG] Export hoan tat!")
for table, count in export_log.items():
    print(f"   {table}: {count} records")