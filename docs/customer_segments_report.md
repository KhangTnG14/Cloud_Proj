# Customer Segmentation Report — TourGo

## Dataset Overview
| Metric | Value |
|--------|-------|
| Total Customers | 220 |
| Total Bookings | 916 |
| Confirmed Bookings | 550 (60%) |
| Cancelled Bookings | 188 (20.5%) |
| Total Reviews | 150 |
| Avg Rating | 4.49 / 5 |

---

## Model: K-Means Clustering
| Parameter | Value |
|-----------|-------|
| Algorithm | K-Means (Spark MLlib) |
| Features | 7 features |
| K (clusters) | 4 (chọn bằng Elbow Method) |
| Silhouette Score | X.XX ← điền sau khi [B] train xong |
| Scaler | StandardScaler |

---

## Features sử dụng
| Feature | Mô tả |
|---------|-------|
| total_bookings | Tổng số lần đặt tour |
| confirmed_bookings | Số lần đặt thành công |
| total_spent | Tổng tiền đã chi |
| cancellation_rate | Tỷ lệ hủy tour |
| avg_rating_given | Điểm đánh giá trung bình |
| unique_tours | Số tour khác nhau đã đặt |
| days_active | Số ngày kể từ khi đăng ký |

---

## Cluster Profiles ← điền sau khi [B] train xong

| Cluster | Tên | Size | Avg Bookings | Avg Spent | Cancel Rate | Avg Rating |
|---------|-----|------|-------------|-----------|-------------|------------|
| 0 | Khách VIP | X | X | X VNĐ | X% | X/5 |
| 1 | Khách Tiềm Năng | X | X | X VNĐ | X% | X/5 |
| 2 | Khách Ngủ Đông | X | X | X VNĐ | X% | X/5 |
| 3 | Không Ổn Định | X | X | X VNĐ | X% | X/5 |

---

## Business Insights ← cập nhật sau khi có cluster profiles

- Cụm VIP chiếm X% users nhưng đóng góp X% doanh thu
  → Ưu tiên chăm sóc, gửi ưu đãi đặc biệt

- Cụm Tiềm Năng có booking nhưng chưa chi nhiều
  → Re-engage bằng email marketing, tour giá tốt

- Cụm Ngủ Đông đăng ký lâu nhưng ít đặt
  → Gửi thông báo tour mới, khuyến mãi kích hoạt

- Cụm Không Ổn Định hay hủy tour
  → Review chính sách hoàn tiền, cải thiện trải nghiệm

---

## Cancellation Rate Analysis
- Overall cancel rate: 20.5% (188/916)
- Cluster với cancel rate cao nhất: X% ← điền sau
- Cluster với cancel rate thấp nhất: X% ← điền sau

---

## Recommendation per Segment ← điền sau Ngày 7
| Cluster | Top Tour 1 | Top Tour 2 | Top Tour 3 |
|---------|-----------|-----------|-----------|
| VIP | | | |
| Tiềm Năng | | | |
| Ngủ Đông | | | |
| Không Ổn Định | | | |