import os
import sys
from datetime import datetime
from pathlib import Path
import django
import pandas as pd

# ==============================================================================
# 🛠️ KHỞI TẠO MÔI TRƯỜNG DJANGO (BẮT BUỘC CHO SCRIPT ĐỘC LẬP)
# ==============================================================================
# Lấy đường dẫn thư mục gốc 'backend'
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Thiết lập biến môi trường trỏ tới file settings của mục core
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Kích hoạt cấu hình hệ thống của Django
django.setup()

# ==============================================================================
# 📦 IMPORT CÁC MODEL THEO ĐÚNG DJANGO ORM
# ==============================================================================
from tours.models import Booking, Payment, Revenue, Review, Tour
from users.models import User

# Đường dẫn tĩnh tuyệt đối tới thư mục chứa dữ liệu sạch CSV của bạn
DATA_DIR = r"C:\Test\backend\exported_data"


def get_file_path(filename):
    """Hàm lấy đường dẫn tuyệt đối của file CSV bằng cách ghép chuỗi an toàn"""
    return os.path.join(DATA_DIR, filename)


# ==============================================================================
# 📥 CÁC HÀM SEED DỮ LIỆU SẠCH SỬ DỤNG DJANGO ORM
# ==============================================================================


def seed_users():
    print("⏳ Đang nạp bảng users...")
    file_path = get_file_path("users_clean.csv")
    df = pd.read_csv(file_path)

    users_to_create = []
    for _, row in df.iterrows():
        # Kiểm tra trùng lặp bằng Django ORM
        if not User.objects.filter(id=int(row["id"])).exists():
            # Chuyển đổi chuỗi string thành đối tượng datetime của Python
            date_joined_dt = datetime.strptime(
                str(row["date_joined"]), "%Y-%m-%d %H:%M:%S"
            )

            user = User(
                id=int(row["id"]),
                role=str(row["role"]).upper(),
                is_active=bool(row["is_active"]),
                date_joined=date_joined_dt,
            )
            users_to_create.append(user)

    # Sử dụng bulk_create để nạp dữ liệu siêu nhanh vào SQL Server
    if users_to_create:
        User.objects.bulk_create(users_to_create)
    print("✅ Nạp bảng users thành công!")


def seed_tours():
    print("⏳ Đang nạp bảng tours...")
    file_path = get_file_path("tours_clean.csv")
    df = pd.read_csv(file_path)

    tours_to_create = []
    for _, row in df.iterrows():
        if not Tour.objects.filter(id=int(row["id"])).exists():
            created_at_dt = datetime.strptime(
                str(row["created_at"]), "%Y-%m-%d %H:%M:%S"
            )
            departure_date_d = pd.to_datetime(row["departure_date"]).date()

            tour = Tour(
                id=int(row["id"]),
                creator_id=int(row["creator_id"]),
                title=row["title"],
                price=float(row['price']),
                departure_date=departure_date_d,
                slots=int(row["slots"]),
                status=(
                    str(row["status"]).upper()
                    if pd.notna(row["status"])
                    else "APPROVED"
                ),
                created_at=created_at_dt,
                category_names=(
                    row["category_names"] if pd.notna(row["category_names"]) else ""
                ),
            )
            tours_to_create.append(tour)

    if tours_to_create:
        Tour.objects.bulk_create(tours_to_create)
    print("✅ Nạp bảng tours thành công!")


def seed_bookings():
    print("⏳ Đang nạp bảng bookings...")
    file_path = get_file_path("bookings_clean.csv")
    df = pd.read_csv(file_path)

    bookings_to_create = []
    for _, row in df.iterrows():
        if not Booking.objects.filter(id=int(row["id"])).exists():
            created_at_dt = datetime.strptime(
                str(row["created_at"]), "%Y-%m-%d %H:%M:%S"
            )
            booking_date_d = pd.to_datetime(row["booking_date"]).date()

            booking = Booking(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                tour_id=int(row["tour_id"]),
                number_of_people=int(row["number_of_people"]),
                total_price=float(row['total_price']),
                booking_date=booking_date_d,
                status=(
                    str(row["status"]).upper()
                    if pd.notna(row["status"])
                    else "CONFIRMED"
                ),
                created_at=created_at_dt,
            )
            bookings_to_create.append(booking)

    if bookings_to_create:
        Booking.objects.bulk_create(bookings_to_create)
    print("✅ Nạp bảng bookings thành công!")


