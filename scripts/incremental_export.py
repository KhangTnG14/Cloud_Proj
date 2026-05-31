# -*- coding: utf-8 -*-
import os
import sys
import io
import csv
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Fix đường dẫn khi chạy từ scripts/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(project_dir, 'backend')
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# Load .env từ thư mục gốc project
from dotenv import load_dotenv
load_dotenv(os.path.join(project_dir, '.env'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import boto3
from tours.models import Tour, Booking, Payment, Review
from users.models import User

# ============================================================
# CONFIG
# ============================================================
BUCKET                  = 'tourgo-bigdata-lake'
STATE_FILE              = os.path.join(current_dir, 'last_export_state.json')
EXPORT_INTERVAL_MINUTES = 5
OVERLAP_SECONDS         = 60

# Tạo thư mục logs nếu chưa có
logs_dir = os.path.join(project_dir, 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(logs_dir, 'export.log'),
            encoding='utf-8'
        )
    ]
)
logger = logging.getLogger(__name__)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-southeast-1')
)

# ============================================================
# STATE MANAGEMENT
# ============================================================
def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_export_time":       "2020-01-01T00:00:00",
        "run_count":              0,
        "total_records_exported": 0
    }

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
    try:
        s3.put_object(
            Bucket=BUCKET,
            Key='metadata/last_export_state.json',
            Body=json.dumps(state, indent=2).encode('utf-8')
        )
    except Exception as e:
        logger.warning(f"[STATE] Khong upload duoc state len S3: {e}")

# ============================================================
# UPLOAD LOCAL CSV TO S3
# ============================================================
def upload_local_csv_to_s3(timestamp_str):
    exported_dir = os.path.join(backend_dir, 'exported_data')
    total = 0

    if not os.path.exists(exported_dir):
        logger.warning(f"[LOCAL] Khong tim thay folder: {exported_dir}")
        return 0

    for filename in os.listdir(exported_dir):
        if not filename.endswith('.csv'):
            continue
        table_name = filename.replace('.csv', '')
        local_path = os.path.join(exported_dir, filename)
        try:
            with open(local_path, 'rb') as f:
                key = f"raw/{table_name}/{timestamp_str}/data.csv"
                s3.put_object(
                    Bucket=BUCKET,
                    Key=key,
                    Body=f.read()
                )
            logger.info(f"[LOCAL] Uploaded {filename} -> s3://{BUCKET}/{key}")
            total += 1
        except Exception as e:
            logger.error(f"[LOCAL] Loi upload {filename}: {e}")

    return total

# ============================================================
# UPLOAD TO S3
# ============================================================
def upload_to_s3(rows, fields, table_name, timestamp_str):
    if not rows:
        logger.info(f"[SKIP] {table_name}: 0 records moi")
        return 0
    try:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        key = f"raw/{table_name}/{timestamp_str}/data.csv"
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=buffer.getvalue().encode('utf-8-sig')
        )
        logger.info(f"[S3] Uploaded {len(rows)} rows -> s3://{BUCKET}/{key}")
        return len(rows)
    except Exception as e:
        logger.error(f"[S3] Loi upload {table_name}: {e}")
        return 0

# ============================================================
# FULL SYNC (users, tours)
# ============================================================
def export_full_sync(timestamp_str):
    total = 0

    # USERS
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
                'id':          u.id,
                'role':        role,
                'is_active':   u.is_active,
                'date_joined': u.date_joined.strftime('%Y-%m-%d %H:%M:%S') if u.date_joined else '',
            })
        total += upload_to_s3(users_data,
            ['id', 'role', 'is_active', 'date_joined'],
            'users', timestamp_str)
    except Exception as e:
        logger.error(f"[SYNC] Loi users: {e}")

    # TOURS
    try:
        tours_data = []
        for t in Tour.objects.select_related('creator').prefetch_related('categories').all():
            cats = ",".join([c.name for c in t.categories.all()])
            tours_data.append({
                'id':             t.id,
                'creator_id':     t.creator_id,
                'title':          t.title,
                'price':          float(t.price) if t.price else 0.0,
                'departure_date': str(t.departure_date),
                'slots':          t.slots,
                'status':         t.status or 'active',
                'created_at':     t.created_at.strftime('%Y-%m-%d %H:%M:%S') if t.created_at else '',
                'category_names': cats or '',
            })
        total += upload_to_s3(tours_data,
            ['id', 'creator_id', 'title', 'price', 'departure_date',
             'slots', 'status', 'created_at', 'category_names'],
            'tours', timestamp_str)
    except Exception as e:
        logger.error(f"[SYNC] Loi tours: {e}")

    return total

