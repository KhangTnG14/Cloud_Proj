import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import { getCategories, getTourById } from '../../api/tourApi';
import './ToursPage.css';

const fallbackImage = 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e';

const ToursPage = () => {
  const [tours, setTours] = useState([]);
  const [allCategories, setAllCategories] = useState([]);

  const [search, setSearch] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [startDate, setStartDate] = useState('');

  const [currentUser, setCurrentUser] = useState(null);

  const navigate = useNavigate();
  const location = useLocation();

  const fetchTours = async (searchParams = {}) => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/tours/', {
        params: {
          search: searchParams.search !== undefined ? searchParams.search : search,
          category: searchParams.category !== undefined ? (searchParams.category || undefined) : (categoryId || undefined),
          min_price: searchParams.min_price !== undefined ? searchParams.min_price : minPrice,
          max_price: searchParams.max_price !== undefined ? searchParams.max_price : maxPrice,
          start_date: searchParams.start_date !== undefined ? searchParams.start_date : startDate,
        },
      });

      const toursData = Array.isArray(response.data) ? response.data : [];

      const toursWithImages = await Promise.all(
        toursData.map(async (tour) => {
          try {
            const detail = await getTourById(tour.id);
            return {
              ...tour,
              image: detail.image_url || fallbackImage,
            };
          } catch (error) {
            return {
              ...tour,
              image: fallbackImage,
            };
          }
        })
      );

      setTours(toursWithImages);
    } catch (error) {
      console.error(error);
      setTours([]);
    }
  };

  const fetchCurrentUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await axios.get('http://127.0.0.1:8000/api/me/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setCurrentUser(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      approved: { label: 'Đang hoạt động', className: 'status-approved' },
      pending:  { label: 'Chờ duyệt',      className: 'status-pending'  },
      rejected: { label: 'Từ chối',         className: 'status-rejected' },
    };
    return statusMap[status] || { label: status, className: '' };
  };

  useEffect(() => {
    fetchCurrentUser();
    getCategories()
      .then(setAllCategories)
      .catch(() => setAllCategories([]));

    const queryParams = new URLSearchParams(location.search);
    const urlSearch = queryParams.get('search') || '';
    const urlStartDate = queryParams.get('startDate') || '';
    const urlMinPrice = queryParams.get('minPrice') || '';
    const urlMaxPrice = queryParams.get('maxPrice') || '';

    if (urlSearch) setSearch(urlSearch);
    if (urlStartDate) setStartDate(urlStartDate);
    if (urlMinPrice) setMinPrice(urlMinPrice);
    if (urlMaxPrice) setMaxPrice(urlMaxPrice);

    fetchTours({
      search: urlSearch,
      start_date: urlStartDate,
      min_price: urlMinPrice,
      max_price: urlMaxPrice,
    });
  }, [location.search]);

  return (
    <div className="tours-page">
      <div className="tours-container">
        {/* SIDEBAR */}
        <aside className="filter-sidebar">
          <div className="filter-box">
            <h2 className="filter-title">Bộ lọc</h2>

            <div className="filter-group">
              <label>Loại tour</label>
              <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
                <option value="">Tất cả loại</option>
                {allCategories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Tìm tour</label>
              <input
                type="text"
                placeholder="Ví dụ: Tour Đà Lạt..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Ngày khởi hành</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Giá từ</label>
              <input
                type="number"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Đến giá</label>
              <input
                type="number"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
              />
            </div>

            <button className="search-btn" onClick={() => fetchTours()}>
              Tìm kiếm ngay
            </button>
          </div>
        </aside>

        {/* TOURS GRID */}
        <section className="tours-grid">
          {tours
            .filter((tour) => {
              const isAdmin =
                currentUser &&
                (currentUser.is_staff || currentUser.role === 'ADMIN');

              const isProvider =
                currentUser && currentUser.role === 'PROVIDER';

              // Admin thấy tất cả
              if (isAdmin) return true;

              // Provider không thấy tour bị rejected
              if (isProvider) return tour.status !== 'rejected';

              // Customer / khách chỉ thấy tour approved
              return tour.status === 'approved';
            })
            .map((tour) => (
              <div key={tour.id} className="tour-card">
                {/* IMAGE */}
                <div className="tour-image-wrapper">
                  <img
                    src={tour.image || fallbackImage}
                    alt={tour.title}
                    onError={(e) => { e.target.src = fallbackImage; }}
                    className="tour-image"
                  />
                  <div className="tour-badge">Popular</div>

                  {/* Badge trạng thái - chỉ admin và provider mới thấy */}
                  {currentUser &&
                    (currentUser.is_staff ||
                      currentUser.role === 'ADMIN' ||
                      currentUser.role === 'PROVIDER') && (
                    <div className={`tour-status-badge ${getStatusBadge(tour.status).className}`}>
                      {getStatusBadge(tour.status).label}
                    </div>
                  )}
                </div>

                {/* CONTENT */}
                <div className="tour-content">
                  <h3 className="tour-title">{tour.title}</h3>

                  {tour.category_names?.length > 0 && (
                    <div className="tour-categories">
                      {tour.category_names.map((name) => (
                        <span key={name} className="category-tag">
                          {name}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="tour-footer">
                    <div>
                      <p className="tour-price-label">Giá từ</p>
                      <h4 className="tour-price">
                        {Number(tour.price).toLocaleString()} đ
                      </h4>
                    </div>
                    <div className="tour-slots">{tour.slots} chỗ</div>
                  </div>

                  {tour.status === 'approved' && (
                    <button className="book-btn" onClick={() => navigate(`/tours/${tour.id}`)}>
                      Đặt Tour
                    </button>
                  )}
                </div>
              </div>
            ))}
        </section>
      </div>
    </div>
  );
};

export default ToursPage;