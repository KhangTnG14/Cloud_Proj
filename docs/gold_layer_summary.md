# GOLD LAYER DATA ARCHITECTURE & SUMMARY REPORT — TOURGO
**Người thực hiện:** [A] Leader / Business Logic & Validation (Nguyễn Vũ Hà)  
**Phiên bản:** 2.0 — Production Ready (Cập nhật theo Số liệu thực tế hệ thống)  
**Mục tiêu:** Tài liệu hóa cấu trúc dữ liệu tổng hợp tầng Gold (Gold Layer) từ Delta Lake. Làm minh chứng số liệu thực tế phục vụ slide báo cáo phản biện cuối kỳ và cung cấp nguyên liệu đầu vào sạch cho phân hệ Machine Learning.

---

## 1. BẢNG TỔNG KẾT THỰC THỂ DỮ LIỆU TẦNG GOLD (GOLD TABLES METRICS)

Dưới đây là bảng tổng hợp cấu trúc logic và định hướng hiển thị của các bảng Vàng kinh doanh, dựa trên tập dữ liệu thực tế (Real-data) khớp lệnh từ tầng Silver sạch (227 Users, 779 Tours, 1,326 Bookings, 794 Payments, 788 Revenues, 272 Reviews):

| Tên Bảng (Delta Table) | Trạng thái | Thuật toán tổng hợp (PySpark Logic) | Ý Nghĩa Doanh Nghiệp / Chỉ Số Đo Lường | Phân Hệ Tiêu Thụ |
| :--- | :---: | :--- | :--- | :--- |
| `gold_revenue_daily` | ✔️ PASSED | `.groupBy("booking_date")` tính tổng `total_amount`, `creator_share`, `admin_share`. | Doanh thu tổng (GMV), doanh thu thực nhận của đối tác và hoa hồng sàn trích lại phát sinh lũy kế theo từng ngày vận hành. | Biểu đồ doanh thu thời gian (Line Chart), làm dữ liệu huấn luyện cho mô hình Dự báo Doanh thu (Forecasting). |
| `gold_provider_performance` | ✔️ PASSED | `.groupBy("creator_id")` liên kết tổng doanh thu, đếm số đơn trạng thái `confirmed` và tính `avg(rating)`. | Bảng xếp hạng năng lực kinh doanh, hiệu suất đơn hàng thành công và điểm chất lượng dịch vụ của từng đối tác (Provider). | Bảng vinh danh đối tác xuất sắc (Provider Leaderboard), biểu đồ cột doanh thu đối tác (Bar Chart). |
| `gold_tour_performance` | ✔️ PASSED | `.groupBy("tour_id")` liên kết bảng tours tính tổng số khách (`total_travelers`) và doanh thu tích lũy. | Đo lường hiệu suất thương mại của từng mã Tour du lịch để xác định các sản phẩm thu hút dòng tiền tốt nhất hệ thống. | Biểu đồ Top Tour bán chạy nhất (Top Tours Chart), hệ thống gợi ý Tour (Recommendation System). |
| `gold_booking_funnel` | ✔️ PASSED | `.groupBy("status")` chia cho tổng số lượng đơn đặt hàng để tính toán tỷ lệ chuyển đổi phần trăm (%). | Phân tích phễu chuyển đổi trạng thái của đơn hàng theo 3 trạng thái cốt lõi hệ thống: `Pending`, `Confirmed`, `Cancelled`. | Biểu đồ phễu kinh doanh (Funnel Chart), kiểm soát và cảnh báo tỷ lệ hủy đơn bất thường. |
| `gold_payment_analysis` | ✔️ PASSED | `.groupBy("payment_method")` tính tổng số tiền và số lượng giao dịch tương ứng. | Phân tích cơ cấu và thị phần dòng tiền giữa các giải pháp cổng thanh toán tích hợp thực tế: `VNPAY`, `VietQR`, `CASH`, `BANK_TRANSFER`. | Biểu đồ cơ cấu phương thức thanh toán (Pie Chart). |
| `gold_review_summary` | ✔️ PASSED | `.groupBy("rating")` đếm tần suất xuất hiện của các dải điểm từ 1 đến 5 sao. | Đo lường mức độ hài lòng tổng quan và phân phối mật độ trải nghiệm hành khách của toàn sàn thương mại điện tử. | Biểu đồ cột phân phối xếp hạng chất lượng (Rating Distribution Chart). |

---

## 2. BIÊN BẢN KIỂM ĐỊNH TÍNH TOÀN VẸN LOGIC (DATA QUALITY AUDITING)

Thông qua việc đối soát chéo dữ liệu giữa các tầng, [A] Nguyễn Vũ Hà xác nhận hệ thống đạt các tiêu chuẩn chất lượng nghiêm ngặt sau:

1. **Tính nhất quán dòng tiền tài chính:** Toàn bộ dữ liệu doanh thu tầng Gold được bảo toàn chính xác. Logic dọn dẹp tại tầng Silver đã loại bỏ các rủi ro sai số dấu phẩy động bằng hàm trị tuyệt đối dung sai toán học `_abs(col("creator_share") + col("admin_share") - col("total_amount")) < 0.01`, đảm bảo dòng tiền khớp lệnh $100\%$, không xảy ra tình trạng lệch tiền tệ.
2. **Loại bỏ dữ liệu nhạy cảm (PII Compliant):** Quá trình nghiệm thu xác nhận bảng dữ liệu người dùng (`silver_users`) đã được loại bỏ hoàn toàn các trường thông tin cá nhân như mật khẩu, email, số điện thoại để bảo mật danh tính theo đúng chuẩn thiết kế hệ thống.
3. **Làm mịn dữ liệu đánh giá rỗng (Null Handling):** Chỉ số đánh giá trung bình (`avg_rating`) tại bảng hiệu suất đối tác đã được cấu hình xử lý làm mịn bằng hàm làm tròn `_round(..., 2)` và tự động xử lý các giá trị rỗng (`Null`) thành `0.0` đối với các đối tác hoặc gói sản phẩm mới lên sàn chưa có lượt review, giúp giao diện Dashboard hiển thị mượt mà không bị lỗi giao diện.

---

## 3. THÔNG TIN BÀN GIAO PHÂN HỆ TIẾP THEO

* **Đường dẫn cấu trúc Delta Lake tầng Gold trên Cloud Storage:**
  * `dbfs:/mnt/delta/gold/revenue_daily`
  * `dbfs:/mnt/delta/gold/provider_performance`
  * `dbfs:/mnt/delta/gold/tour_performance`
* **Thông tin mảng dữ liệu mẫu thật bàn giao cho [D] Khánh cấu hình `streaming_simulator.py` (Trích xuất từ kết quả Cell 10 của tầng Silver):**
  * `SAMPLE_USER_IDS = [3, 19, 2, 7, 5, 1]`
  * `SAMPLE_TOUR_IDS = [33, 151, 28, 29, 30, 171, 93, 564, 364, 262]`
  * `SAMPLE_PRICES   = [3000000, 1000000, 1500000, 500000, 250000, 350000, 750000, 1231123]`