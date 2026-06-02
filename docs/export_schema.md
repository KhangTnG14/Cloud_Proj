# TOURGO ANALYTICS - EXPORT DATA SCHEMA ARCHITECTURE
**Vai trò thực hiện:** [A] Leader / Business Logic & Validation (Nguyễn Vũ Hà)  
**Phiên bản:** 3.0 — Production Ready & ML Ready (Verified)  
**Mục tiêu:** Định nghĩa cấu trúc Schema chuẩn hóa cho 6 file dữ liệu CSV xuất từ hệ thống Web TOURGO sang môi trường Big Data Databricks. Loại bỏ hoàn toàn dữ liệu nhạy cảm (PII) đảm bảo tính bảo mật và toàn vẹn tài chính.

---

## GLOBAL STANDARDS

* **Timezone:** Toàn bộ các trường mốc thời gian áp dụng chuẩn: `Asia/Ho_Chi_Minh (UTC+7)`
* **Enum Convention:** Toàn bộ các giá trị phân loại danh mục (Enum) bắt buộc viết hoa đồng nhất: `CUSTOMER`, `PROVIDER`, `ADMIN`, `PENDING`, `CONFIRMED`, `CANCELLED`, `ACTIVE`, `INACTIVE`, `SUCCESS`, `FAILED`, `AWAITING_ADMIN`.
* **CSV Export Configuration:**
  * Encoding: `UTF-8` (Bảo toàn tiếng Việt có dấu).
  * Delimiter: Dấu phẩy `,`
  * Quote Character: Dấu nháy kép `"` (Bắt buộc bao bọc trường chuỗi ký tự).
  * Header: Bắt buộc cấu hình dòng đầu tiên chứa tên trường.
  * Null Value: Biểu diễn bằng chuỗi rỗng (Empty String).

---

## 1. CHI TIẾT SCHEMA 6 FILE EXPORT DỮ LIỆU THÔ

### 1.1. Bảng `users.csv`
* **Mục đích:** Phục vụ phân hệ phân cụm hành vi khách hàng (Machine Learning) và phân tích thâm niên tài khoản.
* *Dữ liệu loại bỏ bảo mật (PII Stripped):* `email`, `phone`, `password`, `username`, `avatar`.

| Field | SQL Type | Spark Type | Constraint | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | IntegerType | PK, NOT NULL | ID duy nhất định danh người dùng |
| `role` | VARCHAR(20) | StringType | CUSTOMER / PROVIDER / ADMIN | Vai trò phân quyền trên hệ thống |
| `is_active` | BIT | BooleanType | NOT NULL | Trạng thái tài khoản hoạt động (`True` / `False`) |
| `date_joined` | DATETIME | TimestampType | NOT NULL | Ngày giờ tài khoản đăng ký gia nhập hệ thống |

### 1.2. Bảng `tours.csv`
* **Mục đích:** Phục vụ phân tích hiệu suất sản phẩm Tour, năng lực kinh doanh đối tác và hệ thống gợi ý (Recommendation System).
* **Business Rule:** Trường `creator_id` bắt buộc phải tham chiếu đến một `user_id` có `role = 'PROVIDER'`.
* **Category Format:** Phân tách các danh mục bằng Delimiter nội bộ là dấu gạch đứng `|` (Ví dụ: `Biển\|Núi\|Sinh thái`).

| Field | SQL Type | Spark Type | Constraint | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | IntegerType | PK, NOT NULL | ID duy nhất định danh Tour du lịch |
| `creator_id` | INT | IntegerType | FK → users.id | ID của đối tác (Provider) sở hữu và tạo gói Tour |
| `title` | NVARCHAR(255) | StringType | NOT NULL | Tên gọi hiển thị của Tour du lịch |
| `price` | DECIMAL(18,2) | DecimalType(18,2) | NOT NULL | Đơn giá trọn gói mở bán của Tour |
| `departure_date` | DATE | DateType | NOT NULL | Ngày khởi hành chính thức của chuyến đi |
| `slots` | INT | IntegerType | > 0, NOT NULL | Số lượng chỗ (vé) tối đa mở bán cho Tour |
| `status` | VARCHAR(20) | StringType | approved/pending/cancelled| Trạng thái hiển thị đóng/mở bán gói Tour |
| `created_at` | DATETIME | TimestampType | NOT NULL | Ngày giờ gói Tour được phê duyệt lên sàn |
| `category_names` | NVARCHAR(MAX) | StringType | NULLABLE | Chuỗi gộp danh mục chủ đề của Tour |

