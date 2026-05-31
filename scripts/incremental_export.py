import os
import django
import csv
import sys
import json
import boto3
import time
import logging
import io
from datetime import datetime, timedelta
from pathlib import Path
os.makedirs("logs", exist_ok=True)
# Khởi tạo log để dễ dàng theo dõi quá trình chạy background qua file log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/export.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Các kịch bản thư mục con có khả năng chứa mã nguồn dự án Web của nhóm
POSSIBLE_PATHS = [
    BASE_DIR,                           # Nếu core nằm ngay thư mục gốc
    os.path.join(BASE_DIR, "backend"),  # Nếu nằm trong thư mục backend
    os.path.join(BASE_DIR, "TourGo"),   # Nếu nằm trong thư mục TourGo
    os.path.join(BASE_DIR, "backend", "TourGo") # Nếu bị lồng sâu 2 cấp
]

django_project_path = None
for p in POSSIBLE_PATHS:
    if os.path.exists(os.path.join(p, "core", "settings.py")):
        django_project_path = str(p)
        break

if django_project_path:
    sys.path.append(django_project_path)
    logging.info(f"🔍 [Path Match] Tìm thấy cấu hình Django tại: {django_project_path}")
else:
    # Nếu vẫn không dò ra, ép hệ thống in ra danh sách file hiện tại để Hà kiểm tra trực tiếp
    logging.error(f"❌ Không tìm thấy thư mục 'core/settings.py' tại cấu trúc gốc: {BASE_DIR}")
    if os.path.exists(os.path.join(BASE_DIR, "backend")):
         logging.error(f"Thư mục con của 'backend': {os.listdir(os.path.join(BASE_DIR, 'backend'))}")
    raise ModuleNotFoundError("Vui lòng kiểm tra lại vị trí chính xác của thư mục 'core' chứa settings.py")

# Cấu hình môi trường Django để tương tác với cơ sở dữ liệu SQL Server
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tours.models import Tour, Booking, Payment, Revenue, Review
from users.models import User

BUCKET = 'tourgo-data-lake'
STATE_FILE = 'scripts/last_export_state.json'
EXPORT_INTERVAL_MINUTES = 5
OVERLAP_SECONDS = 60  # Buffer an toàn chống rớt bản ghi phát sinh đồng thời

# Khởi tạo kết nối AWS S3 sử dụng các biến cấu hình từ hệ thống
s3 = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='ap-southeast-1'
)

def load_state():
    """Tải trạng thái mốc thời gian của chu kỳ đồng bộ trước đó"""
    if Path(STATE_FILE).exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    # Nếu chạy lần đầu, lấy mốc lịch sử mặc định để quét sạch toàn bộ dữ liệu hiện có
    return {"last_export_time": "2020-01-01T00:00:00", "run_count": 0, "total_records_exported": 0}

