# TOURGO ANALYTICS - EXPORT DATA SCHEMA & INCREMENTAL STRATEGY
[cite_start]**Vai trò thực hiện:** [A] Leader / Business Logic & Validation (Nguyễn Vũ Hà) [cite: 1837]
[cite_start]**Phiên bản:** 2.0 — Incremental Export Architecture [cite: 1712]
[cite_start]**Mục tiêu:** Định nghĩa cấu trúc Schema chuẩn hóa cho 6 phân hệ dữ liệu kết xuất từ SQL Server (Django ORM) sang Amazon S3[cite: 6, 1771, 1775]. [cite_start]Thiết lập chiến lược cập nhật tăng trưởng (Incremental) nhằm tối ưu hóa băng thông, đảm bảo tính vẹn toàn dữ liệu và bảo mật PII[cite: 8, 1735, 1846].

---

## 1. CHIẾN LƯỢC ĐỒNG BỘ DỮ LIỆU (INCREMENTAL STRATEGY)

[cite_start]Để hỗ trợ chu kỳ quét tự động 5 phút/lần của `incremental_export.py`, dữ liệu được phân chia thành 2 cơ chế đồng bộ dựa trên tính chất thay đổi của thực thể[cite: 1729, 1768, 1769]:

| Tên Bảng (Table) | Cơ Chế Đồng Bộ (Mode) | Trường Định Định Vị (Key Field) | Lý Do Kiến Trúc |
| :--- | :--- | :--- | :--- |
| `users` | **Full Sync** (Snapshot) | `date_joined` | Số lượng bản ghi nhỏ. [cite_start]Các trường `role` hoặc `is_active` có khả năng cập nhật trạng thái từ phía Admin[cite: 1847]. |
| `tours` | **Full Sync** (Snapshot) | `created_at` | [cite_start]Trạng thái Tour (`status`) thay đổi liên tục khi Provider chỉnh sửa hoặc được Admin phê duyệt (`pending` → `approved`)[cite: 1847]. |
| `bookings` | **Incremental** (Tăng trưởng) | `created_at` | Thực thể giao dịch tuyến tính. Chỉ phát sinh thêm mới, không có hành vi cập nhật đè (Trạng thái `status` thay đổi được ghi nhận qua log riêng)[cite: 1847]. |
| `payments` | **Incremental** (Tăng trưởng) | `created_at` | [cite_start]Nhật ký tài chính đóng băng ngay sau khi phát sinh giao dịch[cite: 1847]. |
| `revenues` | **Incremental** (Tăng trưởng) | `created_at` | [cite_start]Dữ liệu đối soát dòng tiền cố định sau khi hạch toán thành công[cite: 1847]. |
| `reviews` | **Incremental** (Tăng trưởng) | `created_at` | [cite_start]Hành khách chỉ gửi đánh giá một lần duy nhất sau chuyến đi[cite: 1847]. |

---

## 2. BẢNG CHI TIẾT SCHEMA 6 FILE EXPORT

### 2.1. Bảng `users.csv` (Thông tin người dùng đã ẩn danh)
* [cite_start]Quản lý phân hệ phân cụm hành vi và thâm niên hệ thống[cite: 117].
* [cite_start]*Dữ liệu loại bỏ bảo mật:* `password`, `email`, `phone`, `username`, `avatar`[cite: 118].

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID duy nhất của người dùng |
| `role` | VARCHAR(20) | StringType | NOT NULL | Vai trò hệ thống (`Customer`, `Provider`, `Admin`) |
| `is_active` | BIT | BooleanType | NOT NULL | Trạng thái tài khoản (`True` / `False`) |
| `date_joined` | DATETIME | TimestampType | NOT NULL | Ngày đăng ký hệ thống (Định dạng: `YYYY-MM-DD HH:mm:ss`) |

### 2.2. Bảng `tours.csv` (Thông tin các gói sản phẩm du lịch)
* [cite_start]Phục vụ phân hệ xếp hạng hiệu suất Tour và khai phá thuộc tính danh mục (`category_names`)[cite: 119, 121].

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

### 2.3. Bảng `bookings.csv` (Thông tin giao dịch đặt Tour)
* [cite_start]Đầu não cho phân hệ phễu chuyển đổi (`gold_booking_funnel`) và thuật toán dự báo[cite: 20, 122].

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

