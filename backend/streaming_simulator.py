import os
import sys
import json
import time
import random
import boto3
from datetime import datetime, date
# 🔥 ĐÃ THÊM: Import thư viện load file .env trực tiếp
from dotenv import load_dotenv

# ── 1. NẠP BIẾN MÔI TRƯỜNG TỪ FILE .ENV TRƯỚC KHI GỌI AWS ──────────────
# Vị trí file: C:\Test\backend\streaming_simulator.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))   # Thư mục backend
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)                 # Thư mục gốc C:\Test
ENV_PATH = os.path.join(PROJECT_ROOT, '.env')              # Đường dẫn tới C:\Test\.env

if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"✅ [SYSTEM] Đã nạp file cấu hình bảo mật .env từ: {ENV_PATH}")
else:
    print(f"⚠️ [CẢNH BÁO] Không tìm thấy file .env tại {ENV_PATH}. Hãy kiểm tra lại vị trí file!")

# ── 2. THIẾT LẬP KẾT NỐI DJANGO ORM TẠI CHỖ ───────────────────────────
sys.path.append(CURRENT_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    import django
    django.setup()
    from tours.models import Tour, Booking
    from users.models import User
    HAS_DJANGO = True
except Exception as e:
    print(f"[CẢNH BÁO] Không thể khởi chạy Django ORM: {e}")
    HAS_DJANGO = False

# ── 3. CẤU HÌNH AWS S3 CHUẨN XÁC THEO ẢNH CHỤP CONSOLE ────────────────
BUCKET = 'tourgo-bigdata-lake'
PREFIX = 'streaming/new_bookings'
REGION = 'eu-north-1'  # Khu vực Stockholm

# Hệ thống lấy chính xác chuỗi mã thực tế từ file .env vừa nạp ở trên
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Khởi tạo client kèm định danh vùng Region chuẩn xác
s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

# ── 4. TRÍCH XUẤT ID THẬT TỪ DATABASE DJANGO ─────────────────────────
if HAS_DJANGO:
    try:
        SAMPLE_USER_IDS = list(User.objects.filter(is_active=True).values_list('id', flat=True))
        SAMPLE_TOUR_IDS = list(Tour.objects.filter(status='Active').values_list('id', flat=True))
        
        if not SAMPLE_USER_IDS: SAMPLE_USER_IDS = [1, 2, 3]
        if not SAMPLE_TOUR_IDS: SAMPLE_TOUR_IDS = [1, 2, 3]
    except Exception:
        SAMPLE_USER_IDS = [1, 2, 3, 5, 8, 13, 21]
        SAMPLE_TOUR_IDS = [1, 2, 3, 4, 5]
else:
    SAMPLE_USER_IDS = [1, 2, 3, 5, 8, 13, 21]
    SAMPLE_TOUR_IDS = [1, 2, 3, 4, 5]

SAMPLE_PRICES = [1500000, 2000000, 3500000, 5000000, 7500000]

def generate_booking():
    """Tạo bản ghi dữ liệu đơn hàng giả lập khớp kiểu Double và Timestamp của Spark"""
    return {
        "id": int(datetime.now().timestamp() * 1000) + random.randint(1, 999),
        "user_id": random.choice(SAMPLE_USER_IDS),
        "tour_id": random.choice(SAMPLE_TOUR_IDS),
        "number_of_people": random.randint(1, 4),
        "total_price": float(random.choice(SAMPLE_PRICES)),
        "booking_date": str(date.today()),
        "status": random.choice(["pending", "confirmed"]),
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "source": "streaming_simulator"
    }

def upload_batch(batch_size=2):
    """Đóng gói mảng bản ghi thành chuỗi JSON Lines (phân tách \n) và đẩy lên AWS S3"""
    bookings = [generate_booking() for _ in range(batch_size)]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    key = f"{PREFIX}/bookings_{timestamp}.json"
    
    body = "\n".join(json.dumps(b) for b in bookings)
    
    try:
        s3.put_object(Bucket=BUCKET, Key=key, Body=body)
        print(f"✅ [S3] Đã đẩy thành công batch {batch_size} đơn → s3://{BUCKET}/{key}")
    except Exception as e:
        print(f"❌ [S3 LỖI THỰC TẾ] Không thể đẩy dữ liệu stream lên Bucket [{BUCKET}]: {e}")
        print("    ↳ Mẹo kiểm tra: Hãy soát lại xem chuỗi điền trong file .env có bị thừa dấu cách hay ngoặc kép không.")
        
    return bookings

if __name__ == '__main__':
    print("="*60)
    print("🚀 TOURGO STREAMING SIMULATOR - NGÀY 2 (ĐÃ FIX LỖI LOAD ENV)")
    print(f"   Target Bucket:              {BUCKET}")
    print(f"   AWS Region:                 {REGION}")
    print(f"   Trạng thái kết nối Django:  {'KẾT NỐI THẬT OK' if HAS_DJANGO else 'DÙNG DATA GIẢ LẬP'}")
    print(f"   Số lượng Khách Hàng khả dụng: {len(SAMPLE_USER_IDS)}")
    print(f"   Số lượng Chuyến Đi khả dụng:  {len(SAMPLE_TOUR_IDS)}")
    print("   Nhấn tổ hợp phím Ctrl+C để dừng luồng giả lập.")
    print("="*60)
    
    try:
        while True:
            current_batch_size = random.randint(1, 3)
            batch = upload_batch(batch_size=current_batch_size)
            
            for b in batch:
                print(f"    ↳ Đơn [{b['id']}]: User ID={b['user_id']} | Tour ID={b['tour_id']} | Giá={b['total_price']:,} VNĐ")
            
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng tiến trình mô phỏng luồng dữ liệu Streaming thành công!")