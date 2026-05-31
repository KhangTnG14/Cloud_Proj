# DELTA LAKE TIME TRAVEL DEMO SCRIPT (TOURGO PROJECT)

**Người thực hiện:** Member B (Data Engineer)
**Người thuyết trình:** Member A (Leader)
**Mục tiêu:**

* Chứng minh khả năng **Time Travel (truy xuất dữ liệu theo thời gian)**
* Đảm bảo **ACID properties** của Delta Lake
* Thể hiện hệ thống có khả năng **versioning & rollback chuyên nghiệp**

---

## LẦN 1: KHỞI TẠO DỮ LIỆU GỐC (VERSION 0)

### Mục tiêu

* Tạo version đầu tiên của bảng Delta

### Thực hiện

```python
# Đọc dữ liệu từ Bronze (S3 / Data Lake)
df_v0 = spark.read.csv("/mnt/s3/raw/bookings.csv", header=True, inferSchema=True)

# Ghi vào bảng Delta (Version 0)
df_v0.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_bookings_delta")

# Kiểm tra số lượng dòng
print(f"Số lượng đơn hàng ban đầu: {df_v0.count()}")
```

---

## LẦN 2: GIẢ LẬP BIẾN ĐỘNG DỮ LIỆU (VERSION 1)

### Mục tiêu

* Tạo thêm một version mới để phục vụ Time Travel

### 🛠 Thực hiện

```python
# Giả lập thêm 50 đơn hàng mới
new_data = spark.createDataFrame(sample_50_new_bookings)

# Append vào bảng Delta → tạo Version 1
new_data.write.format("delta") \
    .mode("append") \
    .saveAsTable("gold_bookings_delta")

# Kiểm tra dữ liệu sau update
df_v1 = spark.table("gold_bookings_delta")
print(f"Số lượng đơn hàng sau khi thêm: {df_v1.count()}")
```

---

## LẦN 3: DEMO TIME TRAVEL (QUAN TRỌNG NHẤT)

 Đây là phần **Leader trình bày để ăn điểm**

---

### Kịch bản 1: Query theo Version

 **Thuyết trình:**

> "Thưa thầy, dù dữ liệu hiện tại đã thay đổi, nhưng chúng em có thể quay lại quá khứ để xem trạng thái hệ thống tại thời điểm ban đầu."

```sql
SELECT COUNT(*) 
FROM gold_bookings_delta 
VERSION AS OF 0;
```

 **Kết quả mong đợi:**

* Số lượng bản ghi = Version 0 (ban đầu)

---

### Kịch bản 2: Query theo Timestamp

**Thuyết trình:**

> "Ngoài version, hệ thống còn cho phép truy vấn dữ liệu theo mốc thời gian cụ thể."

```sql
SELECT * 
FROM gold_bookings_delta 
TIMESTAMP AS OF '2026-04-23 10:00:00';
```

**Ý nghĩa:**

* Kiểm tra trạng thái dữ liệu tại một thời điểm trong quá khứ

---

### (Optional - Điểm cộng): Kiểm tra lịch sử version

```sql
DESCRIBE HISTORY gold_bookings_delta;
```

 Hiển thị:

* Version
* Timestamp
* Operation (WRITE / APPEND)

---

## LẦN 4: SCHEMA ENFORCEMENT (ĐIỂM CỘNG MẠNH)

### Kịch bản

* Cố tình ghi dữ liệu sai schema vào bảng Delta

---

### 🛠 Thực hiện

```python
# Tạo dữ liệu sai schema (ví dụ thêm cột lạ)
bad_data = df_v0.withColumn("invalid_column", lit("error"))

# Thử ghi vào Delta
bad_data.write.format("delta") \
    .mode("append") \
    .saveAsTable("gold_bookings_delta")
```

---

### Kết quả mong đợi

* Spark sẽ **báo lỗi ngay lập tức**

---

### Thuyết trình

> "Delta Lake có cơ chế Schema Enforcement giúp ngăn chặn dữ liệu không hợp lệ, đảm bảo pipeline luôn ổn định và không bị phá vỡ ở các bước downstream."

---

## KẾT LUẬN DEMO

### Những gì chứng minh được:

*  Time Travel (Version & Timestamp)
*  Data Versioning
*  ACID Transaction
*  Schema Enforcement
*  Pipeline Production-Ready