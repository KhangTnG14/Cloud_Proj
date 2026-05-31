# TOURGO CLOUD ANALYTICS - KPI DATA ARCHITECTURE & GOLD LAYER DEFINITIONS
**Vai trò thực hiện:** [A] Leader / Business Logic & Validation (Nguyễn Vũ Hà)  
**Mục tiêu:** Định nghĩa chính xác công thức toán học, logic lọc dữ liệu và cấu trúc cấu phần cho 4 nhóm chỉ số hiệu suất cốt lõi (KPI) của sàn thương mại điện tử TOURGO. Làm kim chỉ nam cho bạn [B] lập trình tầng Gold và bạn [C] vẽ Dashboard.

---

## 1. ĐẶC TẢ CHI TIẾT 4 CÔNG THỨC KPI CỐT LÕI

### KPI 1: Tổng Doanh Thu Hệ Thống (Platform Revenue Metrics)
* **Mục đích:** Đo lường dòng tiền thực tế chảy qua hệ thống theo thời gian (Ngày/Tháng/Quý).
* **Điều kiện lọc logic:** Chỉ ghi nhận dữ liệu từ bảng `tourgo.silver_revenues` (Do thực thể này chỉ được sinh ra khi giao dịch thanh toán thành công qua cổng VNPay hoặc quét mã VietQR).
* **Công thức toán học:**
  $$\text{Daily GMV} = \sum (\text{revenues.total\_amount})$$
  $$\text{Daily Provider Revenue} = \sum (\text{revenues.creator\_share})$$
  $$\text{Daily Platform Fee} = \sum (\text{revenues.admin\_share})$$
* **Quy ước đồng bộ:** $\text{total\_amount} = \text{creator\_share} + \text{admin\_share}$.

### KPI 2: Hiệu Suất Nhà Cung Cấp (Provider Performance)
* **Mục đích:** Xếp hạng, đánh giá năng lực kinh doanh và chất lượng dịch vụ của từng đối tác (Provider).
* **Công thức toán học theo từng `creator_id`:**
  * **Tổng doanh thu mang lại (GMV):** $\sum(\text{revenues.total\_amount})$
  * **Doanh thu thực nhận của đối tác:** $\sum(\text{revenues.creator\_share})$
  * **Tổng số đơn hàng hoàn tất:** $\text{COUNT}(\text{bookings.id})$ với điều kiện $\text{bookings.status} = \text{'confirmed'}$.
  * **Điểm chất lượng dịch vụ:** $\text{AVG}(\text{reviews.rating})$. *Nếu chưa có lượt đánh giá, mặc định gán giá trị bằng 0.0.*

### KPI 3: Hiệu Suất Gói Sản Phẩm (Tour Performance)
* **Mục đích:** Xác định các sản phẩm Tour "gà đẻ trứng vàng" có doanh thu cao nhất và các Tour được yêu thích nhất để đưa vào mô hình gợi ý (Recommendation System).
* **Công thức toán học theo từng `tour_id`:**
  * **Doanh thu tích lũy của Tour:** $\sum(\text{revenues.total\_amount})$ kết hợp (JOIN) qua bảng `bookings` dựa trên trường `tour_id`.
  * **Tổng số lượng hành khách đã phục vụ:** $\sum(\text{bookings.number\_of\_people})$ với trạng thái `confirmed`.
  * **Chỉ số đánh giá trung bình:** $\text{AVG}(\text{reviews.rating})$.

### KPI 4: Phễu Chuyển Đổi Đơn Hàng (Booking Funnel Rate)
* **Mục đích:** Phân tích hành vi người dùng, đo lường tỷ lệ giữ chân khách hàng và phát hiện bất thường nếu tỷ lệ hủy đơn tăng cao đột biến.
* **Công thức toán học:**
  $$\text{Total Bookings} = \text{COUNT}(\text{bookings.id})$$
  $$\text{Tỷ lệ đặt tour thành công (Confirmed Rate)} = \frac{\text{COUNT}(\text{bookings với status = 'confirmed'})}{\text{Total Bookings}} \times 100\%$$
  $$\text{Tỷ lệ khách hủy tour (Cancelled Rate)} = \frac{\text{COUNT}(\text{bookings với status = 'cancelled'})}{\text{Total Bookings}} \times 100\%$$
  $$\text{Tỷ lệ đơn chờ xử lý (Pending Rate)} = \frac{\text{COUNT}(\text{bookings với status = 'pending'})}{\text{Total Bookings}} \times 100\%$$

---

## 2. ÁNH XẠ CẤU TRÚC ĐẦU RA TẦNG GOLD (GOLD DELTA TABLES TARGET)

Để phục vụ trực quan hóa dữ liệu cho Dashboard của bạn [C], [A] thống nhất cấu trúc 3 bảng đầu ra tầng Gold yêu cầu [B] khởi tạo chính xác:

### 2.1. Bảng `tourgo.gold_revenue_daily`
* **Các cột cấu trúc:** `booking_date` (Date), `total_revenue` (Double), `provider_revenue` (Double), `platform_fee` (Double), `num_transactions` (Integer), `month` (String).

### 2.2. Bảng `tourgo.gold_provider_performance`
* **Các cột cấu trúc:** `creator_id` (Integer), `total_provider_revenue` (Double), `total_gmv` (Double), `total_confirmed_bookings` (Integer), `active_tours_count` (Integer), `avg_rating` (Double).

### 2.3. Bảng `tourgo.gold_tour_performance`
* **Các cột cấu trúc:** `tour_id` (Integer), `title` (String), `price` (Double), `category_names` (String), `total_bookings` (Integer), `total_revenue` (Double), `total_travelers` (Integer), `avg_rating` (Double), `review_count` (Integer).