### 2.4. Bảng `payments.csv` (Nhật ký giao dịch tài chính)
* [cite_start]Phục vụ phân tích so sánh tỷ lệ phương thức thanh toán (`VietQR` vs `VNPay`)[cite: 24, 123].

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID duy nhất của giao dịch thanh toán |
| `booking_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID đơn đặt chỗ liên kết |
| `amount` | DECIMAL(18,2) | DoubleType | NOT NULL | Số tiền thực tế giao dịch thành công |
| `payment_method` | VARCHAR(20) | StringType | NOT NULL | Phương thức xử lý (`VNPay`, `VietQR`) |
| `status` | VARCHAR(20) | StringType | NOT NULL | Trạng thái cổng thanh toán (`Success`, `Failed`) |
| `created_at` | DATETIME | TimestampType | NOT NULL | Thời gian thực thi giao dịch thành công |

### 2.5. Bảng `revenues.csv` (Báo cáo phân chia dòng tiền thực tế)
* [cite_start]Giám sát hiệu suất doanh thu đối soát dòng tiền và phục vụ thuật toán hồi quy tuyến tính[cite: 43, 124].

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID bảng phân chia doanh thu |
| `payment_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID hóa đơn gốc đối soát |
| `creator_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của Provider nhận tiền |
| `total_amount` | DECIMAL(18,2) | DoubleType | NOT NULL | Tổng dòng tiền nhận về hệ thống sàn |
| `creator_share` | DECIMAL(18,2) | DoubleType | NOT NULL | Số tiền thực tế chia cho Provider |
| `admin_share` | DECIMAL(18,2) | DoubleType | NOT NULL | Phí hoa hồng sàn trích lại cho Admin |
| `created_at` | DATETIME | TimestampType | NOT NULL | Ngày hạch toán dòng tiền thành công |

### 2.6. Bảng `reviews.csv` (Đánh giá và phản hồi chất lượng)
* [cite_start]Phục vụ phân tích phân phối xếp hạng (Rating 1-5 sao)[cite: 24, 125].
* [cite_start]*Dữ liệu loại bỏ bảo mật:* `content` (bỏ văn bản dài để tối ưu hóa hiệu năng lưu trữ)[cite: 126].

| Tên Trường (Field) | Kiểu Dữ Liệu SQL Server | Kiểu Dữ Liệu Spark | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT (Primary Key) | IntegerType | NOT NULL | ID bản ghi đánh giá |
| `user_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của khách hàng đánh giá |
| `tour_id` | INT (Foreign Key) | IntegerType | NOT NULL | ID của Tour được nhận đánh giá |
| `rating` | INT | IntegerType | NOT NULL | Số sao đánh giá tiêu chuẩn (Dải giá trị: `1` đến `5`) |
| `created_at` | DATETIME | TimestampType | NOT NULL | Ngày thực hiện gửi đánh giá lên hệ thống |

---

## 3. QUY CHUẨN ĐỊNH DẠNG TỆP TIN XUẤT KHẨU (CSV CONFIGURATION)
[cite_start]Để bảo đảm tính thống nhất tuyệt đối khi truyền dữ liệu qua AWS S3[cite: 1775, 1786]:
1. **Ký tự phân tách (Delimiter):** Dấu phẩy `,`
2. **Ký tự bao bọc chuỗi (Quote Character):** Dấu nháy kép `"` (Bắt buộc bao bọc trường `title` và `category_names` để tránh lỗi vỡ dòng do dấu phẩy chứa bên trong dữ liệu).
3. [cite_start]**Định dạng Mã hóa (Encoding):** `UTF-8` hoặc `UTF-8-SIG` (Đảm bảo tiếng Việt có dấu hiển thị chuẩn xác trên hệ thống Databricks Spark)[cite: 139, 221].
4. [cite_start]**Cấu trúc lưu trữ trên Cloud Storage (S3 Data Lake Path):** Mỗi chu kỳ chạy thành công, dữ liệu phải được lưu vào các phân khu thư mục định danh bằng mốc thời gian cô lập (`timestamp subfolders`) theo dạng[cite: 1814, 1945]:
   [cite_start]`s3://tourgo-data-lake/raw/{table_name}/{YYYYMMDD_HHMMSS}/data.csv` [cite: 1814, 1945]