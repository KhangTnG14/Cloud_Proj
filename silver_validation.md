# TOURGO DATA PIPELINE - SILVER LAYER VALIDATION REPORT
**Người thực hiện:** [A] Leader / Business Logic & Validation (Nguyễn Vũ Hà)
**Mục tiêu:** Nghiệm thu, đối soát Business Logic trên tập dữ liệu sạch tầng Silver (đã được xử lý bởi bạn [B]) để làm căn cứ tính toán các bảng KPI tầng Gold (Day 3).

---

## 1. KẾT QUẢ ĐỐI SOÁT CHẤT LƯỢNG DỮ LIỆU THỰC TẾ (QA METRICS)

Dựa trên kết quả thực thi dọn dẹp hệ thống của bạn [B] tại Notebook `02_silver_cleaning.ipynb`, [A] xác nhận toàn bộ dữ liệu thực tế từ SQL Server đã được bảo toàn nguyên vẹn khi đi qua tầng Silver:

* **Bảng so khớp số liệu hệ thống:**
  * `users`: 18 bản ghi gốc -> Giữ nguyên 18 bản ghi sạch (Dropped: 0) - **PASSED**
  * `tours`: 23 bản ghi gốc -> Giữ nguyên 23 bản ghi sạch (Dropped: 0) - **PASSED**
  * `bookings`: 11 bản ghi gốc -> Giữ nguyên 11 bản ghi sạch (Dropped: 0) - **PASSED**
  * `payments`: 10 bản ghi gốc -> Giữ nguyên 10 bản ghi sạch (Dropped: 0) - **PASSED**
  * `revenues`: 4 bản ghi gốc -> Giữ nguyên 4 bản ghi sạch (Dropped: 0) - **PASSED**
  * `reviews`: 1 bản ghi gốc -> Giữ nguyên 1 bản ghi sạch (Dropped: 0) - **PASSED**

* **Đánh giá Business Logic:**
  1. **Luồng Booking & Payment:** Khớp luồng giao dịch Sandbox (~91%). Lệch 1 đơn do hành khách tạo đơn đặt (`bookings`) nhưng chưa thực hiện lệnh thanh toán qua cổng VNPay/VietQR (`payments`). Khung dữ liệu xử lý giữ nguyên thực thể hoàn toàn hợp lệ.
  2. **Toán học Doanh thu:** Đạt độ chính xác tuyệt đối (0 bản ghi lỗi công thức). Biến đổi tính toán `creator_share + admin_share == total_amount` đã được xử lý dung sai số thực (`_abs < 0.01`) chuẩn xác.
  3. **Điều kiện Review:** 100% review trên hệ thống thuộc về khách hàng hợp lệ, không tồn tại review lậu (Dropped = 0).

---

## 2. NHẬT KÝ SỬA LỖI HỆ THỐNG (BUG LOG)
* **Sự cố phát hiện:** Trong lượt chạy đầu tiên, bộ lọc của Spark làm rớt sạch 100% dữ liệu bảng người dùng (`silver_users`: 0/18 records) do xung đột ký tự chữ hoa/chữ thường của trường `role` giữa SQL Server (`Customer`) và điều kiện lọc ban đầu của Spark (`CUSTOMER`).
* **Khắc phục:** [A] đã phát hiện kịp thời và phối hợp cùng [B] chèn hàm chuẩn hóa chuỗi viết hoa `upper(col("role"))`. Hệ thống đã khôi phục nguyên vẹn trạng thái **18/18 người dùng** về tầng Silver thành công.

---

## 3. THÔNG TIN CHUYỂN TIẾP CHO THÀNH VIÊN TIẾP THEO (DAY 3 - GOLD LAYER)

Dữ liệu sạch tầng Silver đã được lưu dưới dạng **Managed Tables** trong database `tourgo`. Thành viên làm Day 3 chỉ cần gọi thẳng database này để tính toán các bảng KPI:

* **Tên Database:** `tourgo`
* **Các bảng sẵn sàng sử dụng:**
  * `tourgo.silver_users`
  * `tourgo.silver_tours`
  * `tourgo.silver_bookings`
  * `tourgo.silver_payments`
  * `tourgo.silver_revenues`
  * `tourgo.silver_reviews`

* **Dữ liệu mẫu cho [D] Khánh cấu hình `streaming_simulator.py`:**
  * `SAMPLE_USER_IDS = []`
  * `SAMPLE_TOUR_IDS = [28, 29, 30, 9, 11, 14, 17, 19, 23, 24]`
  * `SAMPLE_PRICES = [1000000, 2000000, 1500000, 10000000, 70000, 150000, 1231123, 99999]`