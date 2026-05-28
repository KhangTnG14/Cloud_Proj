import React, { useEffect, useState } from 'react';
import { getMyBookings, cancelBooking } from '../../api/tourApi';
import './BookingHistory.css';

const sections = [
  { key: 'upcoming', label: 'Sắp đi' },
  { key: 'completed', label: 'Đã đi' },
  { key: 'cancelled', label: 'Đã hủy' },
  { key: 'pending', label: 'Chờ thanh toán' },
];

export default function BookingHistory() {
  const [bookings, setBookings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);

  const fetchBookings = async () => {
    try {
      const res = await getMyBookings();
      setBookings(res.bookings);
    } catch (error) {
      console.error('Lỗi lấy lịch sử đặt tour:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleCancel = async (id) => {
    if (!window.confirm('Bạn có chắc chắn muốn hủy đơn tour này không?')) return;

    setCancellingId(id);
    try {
      await cancelBooking(id);
      alert('Hủy đơn tour thành công!');
      setLoading(true);
      await fetchBookings();
    } catch (error) {
      alert(error.response?.data?.error || 'Không thể hủy đơn tour!');
    } finally {
      setCancellingId(null);
    }
  };

  if (loading) {
    return <div className="loading">Đang tải lịch sử đặt tour...</div>;
  }

  if (!bookings) {
    return <div className="loading">Không có dữ liệu.</div>;
  }
  console.log('tour_image:', bookings);
  return (
    <div className="booking-history-card">
      <h2>Lịch sử đặt tour</h2>

      {sections.map((section) => (
        <div key={section.key} className="booking-section">
          <h3>{section.label}</h3>
          {bookings[section.key]?.length === 0 ? (
            <p className="empty-text">Không có tour trong mục này.</p>
          ) : (
            bookings[section.key].map((item) => (
              <div key={item.id} className="booking-row">
                <div className="booking-left">
                  <img
  src={
    item.tour_image && item.tour_image.startsWith('http')
      ? item.tour_image
      : `http://127.0.0.1:8000${item.tour_image || ''}`
  }
  alt={item.tour_title}
  onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e'; }}
/>
                  <div>
                    <h4>{item.tour_title}</h4>
                    <p>{item.tour_address}</p>
                  </div>
                </div>
                <div className="booking-right">
                  <p><strong>Ngày khởi hành:</strong> {item.tour_departure_date}</p>
                  <p><strong>Số người:</strong> {item.number_of_people}</p>
                  <p><strong>Trạng thái:</strong> {item.status_display}</p>
                  <p><strong>Tổng tiền:</strong> {Number(item.total_price).toLocaleString()} VNĐ</p>
                  {item.status === 'pending' && (
                    <button
                      type="button"
                      className="btn-cancel-booking"
                      onClick={() => handleCancel(item.id)}
                      disabled={cancellingId === item.id}
                    >
                      {cancellingId === item.id ? 'Đang hủy...' : 'Hủy tour'}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      ))}
    </div>
  );
}