### 1.3. Bảng `bookings.csv`
* **Mục đích:** Đầu não phân tích phễu chuyển đổi đơn hàng (Booking Funnel), hạch toán doanh thu và dự báo xu hướng.
* **Business Rule:** Trường `user_id` bắt buộc phải tham chiếu đến một `user_id` có `role = 'CUSTOMER'`.

| Field | SQL Type | Spark Type | Constraint | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | IntegerType | PK, NOT NULL | ID duy nhất định danh đơn đặt Tour |
| `user_id` | INT | IntegerType | FK → users.id | ID của tài khoản khách hàng thực hiện đặt đơn |
| `tour_id` | INT | IntegerType | FK → tours.id | ID của gói Tour du lịch được lựa chọn đặt |
| `number_of_people` | INT | IntegerType | > 0, NOT NULL | Số lượng hành khách đăng ký tham gia trong đơn |
| `total_price` | DECIMAL(18,2) | DecimalType(18,2) | >= 0, NOT NULL | Tổng giá trị hóa đơn thô tính toán toán học |
| `booking_date` | DATE | DateType | NOT NULL | Ngày hành khách sử dụng dịch vụ/khởi hành thực tế |
| `status` | VARCHAR(20) | StringType | **APPROVED / PENDING / CANCELLED** | Trạng thái kiểm duyệt và hiển thị gói Tour (`approved`: Đang mở bán, `pending`: Chờ Admin   duyệt`cancelled`: Ẩn/Hủy bán) |
| `created_at` | DATETIME | TimestampType | NOT NULL | Mốc thời gian thực tế hệ thống ghi nhận tạo đơn |

### 1.4. Bảng `payments.csv`
* **Mục đích:** Phục vụ phân tích dòng tiền vào, đo lường thị phần giữa các giải pháp và cổng kết nối thanh toán.

| Field | SQL Type | Spark Type | Constraint | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | IntegerType | PK, NOT NULL | ID duy nhất định danh giao dịch tài chính |
| `booking_id` | INT | IntegerType | FK → bookings.id | ID của đơn đặt Tour liên kết đối chiếu luồng |
| `amount` | DECIMAL(18,2) | DecimalType(18,2) | >= 0, NOT NULL | Số tiền thực tế ghi nhận giao dịch thành công |
| `payment_method` | VARCHAR(20) | StringType | NOT NULL | Cổng xử lý: `VNPAY` / `VIETQR` / `CASH` / `BANK_TRANSFER` |
| `status` | VARCHAR(20) | StringType | NOT NULL | Trạng thái cổng: `SUCCESS` / `FAILED` / `AWAITING_ADMIN` |
| `created_at` | DATETIME | TimestampType | NOT NULL | Thời gian thực tế ghi nhận luồng tiền thanh toán |

### 1.5. Bảng `revenues.csv`
* **Mục đích:** Phục vụ báo cáo tài chính doanh nghiệp, đo lường tăng trưởng và phân tích hiệu suất nhà cung ứng.
* **Business Rule:** Đảm bảo cân bằng toán học dòng tiền tuyệt đối: `creator_share + admin_share = total_amount`.

