# TOURGO Analytics Dashboard Layout

Notebook: `05_dashboard.ipynb`

Mục tiêu: Thiết kế sẵn bố cục Dashboard gồm 8 sections để từ Ngày 3 trở đi có thể điền data, chart và insight vào từng phần.

## Cell 1 - Title

Title: `TOURGO Analytics Dashboard`

Nội dung dự kiến:

- Tên dashboard.
- Thời gian cập nhật dữ liệu.
- Ghi chú nguồn dữ liệu: TourGo real data từ S3/Delta Lake.

## Cell 2 - Section 1: Business Overview

Mục tiêu: Tóm tắt tình hình kinh doanh bằng 4 KPI chính.

KPI đề xuất:

- Tổng doanh thu.
- Tổng số booking.
- Tổng số tour đang/đã mở bán.
- Điểm rating trung bình.

Visual đề xuất:

- 4 KPI cards/databricks display values.
- Bảng nhỏ so sánh theo trạng thái booking nếu cần.

## Cell 3 - Section 2: Revenue Analysis

Mục tiêu: Theo dõi xu hướng doanh thu và đóng góp doanh thu theo nhóm.

Visual đề xuất:

- Line chart: doanh thu theo ngày/tháng.
- Bar chart: doanh thu theo creator/provider hoặc theo category.

Chỉ số cần tính:

- `total_revenue`.
- `creator_share`.
- `admin_share`.
- Revenue growth theo thời gian.

## Cell 4 - Section 3: Tour Performance

Mục tiêu: Xác định tour nào bán tốt, tour nào cần tối ưu.

Visual đề xuất:

- Bar chart: top tours theo doanh thu.
- Bar chart/table: top tours theo số booking hoặc số người tham gia.
- Table chi tiết: title, category, bookings, participants, revenue, avg_rating.

## Cell 5 - Section 4: Payment Analysis

Mục tiêu: Phân tích phương thức thanh toán và trạng thái thanh toán.

Visual đề xuất:

- Pie/donut chart: tỉ lệ payment method.
- Stacked bar/table: payment status theo method.

Chỉ số cần tính:

- Số giao dịch thành công/thất bại/chờ xử lý.
- Tổng amount theo payment_method.

## Cell 6 - Section 5: Customer Segments

Mục tiêu: Hiển thị kết quả phân cụm khách hàng từ mô hình K-Means.

Visual đề xuất:

- Scatter plot: customer segments.
- Bar chart: số user theo từng cluster.
- Table mô tả từng segment: booking_count, total_spent, avg_people, last_booking_date.

## Cell 7 - Section 6: Revenue Forecast

Mục tiêu: So sánh doanh thu thực tế và doanh thu dự báo.

Visual đề xuất:

- Line chart: actual vs predicted revenue.
- KPI/table: MAE, RMSE hoặc MAPE nếu có.

Chỉ số cần tính:

- Actual revenue theo ngày/tháng.
- Predicted revenue theo ngày/tháng.
- Forecast error.

## Cell 8 - Section 8: Anomaly Alerts (Day 8 — [C])

Mục tiêu: Hiển thị các bất thường về doanh thu, booking hoặc tour từ bảng `gold_anomalies` (notebook `04c_anomaly_detection.ipynb`).

Visual đề xuất:

- Table alert: date, anomaly_type, severity, user_id, tour_id, tour_title, value.
- Bar chart: số alert theo severity và theo anomaly_type.

Quy tắc gợi ý:

- Doanh thu giảm/tăng bất thường.
- Payment failed rate cao.
- Booking cancel rate cao.

## Cell 9 - Section 9: Real-Time Streaming Status (Day 9 — [C])

Mục tiêu: Hiển thị counter và bảng booking mới từ `stream_bookings_bronze` (notebook `06_streaming.ipynb`).

Visual đề xuất:

- KPI: tổng booking stream, confirmed/pending, streaming revenue.
- Bar/pie chart: số booking theo `status`.
- Table: 10 booking mới nhất (sort `processed_at` desc).
- Line chart (nếu đủ batch): booking count theo `processed_at`.

Phụ thuộc:

- [D] `streaming_simulator.py` upload JSON lên S3.
- [B] `06_streaming.ipynb` ghi bảng `stream_bookings_bronze`.

## Cell 10 - Section 10: Tour Recommendations (Day 7)

Mục tiêu: Hiển thị gợi ý tour theo cluster từ `ml_tour_recommendations`.

## Checklist Ngày 1 - Phần C

- [x] Có layout dashboard trong `docs/dashboard_layout.md`.
- [x] Có notebook khung `05_dashboard.ipynb`.
- [x] Notebook gồm 9 cells đúng theo plan.
- [x] Mỗi cell có comment mô tả section, sẵn sàng điền code và chart.
