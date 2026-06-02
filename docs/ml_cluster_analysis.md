# TOURGO CUSTOMER SEGMENTATION - K-MEANS CLUSTERING ANALYSIS REPORT

**Người thực hiện:** [A] Leader / Business Logic & Validation (Nguyễn Vũ Hà)  
**Phiên bản:** 2.0 — Production Ready (Đối soát thực tế theo Log hệ thống TourGo)  
**Mục tiêu:** Báo cáo luận cứ chọn K tối ưu, định danh nhãn phân khúc kinh doanh cho 4 cụm khách hàng thực tế và đề xuất chiến lược tiếp thị cá nhân hóa phục vụ slide báo cáo cuối kỳ.

---

## 1. LUẬN CỨ TOÁN HỌC CHỌN K TỐI ƯU (ELBOW & SILHOUETTE VALIDATION)

Dựa trên kết quả khảo nghiệm huấn luyện mô hình tuần tự với dải tham số $K \in [2, 8]$ thực thi bởi phân hệ Data Science, [A] Nguyễn Vũ Hà phê duyệt giá trị **$K = 4$** làm cấu hình phân cụm chính thức cho hệ thống với các minh chứng khoa học sau:

1. **Chỉ số Silhouette Score:** Đạt mốc tối ưu phân ranh giới không gian vector rõ nét, các cụm dữ liệu có khoảng cách nội tại cô lập tốt, không xuất hiện hiện tượng chồng lấn hoặc nhiễu loạn phân phối hành vi.
2. **Độ dốc Inertia (Phương pháp Elbow):** Điểm gãy hình học xuất hiện rõ ràng nhất tại vị trí $K = 4$. Sau mốc này, tốc độ giảm sai số bình phương tối thiểu (Inertia) bắt đầu chậm lại tuyến tính, chứng minh việc tăng thêm cụm không đem lại thêm giá trị phân hóa hành vi.
3. **Mục tiêu tối ưu hóa doanh nghiệp:** Phân tách thành 4 phân khúc phản ánh đúng diện mạo thực tế về sức mua, độ tin cậy và thâm niên của toàn bộ tệp khách hàng hoạt động trên sàn TourGo.

---

## 2. ĐỊNH DANH CHI TIẾT ĐẶC ĐIỂM CÁC CỤM THEO SỐ LIỆU THỰC TẾ TOURGO

Thứ tự số thứ tự cụm (Prediction ID) được định danh nghiêm ngặt dựa trên bảng thống kê profile thực tế thu được sau khi kết thúc thuật toán huấn luyện:

### ⚠️ Cụm 0: Khách Hàng Rủi Ro Cao / Không Ổn Định (High-Risk Spammers)

- **Quy mô phân khúc:** 22 khách hàng.
- **Đặc điểm chỉ số thực tế:** Tần suất click đặt tour rất cao ($\text{mean} = 16.27$ đơn) nhưng **tỷ lệ hủy đơn vô cùng đáng báo động ($54.4\%$)**. Do hủy quá nửa số lượng đơn nên tổng chi tiêu thực tế tích lũy bị đọng lại ở mức thấp ($\text{mean} = 40,683,181$ VNĐ).
- **Ý nghĩa doanh nghiệp:** Nhóm khách hàng có hành vi không ổn định, chuyên giữ chỗ ảo gây lãng phí tài nguyên và rủi ro gián đoạn vận hành cho các nhà cung ứng Tour (Provider).

### 🌱 Cụm 1: Khách Hàng Mới Tiềm Năng (Promising Newcomers)

- **Quy mô phân khúc:** 30 khách hàng.
- **Đặc điểm chỉ số thực tế:** Số lượng đơn đặt ở mức vừa phải ($\text{mean} = 7.57$ đơn), chi tiêu trung bình đạt $35,035,000$ VNĐ. Điểm sáng lớn nhất là **tỷ lệ hủy đơn thấp nhất toàn hệ thống (chỉ $10.7\%$)**.
- **Ý nghĩa doanh nghiệp:** Nhóm tài khoản mới hoạt động cực kỳ nghiêm túc và có độ tin cậy cao, là lực lượng nòng cốt cần tập trung kích cầu tương tác.

### 💤 Cụm 2: Khách Hàng Ngủ Đông (Dormant Users)

- **Quy mô phân khúc:** 27 khách hàng.
- **Đặc điểm chỉ số thực tế:** Thâm niên tài khoản cao nhưng tần suất hoạt động giảm sút. Mức chi tiêu đọng lại ở mức trung bình khá ($41,725,185$ VNĐ), lượng tour trải nghiệm ít phong phú hơn các cụm khác.
- **Ý nghĩa doanh nghiệp:** Nhóm khách hàng cũ đang có dấu hiệu giảm tương tác hoặc chuẩn bị rời bỏ nền tảng sang đối thủ cạnh tranh.

### 🏆 Cụm 3: Khách Hàng VIP (High-Value Loyalists)

- **Quy mô phân khúc:** 32 khách hàng.
- **Đặc điểm chỉ số thực tế:** Số đơn đặt hàng rất cao ($\text{mean} = 15.66$ đơn), lượng chi tiêu tài chính đứng đầu toàn sàn ($\text{mean} = 78,131,250$ VNĐ/khách). Tỷ lệ hủy đơn duy trì ở mức rất an toàn ($12.5\%$).
- **Ý nghĩa doanh nghiệp:** Đây là nhóm khách hàng tinh hoa, trung thành, mang lại nguồn doanh thu cốt lõi và dòng tiền ổn định nhất cho TourGo.

---

## 3. ĐỀ XUẤT CHIẾN LƯỢC KINH DOANH CÁ NHÂN HÓA (ACTIONABLE INSIGHTS)

Từ kết quả phân cụm thực tế trên, [A] Nguyễn Vũ Hà đề xuất ban quản trị TourGo áp dụng các chương trình tiếp thị tự động hóa (Marketing Automation):

1. **Đối với cụm Khách VIP (Cụm 3):** Áp dụng ngay chính sách thẻ thành viên kim cương, tặng mã giảm giá phòng chờ thương gia, ưu tiên giữ chỗ tự động không cần đặt cọc trước và phân phối độc quyền các gói Tour hạng sang (Luxury Tours).
2. **Đối với cụm Khách Tiềm Năng (Cụm 1):** Gửi các chiến dịch Email Marketing tặng voucher giảm giá $10\%$ cho lượt đặt tour tiếp theo để kích hoạt tần suất mua hàng, thúc đẩy họ gia tăng chi tiêu.
3. **Đối với cụm Khách Ngủ Đông (Cụm 2):** Triển khai chiến dịch remarketing "We Miss You", tặng quà tri ân thâm niên hoặc khảo sát lý do ngừng tương tác để cải tiến chất lượng dịch vụ.
4. **Đối với cụm Khách Rủi Ro Cao (Cụm 0):** **Siết chặt quy trình vận hành**. Hệ thống tự động áp dụng cơ chế bắt buộc thanh toán đặt cọc trực tuyến tối thiểu $30\%$ qua VNPay/VietQR đối với các tài khoản thuộc cụm này thì mới cho phép xác nhận giữ chỗ Tour, nhằm giảm thiểu tối đa tỷ lệ hủy đơn ảo.