def save_state(state):
    """Lưu lại trạng thái đồng bộ xuống file local và đồng bộ lên S3 Metadata"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    try:
        s3.put_object(Bucket=BUCKET, Key='metadata/last_export_state.json',
                      Body=json.dumps(state, indent=2))
    except Exception as e:
        logging.error(f"Không thể đồng bộ file trạng thái lên S3 Metadata: {e}")

def upload_to_s3(rows, fields, table_name, timestamp_str):
    """Xuất mảng dữ liệu ra định dạng CSV chuẩn UTF-8-SIG và đẩy trực tiếp lên S3"""
    if not rows:
        return 0
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    
    # Cấu trúc lưu trữ động cô lập theo mốc thời gian đúng như yêu cầu của [A] Vũ Hà
    key = f"raw/{table_name}/{timestamp_str}/data.csv"
    s3.put_object(Bucket=BUCKET, Key=key,
                  Body=buffer.getvalue().encode('utf-8-sig'))
    logging.info(f"🚀 [S3 Upload] Thành công: {len(rows)} dòng -> s3://{BUCKET}/{key}")
    return len(rows)

def export_full_sync(timestamp_str):
    """Thực hiện Full Snapshot cho các bảng danh mục (Users, Tours)"""
    total = 0
    logging.info("🔄 Bắt đầu Full Sync cho Users và Tours...")
    
    # BẢNG USERS (Ẩn danh thông tin nhạy cảm bảo mật PII)
    users_qs = list(User.objects.values('id', 'role', 'is_active', 'date_joined'))
    total += upload_to_s3(users_qs, ['id','role','is_active','date_joined'], 'users', timestamp_str)
    
    # BẢNG TOURS (Xử lý gộp liên kết Many-to-Many cho chuyên mục)
    tours_data = []
    for t in Tour.objects.prefetch_related('categories').all():
        cats = ",".join([c.name for c in t.categories.all()])
        # Định dạng date và timestamp sang chuỗi string chuẩn hóa
        tours_data.append({
            'id': t.id, 'creator_id': t.creator_id, 'title': t.title, 'price': float(t.price),
            'departure_date': str(t.departure_date), 'slots': t.slots, 'status': t.status,
            'created_at': t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else "",
            'category_names': cats
        })
    total += upload_to_s3(tours_data,
                          ['id','creator_id','title','price','departure_date','slots','status','created_at','category_names'],
                          'tours', timestamp_str)
    return total

def export_incremental(since_dt, timestamp_str):
    """Thực hiện trích xuất tăng trưởng (Incremental) cho các bảng nhật ký giao dịch"""
    # Xử lý múi giờ để tương thích với cấu hình TIME_ZONE của Django (tránh lỗi Navie/Aware datetime)
    from django.utils.timezone import get_current_timezone
    tz = get_current_timezone()
    if since_dt.tzinfo is None:
        since_dt = since_dt.replace(tzinfo=tz)

    since_with_buffer = since_dt - timedelta(seconds=OVERLAP_SECONDS)
    total = 0
    logging.info(f"📈 Quét dữ liệu phát sinh tăng trưởng kể từ mốc mốc an toàn: {since_with_buffer}")

    # 1. BOOKINGS
    bookings_qs = list(Booking.objects.filter(created_at__gte=since_with_buffer).values(
        'id', 'user_id', 'tour_id', 'number_of_people', 'total_price', 'booking_date', 'status', 'created_at'
    ))
    for b in bookings_qs:
        b['total_price'] = float(b['total_price'])
        b['booking_date'] = str(b['booking_date'])
        b['created_at'] = b['created_at'].strftime("%Y-%m-%d %H:%M:%S") if b['created_at'] else ""
    if bookings_qs:
        total += upload_to_s3(bookings_qs, ['id','user_id','tour_id','number_of_people','total_price','booking_date','status','created_at'], 'bookings', timestamp_str)

    # 2. PAYMENTS (Bổ sung hoàn chỉnh phần thiếu của D)
    payments_qs = list(Payment.objects.filter(created_at__gte=since_with_buffer).values(
        'id', 'booking_id', 'amount', 'payment_method', 'status', 'created_at'
    ))
    for p in payments_qs:
        p['amount'] = float(p['amount'])
        p['created_at'] = p['created_at'].strftime("%Y-%m-%d %H:%M:%S") if p['created_at'] else ""
    if payments_qs:
        total += upload_to_s3(payments_qs, ['id','booking_id','amount','payment_method','status','created_at'], 'payments', timestamp_str)

    # 3. REVENUES (Bổ sung hoàn chỉnh phần thiếu của D)
    revenues_qs = list(Revenue.objects.filter(created_at__gte=since_with_buffer).values(
        'id', 'payment_id', 'creator_id', 'total_amount', 'creator_share', 'admin_share', 'created_at'
    ))
    for r in revenues_qs:
        r['total_amount'] = float(r['total_amount'])
        r['creator_share'] = float(r['creator_share'])
        r['admin_share'] = float(r['admin_share'])
        r['created_at'] = r['created_at'].strftime("%Y-%m-%d %H:%M:%S") if r['created_at'] else ""
    if revenues_qs:
        total += upload_to_s3(revenues_qs, ['id','payment_id','creator_id','total_amount','creator_share','admin_share','created_at'], 'revenues', timestamp_str)

    # 4. REVIEWS (Bổ sung hoàn chỉnh phần thiếu của D)
    reviews_qs = list(Review.objects.filter(created_at__gte=since_with_buffer).values(
        'id', 'user_id', 'tour_id', 'rating', 'created_at'
    ))
    for rv in reviews_qs:
        rv['created_at'] = rv['created_at'].strftime("%Y-%m-%d %H:%M:%S") if rv['created_at'] else ""
    if reviews_qs:
        total += upload_to_s3(reviews_qs, ['id','user_id','tour_id','rating','created_at'], 'reviews', timestamp_str)

    return total

def run_export_cycle():
    """Vận hành một chu kỳ đồng bộ khép kín"""
    logging.info("========== BẮT ĐẦU CHU KỲ ĐỒNG BỘ DỮ LIỆU TỰ ĐỘNG ==========")
    state = load_state()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    since_dt = datetime.fromisoformat(state["last_export_time"])
    
    try:
        full_count = export_full_sync(timestamp_str)
        incr_count = export_incremental(since_dt, timestamp_str)
        
        # Cập nhật nhật ký trạng thái mới ngay sau khi thành công
        state["last_export_time"] = datetime.now().isoformat()
        state["run_count"] += 1
        state["total_records_exported"] += (full_count + incr_count)
        save_state(state)
        logging.info(f"🎉 Chu kỳ #{state['run_count']} HOÀN THÀNH. Tổng xuất: {full_count + incr_count} bản ghi.\n")
    except Exception as e:
        logging.error(f"❌ Chu kỳ đồng bộ thất bại do lỗi hệ thống: {e}\n")

def main():
    # Tạo thư mục logs nếu chưa tồn tại
    logging.info(f"🚀 Hệ thống tự động đồng bộ bắt đầu khởi chạy. Chu kỳ: {EXPORT_INTERVAL_MINUTES} phút/lần.")
    while True:
        run_export_cycle()
        logging.info(f"💤 Nghỉ ngơi trong {EXPORT_INTERVAL_MINUTES} phút...")
        time.sleep(EXPORT_INTERVAL_MINUTES * 60)

if __name__ == '__main__':
    main()