# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import random
import boto3
from datetime import datetime, date
from dotenv import load_dotenv

# Load .env
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
load_dotenv(os.path.join(project_dir, '.env'))

# Lấy IDs thật từ CSV
import csv

def load_ids_from_csv(filename, id_col):
    path = os.path.join(project_dir, 'backend', 'exported_data', filename)
    ids = []
    # Sử dụng utf-8-sig để tự bóc tách ký tự BOM ẩn trên Windows nếu có
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            # Tự động loại bỏ hoàn toàn dấu nháy kép thừa ở cả Key và Value của dòng dữ liệu
            clean_row = {k.strip('"'): v.strip('"') for k, v in row.items() if k is not None}
            if id_col in clean_row and clean_row[id_col]:
                ids.append(int(clean_row[id_col]))
    return ids

def load_prices_from_csv():
    path = os.path.join(project_dir, 'backend', 'exported_data', 'tours.csv')
    prices = []
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            # Tự động loại bỏ hoàn toàn dấu nháy kép thừa ở cả Key và Value của dòng dữ liệu
            clean_row = {k.strip('"'): v.strip('"') for k, v in row.items() if k is not None}
            try:
                if 'price' in clean_row and clean_row['price']:
                    prices.append(float(clean_row['price']))
            except:
                pass
    return prices

# Load IDs thật
print("[LOAD] Dang doc IDs that tu CSV...")
REAL_USER_IDS = load_ids_from_csv('users.csv', 'id')
REAL_TOUR_IDS = load_ids_from_csv('tours.csv', 'id')
REAL_PRICES   = load_prices_from_csv()

print(f"[LOAD] Users: {len(REAL_USER_IDS)} | Tours: {len(REAL_TOUR_IDS)} | Prices: {len(REAL_PRICES)}")

# S3 config
BUCKET = 'tourgo-bigdata-lake'
PREFIX = 'streaming/new_bookings'

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-southeast-1')
)

def generate_booking():
    """Tạo 1 booking giả lập với IDs thật từ TourGo"""
    tour_idx = random.randint(0, len(REAL_TOUR_IDS) - 1)
    return {
        "id":               int(datetime.now().timestamp() * 1000) + random.randint(1, 999),
        "user_id":          random.choice(REAL_USER_IDS),
        "tour_id":          REAL_TOUR_IDS[tour_idx],
        "number_of_people": random.randint(1, 4),
        "total_price":      REAL_PRICES[tour_idx] * random.randint(1, 4),
        "booking_date":     str(date.today()),
        "status":           random.choice(["confirmed", "confirmed", "pending"]),
        "created_at":       datetime.now().isoformat(),
        "source":           "streaming_simulator"
    }

def upload_batch(batch_size=2):
    """Upload 1 batch lên S3 dưới dạng JSON Lines"""
    bookings = [generate_booking() for _ in range(batch_size)]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    key = f"{PREFIX}/bookings_{timestamp}.json"

    # JSON Lines: mỗi dòng là 1 JSON object
    body = "\n".join(json.dumps(b, ensure_ascii=False) for b in bookings)

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body.encode('utf-8')
    )
    return bookings, key

def main():
    print("=" * 50)
    print("[START] Streaming Simulator dang chay...")
    print(f"[INFO] Target: s3://{BUCKET}/{PREFIX}/")
    print("[INFO] Interval: 30 giay | Batch: 1-3 bookings")
    print("[INFO] Nhan Ctrl+C de dung")
    print("=" * 50)

    batch_num = 0
    total_uploaded = 0

    while True:
        try:
            batch_size = random.randint(1, 3)
            bookings, key = upload_batch(batch_size)
            batch_num += 1
            total_uploaded += batch_size

            print(f"\n[BATCH #{batch_num}] {datetime.now().strftime('%H:%M:%S')} — Uploaded {batch_size} bookings")
            print(f"  Key: {key}")
            for b in bookings:
                print(f"  Booking {b['id']}: user={b['user_id']} tour={b['tour_id']} price={b['total_price']:,.0f} status={b['status']}")
            print(f"  Total uploaded: {total_uploaded} bookings")

            time.sleep(30)

        except KeyboardInterrupt:
            print(f"\n[STOP] Dung simulator. Tong: {total_uploaded} bookings trong {batch_num} batches.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(10)

if __name__ == '__main__':
    main()