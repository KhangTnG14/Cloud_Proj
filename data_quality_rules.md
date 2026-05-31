# DATA QUALITY & PIPELINE RULES (TOURGO PROJECT)

**Người thực hiện:** Member 2 (Data Engineer)
**Mục tiêu:** Đảm bảo dữ liệu tại tầng **Silver sạch, nhất quán** và tầng **Gold sẵn sàng cho Machine Learning & Analytics**.

---

## 1. TẦNG SILVER: CLEANING & STANDARDIZATION

Thực hiện trên Databricks Notebook để chuyển dữ liệu từ **Bronze (Raw) → Silver (Cleaned)**.

### 1.1. Chuẩn hóa kiểu dữ liệu (Schema Enforcement)

* **Timestamp**

  * Các cột: `booking_date`, `travel_date`, `created_at`
  * Chuyển về `TimestampType`
  * Loại bỏ phần mili-giây nếu có

* **Numeric**

  * `price`, `total_price` → `Decimal(18,2)` (ưu tiên) hoặc `Double`
  * `available_slots`, `num_people` → `Integer`

* **String**

  * Các cột: `destination`, `category`, `status`
  * Chuẩn hóa:

    * `lower()` (chữ thường)
    * `trim()` (loại bỏ khoảng trắng thừa)

---

### 1.2. Data Validation & Cleaning Rules

#### Null Handling

* `price` hoặc `total_price` bị NULL:
  → Điền bằng **giá trị trung bình (mean)** theo từng `category`

* `num_people <= 0`:
  → Gán mặc định = `1`

---

#### Status Validation

Chỉ chấp nhận các giá trị:

* `pending`
* `confirmed`
* `cancelled`

Nếu giá trị ngoài danh sách:
→ Gán mặc định = `pending`

---

### 1.3. Data Quality Check (Bắt buộc)

Sau mỗi bước xử lý:

```python
display(df.describe())
```

Kiểm tra:

* Min / Max
* Null count
* Phân bố dữ liệu

---

## 2. TẦNG GOLD: ANALYTICS & FEATURE ENGINEERING

Tạo các bảng phục vụ:

* Machine Learning (Member 3)
* Dashboard / Frontend (Member 4)

---

### 2.1. Bảng `gold_revenue_analytics`

**Mục tiêu:** Phân tích KPI doanh thu

| Cột              | Logic                                       |
| ---------------- | ------------------------------------------- |
| `month_year`     | Extract từ `booking_date` (format: yyyy-MM) |
| `revenue`        | SUM(`total_price`) với `status = confirmed` |
| `is_peak_season` | 1 nếu tháng ∈ [5,6,7,8], ngược lại = 0      |

---

### 2.2. Bảng `gold_ml_features`

#### Label cho Machine Learning

* `label_booking`:

  * `1` nếu `status = confirmed`
  * `0` nếu `status = cancelled`

---

#### Feature Engineering

* **customer_loyalty_days**

  ```text
  booking_date - user.created_at
  ```

* **tour_urgency**

  ```text
  available_slots / total_slots
  ```

  → Giá trị càng nhỏ → độ khan hiếm càng cao

---

#### Growth Feature (Linear Regression)

* **historical_growth_rate**

  ```text
  (Doanh thu tháng hiện tại - tháng trước) / tháng trước
  ```

---

## 3. STORAGE RULES (QUY TẮC LƯU TRỮ)

### Format

* Luôn sử dụng: **Delta Lake Format**

---

### Write Mode

| Pipeline        | Mode                            |
| --------------- | ------------------------------- |
| Bronze → Silver | `overwrite` (giai đoạn dev)     |
| Silver → Gold   | `overwrite` (cập nhật full KPI) |

---

### Optimization

* Bật:

  * `OPTIMIZE`
  * `ZORDER BY (booking_date)`

Giúp tăng tốc:

* Query dashboard
* BI tools
* ML pipeline

---

## GHI CHÚ QUAN TRỌNG

* Luôn validate dữ liệu sau mỗi bước
* Không để dữ liệu "dirty" lọt vào Gold
* Nếu gặp lỗi nghiêm trọng không thể xử lý:
  → Báo ngay cho **Leader (Member A)**

---

## MỤC TIÊU CUỐI

* Silver: **Sạch + Chuẩn hóa + Không lỗi logic**
* Gold: **Sẵn sàng cho ML + Dashboard + KPI real-time**

---