def seed_payments():
    print("⏳ Đang nạp bảng payments...")
    file_path = get_file_path("payments_clean.csv")
    df = pd.read_csv(file_path)

    payments_to_create = []
    for _, row in df.iterrows():
        if not Payment.objects.filter(id=int(row["id"])).exists():
            created_at_dt = datetime.strptime(
                str(row["created_at"]), "%Y-%m-%d %H:%M:%S"
            )

            payment = Payment(
                id=int(row["id"]),
                booking_id=int(row["booking_id"]),
                amount=float(row['amount']),
                payment_method=(
                    str(row["payment_method"]).upper()
                    if pd.notna(row["payment_method"])
                    else "VNPAY"
                ),
                status=(
                    str(row["status"]).upper()
                    if pd.notna(row["status"])
                    else "SUCCESS"
                ),
                created_at=created_at_dt,
            )
            payments_to_create.append(payment)

    if payments_to_create:
        Payment.objects.bulk_create(payments_to_create)
    print("✅ Nạp bảng payments thành công!")


def seed_revenues():
    print("⏳ Đang nạp bảng revenues...")
    file_path = get_file_path("revenues_clean.csv")
    df = pd.read_csv(file_path)

    revenues_to_create = []
    for _, row in df.iterrows():
        if not Revenue.objects.filter(id=int(row["id"])).exists():
            created_at_dt = datetime.strptime(
                str(row["created_at"]), "%Y-%m-%d %H:%M:%S"
            )

            revenue = Revenue(
                id=int(row["id"]),
                payment_id=int(row["payment_id"]),
                creator_id=int(row["creator_id"]),
                total_amount=float(row['total_amount']),
                creator_share=float(row['creator_share']),
                admin_share=float(row['admin_share']),
                created_at=created_at_dt,
            )
            revenues_to_create.append(revenue)

    if revenues_to_create:
        Revenue.objects.bulk_create(revenues_to_create)
    print("✅ Nạp bảng revenues thành công!")


def seed_reviews():
    print("⏳ Đang nạp bảng reviews...")
    file_path = get_file_path("reviews_clean.csv")
    df = pd.read_csv(file_path)

    reviews_to_create = []
    for _, row in df.iterrows():
        if not Review.objects.filter(id=int(row["id"])).exists():
            created_at_dt = datetime.strptime(
                str(row["created_at"]), "%Y-%m-%d %H:%M:%S"
            )

            review = Review(
                id=int(row["id"]),
                booking_id=int(row["booking_id"]),
                user_id=int(row["user_id"]),
                tour_id=int(row["tour_id"]),
                rating=int(row["rating"]),
                created_at=created_at_dt,
            )
            reviews_to_create.append(review)

    if reviews_to_create:
        Review.objects.bulk_create(reviews_to_create)
    print("✅ Nạp bảng reviews thành công!")


# ==============================================================================
# 🚀 KHỞI CHẠY CHÍNH
# ==============================================================================
if __name__ == "__main__":
    print(
        "🚀 Bắt đầu quá trình nạp dữ liệu sạch vào hệ thống TourGo (Django ORM)..."
    )

    try:
        seed_users()
        seed_tours()
        seed_bookings()
        seed_payments()
        seed_revenues()
        seed_reviews()
        print("\n🎉 TẤT CẢ DỮ LIỆU SẠCH ĐÃ ĐƯỢC SEED VÀO SQL SERVER THÀNH CÔNG!")
    except Exception as e:
        print(f"\n❌ Có lỗi xảy ra trong quá trình seed dữ liệu: {e}")