| Field | SQL Type | Spark Type | Constraint | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | IntegerType | PK, NOT NULL | ID duy nhất của bảng phân chia doanh thu |
| `payment_id` | INT | IntegerType | FK → payments.id | ID của hóa đơn tài chính gốc đối soát dòng tiền vào |
| `creator_id` | INT | IntegerType | FK → users.id | ID của đối tác (Provider) thụ hưởng nhận tiền chia sẻ |
| `total_amount` | DECIMAL(18,2) | DecimalType(18,2) | >= 0, NOT NULL | Tổng dòng tiền gốc nhận về hệ thống sàn từ hóa đơn |
| `creator_share` | DECIMAL(18,2) | DecimalType(18,2) | >= 0, NOT NULL | Số tiền thực tế trích chi trả chuyển vào ví Provider |
| `admin_share` | DECIMAL(18,2) | DecimalType(18,2) | >= 0, NOT NULL | Phí hoa hồng sàn khấu trừ giữ lại cho quản trị Admin |
| `created_at` | DATETIME | TimestampType | NOT NULL | Mốc thời gian phát sinh bản ghi phân chia doanh thu thực tế(sau khi thanh toán được xác nhận thành công)|

### 1.6. Bảng `reviews.csv`

* **Mục đích:** Đo lường chỉ số hài lòng của khách hàng (CSAT) và đánh giá chất lượng sản phẩm Tour phục vụ bài toán Machine Learning (Recommendation System).
* *Dữ liệu loại bỏ bảo mật (PII Stripped):* `content` (Loại bỏ văn bản dài để tối ưu không gian lưu trữ và tốc độ tính toán).
* **Business Rules (Ràng buộc nghiệp vụ nghiêm ngặt):**
  1. **Đối tượng hợp lệ:** Chỉ người dùng có `role = 'CUSTOMER'` mới được quyền gửi đánh giá.
  2. **Điều kiện đơn hàng:** Chỉ những `booking_id` có trạng thái `CONFIRMED` và giao dịch tài chính thành công (`payments.status = 'SUCCESS'`) mới được phép tồn tại bản ghi review tương ứng.
  3. **Ràng buộc duy nhất:** Một đơn đặt hàng (`booking_id`) chỉ được phép xuất hiện tối đa một lần duy nhất trong bảng này (`booking_id` mang ràng buộc `UNIQUE`).
  4. **Logic dòng thời gian (Timeline):** Mốc thời gian đánh giá (`reviews.created_at`) bắt buộc phải xảy ra **SAU HOẶC BẰNG** ngày khởi hành thực tế của chuyến đi (`bookings.booking_date`).

| Field | SQL Type | Spark Type | Constraint | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | IntegerType | PK, NOT NULL | ID duy nhất định danh bản ghi đánh giá |
| `booking_id` | INT | IntegerType | FK → bookings.id, UNIQUE | ID đơn đặt Tour liên kết. Khóa cứng quy tắc: mỗi đơn chỉ được đánh giá tối đa 1 lần. |
| `user_id` | INT | IntegerType | FK → users.id | ID của khách hàng viết đánh giá (Bắt buộc phải trùng khớp với `user_id` trong bảng `bookings` của đơn đó). |
| `tour_id` | INT | IntegerType | FK → tours.id | ID của gói Tour nhận đánh giá (Bắt buộc phải trùng khớp với `tour_id` trong bảng `bookings` của đơn đó). |
| `rating` | INT | IntegerType | NOT NULL (1–5) | Số sao đánh giá tiêu chuẩn chất lượng dịch vụ (Chỉ nhận dải số nguyên từ `1` đến `5`). |
| `created_at` | DATETIME | TimestampType | NOT NULL | Ngày giờ khách gửi đánh giá (Đảm bảo điều kiện thiết lập: `reviews.created_at >= bookings.booking_date`). |
---

## 2. SƠ ĐỒ MỐI QUAN HỆ KIẾN TRÚC DỮ LIỆU (RELATIONSHIP DIAGRAM)

```text
users
 │
├── tours.creator_id (Chỉ lọc Role = PROVIDER)
 ├── bookings.user_id (Chỉ lọc Role = CUSTOMER)
 ├── revenues.creator_id
 └── reviews.user_id

tours
 │
 ├── bookings.tour_id
 └── reviews.tour_id

bookings
 │
 ├── payments.booking_id
 └── reviews.booking_id (Ràng buộc UNIQUE)

payments
 │
 └── revenues.payment_id