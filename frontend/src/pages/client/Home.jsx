import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Thêm useNavigate
import BackGroundImage from '../../assets/background_home_1.jpg';
import ticket from '../../assets/ticket.png';
import { getTours, getTourById, isCustomerTourVisible } from '../../api/tourApi.js';
import './Home.css';

export default function Home() {
  const [tours, setTours] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Các state phục vụ cho thanh tìm kiếm nhanh
  const [search, setSearch] = useState('');
  const [startDate, setStartDate] = useState('');
  const [priceRange, setPriceRange] = useState('Tất cả');

  useEffect(() => {
    const fetchTours = async () => {
      try {
        const data = await getTours();
        const toursWithDetail = await Promise.all(
          data.map(async (tour) => {
            try {
              const detail = await getTourById(tour.id);
              return {
                ...tour,
                tour_images: detail.tour_images,
                image_url: detail.image_url,
              };
            } catch (error) {
              console.error(error);
              return tour;
            }
          })
        );
        setTours(toursWithDetail);
      } catch (error) {
        console.error(error);
        setTours([]);
      } finally {
        setLoading(false);
      }
    };
    fetchTours();
  }, []);

  // Hàm xử lý khi bấm nút "Tìm kiếm" ở Home
  const handleSearchSubmit = () => {
    let minPrice = '';
    let maxPrice = '';

    // Phân tách khoảng giá tương ứng với lựa chọn trong bộ lọc ToursPage
    if (priceRange === 'Dưới 5 triệu') {
      maxPrice = '5000000';
    } else if (priceRange === '5 - 10 triệu') {
      minPrice = '5000000';
      maxPrice = '10000000';
    } else if (priceRange === 'Trên 10 triệu') {
      minPrice = '10000000';
    }

    // Tạo query string đưa lên URL
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (startDate) params.append('startDate', startDate);
    if (minPrice) params.append('minPrice', minPrice);
    if (maxPrice) params.append('maxPrice', maxPrice);

    // Chuyển hướng sang trang danh sách tour kèm theo tham số tìm kiếm
    navigate(`/tours?${params.toString()}`);
  };

  const approvedTours = tours.filter(isCustomerTourVisible);
  const topPrice = [...approvedTours].sort((a, b) => Number(b.price) - Number(a.price)).slice(0, 100);
  const topHot = [...approvedTours].sort((a, b) => Number(a.slots) - Number(b.slots)).slice(0, 100);
  const featuredTours = Array.from(new Map([...topPrice, ...topHot].map((item) => [item.id, item])).values()).slice(0, 100);

  return (
    <div className="home-container">
      {/* HERO SECTION */}
      <section className="hero-section" style={{ backgroundImage: `url(${BackGroundImage})` }}>
        <div className="hero-overlay"></div>

        <div className="hero-content">
          <p className="hero-subtitle">Khám phá những hành trình tuyệt vời</p>
          <h1 className="hero-title">TOURS DU LỊCH</h1>
          <p className="hero-description">
            Trải nghiệm những chuyến đi đáng nhớ cùng dịch vụ du lịch hiện đại và tiện lợi.
          </p>
          <button className="hero-button" onClick={() => navigate('/tours')}>Khám phá ngay</button>
        </div>

        {/* QUICK SEARCH BAR */}
        <div className="quick-search-bar">
          <div className="search-group">
            <label>Điểm đến</label>
            <input 
              type="text" 
              placeholder="Bạn muốn đi đâu?" 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="search-group">
            <label>Ngày khởi hành</label>
            <input 
              type="date" 
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div className="search-group">
            <label>Khoảng giá</label>
            <select value={priceRange} onChange={(e) => setPriceRange(e.target.value)}>
              <option>Tất cả</option>
              <option>Dưới 5 triệu</option>
              <option>5 - 10 triệu</option>
              <option>Trên 10 triệu</option>
            </select>
          </div>

          <button className="search-button" onClick={handleSearchSubmit}>Tìm kiếm</button>
        </div>
      </section>

      {/* TOUR LIST SECTION */}
      <section className="tour-list-container">
        <div className="section-header">
          <h2 className="section-title">Tour nổi bật</h2>
          <p className="section-description">Những tour được yêu thích nhất hiện nay</p>
        </div>

        {loading ? (
          <p className="loading-text">Đang tải dữ liệu...</p>
        ) : (
          <div className="tour-grid">
            {featuredTours.map((tour) => (
              <Link to={`/tours/${tour.id}`} key={tour.id} className="tour-card-link">
                <div className="tour-card">
                  <div className="tour-image">
                    <img
                      src={tour.tour_images?.length > 0 ? tour.tour_images[0].image : tour.image_url || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e'}
                      alt={tour.title}
                      onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e'; }}
                    />
                    <span className="tour-badge">Nổi bật</span>
                  </div>

                  <div className="tour-info">
                    {tour.category_names?.length > 0 && (
                      <div className="category-list">
                        {tour.category_names.map((name) => (
                          <span key={name} className="category-tag">{name}</span>
                        ))}
                      </div>
                    )}
                    <h3 className="tour-title">{tour.title}</h3>
                    <p className="tour-price">
                      {new Intl.NumberFormat('vi-VN').format(tour.price)} VNĐ
                    </p>
                    <div className="tour-slots">
                      <img src={ticket} alt="ticket" />
                      <span>Còn {tour.slots} chỗ</span>
                    </div>
                    <div className="tour-footer">
                      <span className="detail-link">Xem chi tiết →</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}