# ============================================================
# INCREMENTAL EXPORT (bookings, payments, revenues, reviews)
# ============================================================
def export_incremental(since_dt, timestamp_str):
    since_with_buffer = since_dt - timedelta(seconds=OVERLAP_SECONDS)
    total = 0

    # BOOKINGS
    try:
        bookings_qs = list(Booking.objects.filter(
            created_at__gte=since_with_buffer
        ).values(
            'id', 'user_id', 'tour_id', 'number_of_people',
            'total_price', 'booking_date', 'status', 'created_at'
        ))
        rows = [{
            **b,
            'total_price':  float(b['total_price']) if b['total_price'] else 0.0,
            'booking_date': str(b['booking_date'])  if b['booking_date'] else '',
            'created_at':   b['created_at'].strftime('%Y-%m-%d %H:%M:%S') if b['created_at'] else '',
        } for b in bookings_qs]
        total += upload_to_s3(rows,
            ['id', 'user_id', 'tour_id', 'number_of_people',
             'total_price', 'booking_date', 'status', 'created_at'],
            'bookings', timestamp_str)
    except Exception as e:
        logger.error(f"[INCR] Loi bookings: {e}")

    # PAYMENTS
    try:
        payments_qs = list(Payment.objects.filter(
            created_at__gte=since_with_buffer
        ).values(
            'id', 'booking_id', 'amount', 'payment_method', 'status', 'created_at'
        ))
        rows = [{
            **p,
            'amount':     float(p['amount']) if p['amount'] else 0.0,
            'created_at': p['created_at'].strftime('%Y-%m-%d %H:%M:%S') if p['created_at'] else '',
        } for p in payments_qs]
        total += upload_to_s3(rows,
            ['id', 'booking_id', 'amount', 'payment_method', 'status', 'created_at'],
            'payments', timestamp_str)
    except Exception as e:
        logger.error(f"[INCR] Loi payments: {e}")

    # REVENUES
    try:
        from tours.models import Revenue
        revenues_qs = list(Revenue.objects.filter(
            created_at__gte=since_with_buffer
        ).values(
            'id', 'payment_id', 'creator_id',
            'total_amount', 'creator_share', 'admin_share', 'created_at'
        ))
        rows = [{
            **r,
            'total_amount':  float(r['total_amount'])  if r['total_amount']  else 0.0,
            'creator_share': float(r['creator_share']) if r['creator_share'] else 0.0,
            'admin_share':   float(r['admin_share'])   if r['admin_share']   else 0.0,
            'created_at':    r['created_at'].strftime('%Y-%m-%d %H:%M:%S') if r['created_at'] else '',
        } for r in revenues_qs]
        total += upload_to_s3(rows,
            ['id', 'payment_id', 'creator_id', 'total_amount',
             'creator_share', 'admin_share', 'created_at'],
            'revenues', timestamp_str)
    except Exception as e:
        logger.warning(f"[INCR] Revenue chua co model hoac loi: {e}")

    # REVIEWS
    try:
        reviews_qs = list(Review.objects.filter(
            created_at__gte=since_with_buffer
        ).values('id', 'user_id', 'tour_id', 'rating', 'created_at'))
        rows = [{
            **r,
            'created_at': r['created_at'].strftime('%Y-%m-%d %H:%M:%S') if r['created_at'] else '',
        } for r in reviews_qs]
        total += upload_to_s3(rows,
            ['id', 'user_id', 'tour_id', 'rating', 'created_at'],
            'reviews', timestamp_str)
    except Exception as e:
        logger.error(f"[INCR] Loi reviews: {e}")

    return total

# ============================================================
# MAIN EXPORT CYCLE
# ============================================================
def run_export_cycle():
    state         = load_state()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    since_dt      = datetime.fromisoformat(state["last_export_time"])

    logger.info(f"[CYCLE] Run #{state['run_count'] + 1} | Since: {since_dt} | Timestamp: {timestamp_str}")

    # Upload file CSV local từ exported_data lên S3
    local_count = upload_local_csv_to_s3(timestamp_str)
    logger.info(f"[LOCAL] Da upload {local_count} file CSV tu exported_data")

    full_count = export_full_sync(timestamp_str)
    incr_count = export_incremental(since_dt, timestamp_str)
    total      = full_count + incr_count

    state["last_export_time"]       = datetime.now().isoformat()
    state["run_count"]              += 1
    state["total_records_exported"] += total

    save_state(state)

    logger.info(f"[CYCLE] Hoan tat | Local: {local_count} files | Full: {full_count} | Incremental: {incr_count} | Tong: {total}")
    logger.info(f"[STATE] run_count={state['run_count']} | total_exported={state['total_records_exported']}")

def main():
    logger.info("[START] Incremental Export Service dang chay... (5 phut/lan)")
    while True:
        try:
            run_export_cycle()
        except Exception as e:
            logger.error(f"[ERROR] Cycle loi: {e}")
        logger.info(f"[SLEEP] Nghi {EXPORT_INTERVAL_MINUTES} phut...")
        time.sleep(EXPORT_INTERVAL_MINUTES * 60)

# ============================================================
# CLI ARGS (Ngay 8)
# ============================================================
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else "scheduled"

    if mode == "once":
        logger.info("[CLI] Mode: once - chay 1 lan roi thoat")
        run_export_cycle()

    elif mode == "full-reset":
        logger.info("[CLI] Mode: full-reset - reset state va export toan bo")
        save_state({
            "last_export_time":       "2020-01-01T00:00:00",
            "run_count":              0,
            "total_records_exported": 0
        })
        run_export_cycle()

    else:
        logger.info("[CLI] Mode: scheduled - chay lien tuc 5 phut/lan")
        main()