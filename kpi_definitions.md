# JOIN LOGIC, KPI & FEATURE ENGINEERING RULES (TOURGO PROJECT)

**Áp dụng:** Tầng **Silver → Gold**
**Người thực hiện:**

* Member B (Data Engineer - SQL / Aggregation)
* Member C (Machine Learning / Dashboard)

**Mục tiêu:**

* Tạo **bảng phẳng (Flat Table)** chuẩn hóa, không duplicate
* Xây dựng KPI rõ ràng phục vụ Dashboard & ML

---

## 1. LOGIC JOIN (SILVER → GOLD)

### Nguyên tắc

* Join theo **Primary Key chuẩn**
* Tránh duplicate bằng:

  * Không join nhiều-nhiều (many-to-many)
  * Đảm bảo mỗi bảng đã clean ở Silver
* Ưu tiên **LEFT JOIN từ bảng bookings (fact table)**

---

### Bảng đích: `gold_full_booking_data`

| Group      | Field Name       | Source               | Logic / Note                              |
| ---------- | ---------------- | -------------------- | ----------------------------------------- |
| Booking    | booking_id       | bookings             | Primary Key                               |
| Booking    | booking_date     | bookings             | Format: `YYYY-MM-DD`                      |
| Booking    | travel_date      | bookings             | Timestamp chuẩn                           |
| Booking    | status           | bookings             | pending / confirmed / cancelled           |
| Booking    | num_people       | bookings             | Integer                                   |
| User       | user_id          | users                | Join key                                  |
| User       | full_name        | users                |                                           |
| User       | city             | users                |                                           |
| Tour       | tour_id          | tours                | Join key                                  |
| Tour       | tour_name        | tours.name           | Rename cho dễ hiểu                        |
| Tour       | destination      | tours                |                                           |
| Tour       | category         | tours                |                                           |
| Tour       | available_slots  | tours                |                                           |
| Financial  | price_per_person | tours.price          | Giá gốc                                   |
| Financial  | total_amount     | bookings.total_price | Giá thực trả                              |
| Calculated | revenue          | Derived              | IF(status = 'confirmed', total_amount, 0) |

---

### Pseudo SQL Join

```sql
SELECT 
    b.booking_id,
    DATE(b.booking_date) as booking_date,
    b.travel_date,
    b.status,
    b.num_people,

    u.user_id,
    u.full_name,
    u.city,

    t.tour_id,
    t.name as tour_name,
    t.destination,
    t.category,
    t.available_slots,
    t.price as price_per_person,

    b.total_price as total_amount,

    CASE 
        WHEN b.status = 'confirmed' THEN b.total_price 
        ELSE 0 
    END as revenue

FROM bookings b
LEFT JOIN users u ON b.user_id = u.user_id
LEFT JOIN tours t ON b.tour_id = t.tour_id
```

---

## 2. KPI LOGIC (SQL CHO MEMBER B)

---

### A. FINANCIAL KPI

#### Revenue by Day

```sql
SELECT 
    booking_date,
    SUM(revenue) as daily_revenue
FROM gold_full_booking_data
GROUP BY booking_date
```

---

#### Revenue by Month

```sql
SELECT 
    date_format(booking_date, 'yyyy-MM') as month,
    SUM(revenue) as monthly_revenue
FROM gold_full_booking_data
GROUP BY month
```

---

#### Growth Rate (MoM - Month over Month)

```sql
SELECT 
    month,
    monthly_revenue,
    (monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month)) 
    / LAG(monthly_revenue) OVER (ORDER BY month) as growth_rate
FROM (
    SELECT 
        date_format(booking_date, 'yyyy-MM') as month,
        SUM(revenue) as monthly_revenue
    FROM gold_full_booking_data
    GROUP BY month
)
```

---

### B. OPERATION KPI

#### Top 5 Tours (Best Seller)

```sql
SELECT 
    tour_name,
    COUNT(booking_id) as total_confirmed
FROM gold_full_booking_data
WHERE status = 'confirmed'
GROUP BY tour_name
ORDER BY total_confirmed DESC
LIMIT 5
```

---

#### Cancellation Rate (%)

```sql
SELECT 
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) * 100.0 
    / COUNT(booking_id) as cancellation_rate
FROM gold_full_booking_data
```

---

## 3. FEATURE ENGINEERING (CHO ML - MEMBER C)

Bổ sung trực tiếp vào Gold Layer:

---

### Is_Peak_Season (Seasonality)

```sql
CASE 
    WHEN MONTH(travel_date) IN (5,6,7,8) THEN 1 
    ELSE 0 
END as is_peak_season
```

---

### Lead Time (Thời gian đặt trước)

```sql
DATEDIFF(travel_date, booking_date) as lead_time
```

---

### Customer Retention (Khách cũ/mới)

```sql
COUNT(booking_id) OVER(PARTITION BY user_id) as customer_retention
```

---

## 4. CHECKLIST CHO LEADER (MEMBER A)

* [ ] **Confirm Schema**

  * Gửi bảng mapping (Section 1) cho Member B

* [ ] **Check Status Data**

  * Đảm bảo `status` có đủ:

    * confirmed
    * cancelled
  * Nếu toàn bộ là `pending` → KPI & ML sẽ **không hoạt động**

* [ ] **Xác nhận KPI Output cho Dashboard**
  Gửi cho Member C:

  * Revenue by Day
  * Revenue by Month
  * Top 5 Tours
  * Cancellation Rate

---

## MỤC TIÊU CUỐI

* Gold Table = **Single Source of Truth**
* Không duplicate
* KPI chạy nhanh trên Databricks
* ML có feature đầy đủ & meaningful

---
