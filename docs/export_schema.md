# TOURGO ANALYTICS - EXPORT DATA SCHEMA ARCHITECTURE
**Vai trò thực hiện:** [A] Leader / Business Logic & Validation (Nguyễn Vũ Hà)  
**Mục tiêu:** Định nghĩa cấu trúc Schema chuẩn hóa cho 6 file dữ liệu CSV xuất từ hệ thống Web TOURGO sang môi trường Big Data Databricks. Loại bỏ hoàn toàn dữ liệu nhạy cảm (PII) đảm bảo tính bảo mật.

---

## 1. BẢNG CHI TIẾT SCHEMA 6 FILE EXPORT

### 1.1. Bảng `users.csv` (Thông tin người dùng đã ẩn danh)
* Quản lý phân hệ phân cụm hành vi và thâm niên hệ thống.
* *Dữ liệu loại bỏ bảo mật:* `password`, `email`, `phone`, `username`, `avatar`.

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID duy nhất của người dùng |
| `role` | VARCHAR(20) | StringType | NOT NULL | Vai trò hệ thống (`Customer`, `Provider`, `Admin`) |
| `is_active` | BIT | BooleanType | NOT NULL | Trạng thái tài khoản (`True` / `False`) |
| `date_joined` | DATETIME | TimestampType | NOT NULL | Ngày đăng ký hệ thống (Định dạng: `YYYY-MM-DD HH:mm:ss`) |

### 1.2. Bảng `tours.csv` (Thông tin các gói sản phẩm du lịch)
* Phục vụ phân hệ xếp hạng hiệu suất Tour và khai phá thuộc tính danh mục (`category_names`).

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID duy nhất của Tour |
| `creator_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của Provider sở hữu và tạo tour |
| `title` | NVARCHAR(255) | StringType | NOT NULL | Tên gọi của Tour du lịch |
| `price` | DECIMAL(18,2) | DoubleType | NOT NULL | Đơn giá trọn gói của Tour |
| `departure_date` | DATE | DateType | NOT NULL | Ngày khởi hành chính thức (`YYYY-MM-DD`) |
| `slots` | INT | IntegerType | NOT NULL | Số lượng chỗ (vé) tối đa mở bán |
| `status` | VARCHAR(20) | StringType | NOT NULL | Trạng thái hoạt động (`Active`, `Inactive`) |
| `created_at` | DATETIME | TimestampType | NOT NULL | Ngày đăng tải hệ thống |
| `category_names` | NVARCHAR(MAX) | StringType | NULLABLE | Chuỗi danh mục gộp từ quan hệ M2M (Ví dụ: `"Biển,Núi"`) |

### 1.3. Bảng `bookings.csv` (Thông tin giao dịch đặt Tour)
* Đầu não cho phân hệ phễu chuyển đổi (`gold_booking_funnel`) và thuật toán dự báo.

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID duy nhất của Đơn đặt tour |
| `user_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của khách hàng đặt chỗ |
| `tour_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của Tour được đặt |
| `number_of_people` | INT | IntegerType | NOT NULL | Số lượng khách tham gia trong đơn đặt |
| `total_price` | DECIMAL(18,2) | DoubleType | NOT NULL | Tổng giá trị đơn hàng toán học |
| `booking_date` | DATE | DateType | NOT NULL | Ngày thực hiện đặt đơn (`YYYY-MM-DD`) |
| `status` | VARCHAR(20) | StringType | NOT NULL | Trạng thái đơn (`Pending`, `Confirmed`, `Cancelled`) |
| `created_at` | DATETIME | TimestampType | NOT NULL | Thời gian hệ thống ghi nhận tạo đơn |

### 1.4. Bảng `payments.csv` (Nhật ký giao dịch tài chính)
* Phục vụ phân tích so sánh tỷ lệ phương thức thanh toán (`VietQR` vs `VNPay`).

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID duy nhất của giao dịch thanh toán |
| `booking_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID đơn đặt chỗ liên kết |
| `amount` | DECIMAL(18,2) | DoubleType | NOT NULL | Số tiền thực tế giao dịch thành công |
| `payment_method` | VARCHAR(20) | StringType | NOT NULL | Phương thức xử lý (`VNPay`, `VietQR`) |
| `status` | VARCHAR(20) | StringType | NOT NULL | Trạng thái cổng thanh toán (`Success`, `Failed`) |
| `created_at` | DATETIME | TimestampType | NOT NULL | Thời gian thực thi giao dịch thành công |

### 1.5. Bảng `revenues.csv` (Báo cáo phân chia dòng tiền thực tế)
* Cực kỳ quan trọng để giám sát hiệu suất doanh thu đối soát dòng tiền và thuật toán hồi quy tuyến tính.

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID bảng phân chia doanh thu |
| `payment_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID hóa đơn gốc đối soát |
| `creator_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của Provider nhận tiền |
| `total_amount` | DECIMAL(18,2) | DoubleType | NOT NULL | Tổng dòng tiền nhận về hệ thống sàn |
| `creator_share` | DECIMAL(18,2) | DoubleType | NOT NULL | Số tiền thực tế chia cho Provider |
| `admin_share` | DECIMAL(18,2) | DoubleType | NOT NULL | Phí hoa hồng sàn trích lại cho Admin |
| `created_at` | DATETIME | TimestampType | NOT NULL | Ngày hạch toán dòng tiền thành công |

### 1.6. Bảng `reviews.csv` (Đánh giá và phản hồi chất lượng)
* Phục vụ phân tích phân phối xếp hạng (Rating 1-5 sao).
* *Dữ liệu loại bỏ bảo mật:* `content` (bỏ text dài để tối ưu hóa không gian lưu trữ Analytics).

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID bản ghi đánh giá |
| `user_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của khách hàng đánh giá |
| `tour_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của Tour được nhận đánh giá |
| `rating` | INT | IntegerType | NOT NULL | Số sao đánh giá tiêu chuẩn (Dải giá trị: `1` đến `5`) |
| `created_at` | DATETIME | TimestampType | NOT NULL | Ngày thực hiện gửi đánh giá lên hệ thống |

---

## 2. QUY CHUẨN ĐỊNH DẠNG TỆP TIN XUẤT KHẨU (CSV CONFIGURATION)
Để bảo đảm tính thống nhất tuyệt đối khi truyền dữ liệu qua AWS S3:
1. **Ký tự phân tách (Delimiter):** Dấu phẩy `,` 
2. **Ký tự bao bọc chuỗi (Quote Character):** Dấu nháy kép `"` (Bắt buộc bao bọc trường `title` và `category_names` để tránh lỗi vỡ dòng do dấu phẩy chứa bên trong dữ liệu).
3. **Định dạng Mã hóa (Encoding):** `UTF-8` (Đảm bảo tiếng Việt có dấu của trường `title` và `category_names` hiển thị chuẩn xác).
4. **Dòng đầu tiên (Header):** Bắt buộc phải chứa chính xác tên cột như định nghĩa ở Mục 1.