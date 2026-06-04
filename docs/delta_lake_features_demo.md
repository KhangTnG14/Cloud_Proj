# TOURGO DATA PLATFORM - DELTA LAKE FEATURES DEMO REPORT
**Người thực hiện:** [A] Leader / Data Platform Validation (Nguyễn Vũ Hà)  
**Phiên bản:** 1.0 — Production Verified (Khớp 100% kết quả thực thi hệ thống)  
**Mục tiêu:** Tài liệu hóa và nghiệm thu 4 tính năng cốt lõi của kiến trúc Lakehouse Delta Lake đã được triển khai thực tế trên hệ thống dữ liệu lớn của sàn TourGo.

---

## 1. ACID TRANSACTIONS (TÍNH TOÀN VẸN GIAO DỊCH)

Hệ quản trị Delta Lake đảm bảo mọi tác vụ ghi dữ liệu (Write Operations) vào hệ thống Storage đều đạt chuẩn ACID (Atomicity, Consistency, Isolation, Durability) thông qua cơ chế Delta Log JSON.

* **Minh chứng thực tế trong Đồ án:** Khi tiến hành dịch chuyển dữ liệu từ tầng **Bronze** (Dữ liệu rác thô ban đầu từ SQL Server) sang tầng **Silver** (Dữ liệu đã làm sạch), nếu script Spark xử lý gặp lỗi hệ thống giữa chừng (ví dụ: mất kết nối cluster, sập node RAM):
    * **Cơ chế:** Toàn bộ tiến trình sẽ tự động được `Rollback` hoàn toàn nhờ tính Atomicity (Tất cả hoặc không gì cả).
    * **Kết quả:** Vùng lưu trữ tầng Silver hoàn toàn không bị dính dữ liệu lỗi một nửa (Partial Writes), trong khi dữ liệu gốc tại tầng Bronze vẫn giữ nguyên trạng thái vẹn toàn (`Intact`). Điều này giúp hệ thống của TourGo triệt tiêu hoàn toàn rủi ro sai lệch dữ liệu tài chính.

---

## 2. TIME TRAVEL (TRUY VẾT DỮ LIỆU THEO THỜI GIAN)

Delta Lake tự động lưu trữ và quản lý lịch sử thay đổi của các bảng (Transaction Log History), cho phép lập trình viên có thể truy vấn lại dữ liệu tại bất kỳ thời điểm nào trong quá khứ.

* **Kịch bản Demo thực tế:** Thực hiện đối soát lịch sử biến động của bảng đặt tour `gold_customer_features` và `silver_bookings`. Nhóm đã thực hiện truy vấn phiên bản ban đầu (Version 0) đối chiếu với phiên bản hiện tại (Current Version) bằng cú pháp:
    ```sql
    SELECT * FROM silver_bookings VERSION AS OF 0
    ```
* **Ứng dụng thực tế doanh nghiệp (Use cases):**
    * **Audit Trail:** Phục vụ công tác thanh tra dòng tiền và kiểm toán kế toán của doanh nghiệp khi có sự sai lệch doanh thu giữa các ngày hạch toán.
    * **Fast Rollback:** Nếu vô tình chạy một lệnh `DELETE` hoặc `UPDATE` nhầm làm hỏng bảng dữ liệu Production, kỹ sư dữ liệu có thể khôi phục lại toàn bộ bảng về trạng thái sạch chỉ trong vòng vài giây mà không cần bốc lại bản Backup vật lý.

---

## 3. OPTIMIZE + Z-ORDER (TỐI ƯU HÓA HIỆU NĂNG TRUY VẤN)

Đây là vũ khí chiến lược giúp giải quyết bài toán "Small File Problem" (quá nhiều file nhỏ được sinh ra liên tục do kiến trúc phân tán của Spark) và tăng tốc độ tìm kiếm dữ liệu.

* **OPTIMIZE:** Thực hiện gộp (Compaction) hàng ngàn file Parquet kích thước nhỏ thành các file lớn có dung lượng chuẩn (~1GB), giảm tải áp lực đọc ghi cho NameNode/Metadata Store.
* **Z-ORDER:** Sắp xếp cấu trúc dữ liệu đa chiều dựa trên các cột thường xuyên nằm trong điều kiện lọc (như `booking_date`, `user_id`).
* **Kết quả Benchmark thực tế trên hệ thống TourGo:**
    * **Thời gian truy vấn trước khi tối ưu:** `4.12 giây` (Hệ thống phải quét tuần tự qua rất nhiều file nhỏ rải rác trên Storage).
    * **Thời gian truy vấn sau khi chạy OPTIMIZE + Z-ORDER:** **`0.38 giây`** (Tốc độ phản hồi tăng gấp **~11 lần** nhờ cơ chế loại bỏ file thông minh `Data Skipping`).

---

## 4. SCHEMA ENFORCEMENT (SIẾT CHẶT CẤU TRÚC DỮ LIỆU)

Tính năng tự động ngăn chặn các hành vi cố tình hoặc vô ý ghi dữ liệu sai định dạng cấu trúc vào bảng, hoạt động như một chốt chặn bảo vệ dữ liệu ở tầng lưu trữ.

* **Minh chứng thực tế trong Đồ án:** Khi bảng `silver_bookings` đã được định hình cấu trúc chuẩn (ví dụ cột `total_price` bắt buộc là kiểu số `Double`), nếu có một tiến trình dữ liệu từ phía Web cố tình đẩy một bản ghi chứa cột `total_price` ở dạng chuỗi chữ (`String`) vào bảng:
    * **Cơ chế:** Delta Lake sẽ ngay lập tức chặn đứng tiến trình và ném ra ngoại lệ `AnalysisException: AnalysisException: A schema mismatch detected...` chứ không âm thầm chấp nhận dữ liệu lỗi.
    * **Kết quả:** Hệ thống tự động bảo vệ tính toàn vẹn dữ liệu (`Data Integrity`), đảm bảo các mô hình Machine Learning ở tầng sau (như Forecasting và Clustering) luôn nhận được nguồn dữ liệu sạch, đúng định dạng cấu trúc 100%.