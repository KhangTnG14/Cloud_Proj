import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getProviderTours, createProviderTour, uploadTourImages, updateProviderTour, deleteProviderTour, deleteTourImage, getCategories } from '../../api/tourApi';
import axios from 'axios';
// --- THƯ VIỆN BIỂU ĐỒ RECHARTS CHO DAY 24 ---
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './ProviderDashboard.css';
import add from '../../assets/add.png';
import adress from '../../assets/adress.png';
import income from '../../assets/income.png';
import date from '../../assets/calendar.png';
import ticket from '../../assets/ticket.png';
import shoppingcart from '../../assets/shopping-cart.png';
import calendar from '../../assets/calendar.png';
import camera from '../../assets/camera.png';
import image from '../../assets/image.png';
import pencil from '../../assets/pencil.png';
import trash from '../../assets/trash.png';


export default function ProviderDashboard() {
  const [tours, setTours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentTourId, setCurrentTourId] = useState(null);
  const [showImageManager, setShowImageManager] = useState(false);
  const [selectedTour, setSelectedTour] = useState(null);

  // --- STATE THỐNG KÊ CHI TIẾT ---
  const [stats, setStats] = useState({ newOrders: 0, totalRevenue: 0 });
  const [upcomingGuests, setUpcomingGuests] = useState([]);
  
  // --- STATE BIỂU ĐỒ DOANH THU & BỘ LỌC ĐỘNG ---
  const [chartData, setChartData] = useState([]);
  const [pieData, setPieData] = useState([]);
  const [reportType, setReportType] = useState('month'); // Chức năng mới: Chọn Loại báo cáo
  const [year, setYear] = useState(2026);                // Chức năng mới: Chọn Năm theo dõi

  // Form State
  const [formData, setFormData] = useState({
    title: '',
    address: '',
    price: '',
    departure_date: '',
    slots: '',
    latitude: '',
    longitude: '',
    description: '',
    image_url: '' // Optional default image URL
  });

  // Selected files for multiple image upload
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [filePreviews, setFilePreviews] = useState([]);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [allCategories, setAllCategories] = useState([]);
  const [selectedCategoryIds, setSelectedCategoryIds] = useState([]);

  // Tự động gọi lại dữ liệu khi danh sách Tour hoặc Bộ lọc biểu đồ thay đổi
  useEffect(() => {
    fetchTours();
    fetchDashboardStats();
    getCategories().then(setAllCategories).catch(() => setAllCategories([]));
  }, []);

  useEffect(() => {
    fetchRevenueReport(); 
  }, [reportType, year]); // Bộ lọc thay đổi -> Tự động kích hoạt gọi API cập nhật biểu đồ

  // Dữ liệu giả lập hiển thị cho mục đơn hàng & khách hàng
  const fetchDashboardStats = () => {
    setStats(prev => ({ ...prev, newOrders: 3 }));
    setUpcomingGuests([
      { id: 1, name: "Nguyễn Vũ Hà", tour: "Đi Nha Trang 3 Ngày", date: "25/05/2026" },
      { id: 2, name: "Trần Đại Tân", tour: "Đà Lạt Mộng Mơ", date: "28/05/2026" }
    ]);
  };

  // --- HÀM GỌI API BÁO CÁO DOANH THU THẬT ĐÃ ĐỒNG BỘ 100% VỚI BACKEND ---
  const fetchRevenueReport = async () => {
    try {
      // Đọc chính xác khóa token (SimpleJWT) nhóm đang cấu hình lưu ở localStorage
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      
      // Gọi API động kèm params type và year gửi lên Backend lọc dữ liệu từ SQL
      const response = await axios.get(
        `http://127.0.0.1:8000/api/tours/provider/analytics/revenue/?type=${reportType}&year=${year}`, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const rawData = response.data.data || [];

      // 1. Tính tổng doanh thu thực tế từ mảng kết quả trả về để update Card Thống kê
      const totalCalculated = rawData.reduce((sum, item) => sum + (item.total_revenue || 0), 0);
      setStats(prev => ({ ...prev, totalRevenue: totalCalculated }));

      // 2. Chuyển đổi dữ liệu đồng bộ cấu trúc với Biểu đồ cột của Hà
      const formattedChart = rawData.map(item => ({
        month: item.label,               // 'Tháng 05' hoặc 'Quý 1'
        revenue: item.total_revenue,     // Số tiền thu được
        bookings: item.total_bookings    // Số đơn hàng đặt thành công
      }));
      setChartData(formattedChart);

      // 3. Đổ dữ liệu phân bổ tỉ trọng vào biểu đồ Tròn
      const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a855f7', '#ec4899', '#f97316', '#14b8a6', '#6366f1', '#8b5cf6', '#3b82f6', '#10b981'];
      const formattedPie = rawData.map((item, index) => ({
        name: item.label,
        value: item.total_revenue,
        color: COLORS[index % COLORS.length]
      }));
      setPieData(formattedPie);

    } catch (error) {
      console.error("Lỗi lấy báo cáo doanh thu thật, chuyển sang dùng dữ liệu Mock Test:", error);
      
      // Khôi phục dữ liệu mẫu dự phòng nguyên bản nếu Backend mất kết nối
      const mockMonthly = [
        { month: 'Tháng 1', revenue: 4500000 }, { month: 'Tháng 2', revenue: 3000000 },
        { month: 'Tháng 3', revenue: 8500000 }, { month: 'Tháng 4', revenue: 6000000 },
        { month: 'Tháng 5', revenue: 15000000 }, { month: 'Tháng 6', revenue: 0 },
        { month: 'Tháng 7', revenue: 0 }, { month: 'Tháng 8', revenue: 0 },
        { month: 'Tháng 9', revenue: 0 }, { month: 'Tháng 10', revenue: 0 },
        { month: 'Tháng 11', revenue: 0 }, { month: 'Tháng 12', revenue: 0 }
      ];
      setChartData(mockMonthly);

      const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
      const mockQuarterly = [
        { name: 'Quý 1', value: 16000000, color: COLORS[0] },
        { name: 'Quý 2', value: 21000000, color: COLORS[1] },
        { name: 'Quý 3', value: 0, color: COLORS[2] },
        { name: 'Quý 4', value: 0, color: COLORS[3] }
      ];
      setPieData(mockQuarterly);
      setStats(prev => ({ ...prev, totalRevenue: 37000000 }));
    }
  };

  const fetchTours = async () => {
    try {
      setLoading(true);
      const data = await getProviderTours();
      setTours(data);
    } catch (error) {
      console.error('Lỗi lấy danh sách tour nhà cung cấp:', error);
      setMessage({ type: 'error', text: 'Không thể tải danh sách tour của bạn. Vui lòng kiểm tra quyền truy cập!' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const toggleCategory = (categoryId) => {
    setSelectedCategoryIds((prev) =>
      prev.includes(categoryId)
        ? prev.filter((id) => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);

    // Create image previews
    const previews = files.map(file => URL.createObjectURL(file));
    setFilePreviews(previews);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage({ type: '', text: '' });

    try {
      if (editMode) {
        await updateProviderTour(currentTourId, {
          title: formData.title,
          address: formData.address,
          price: parseFloat(formData.price),
          departure_date: formData.departure_date,
          slots: parseInt(formData.slots),
          latitude: formData.latitude ? parseFloat(formData.latitude) : null,
          longitude: formData.longitude ? parseFloat(formData.longitude) : null,
          description: formData.description,
          image_url: formData.image_url || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
          categories: selectedCategoryIds,
        });
        
        if (selectedFiles.length > 0) {
          await uploadTourImages(currentTourId, selectedFiles);
        }
        
        setMessage({ type: 'success', text: 'Cập nhật thông tin tour du lịch thành công.' });
      } else {
        const newTour = await createProviderTour({
          title: formData.title,
          address: formData.address,
          price: parseFloat(formData.price),
          departure_date: formData.departure_date,
          slots: parseInt(formData.slots),
          latitude: formData.latitude ? parseFloat(formData.latitude) : null,
          longitude: formData.longitude ? parseFloat(formData.longitude) : null,
          description: formData.description,
          image_url: formData.image_url || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
          categories: selectedCategoryIds,
        });

        const newTourId = newTour.id;

        if (selectedFiles.length > 0) {
          await uploadTourImages(newTourId, selectedFiles);
        }

        setMessage({ type: 'success', text: 'Chúc mừng! Bạn đã đăng ký và tạo tour du lịch mới thành công.' });
      }

      setFormData({
        title: '', address: '', price: '', departure_date: '', slots: '', latitude: '', longitude: '', description: '', image_url: ''
      });
      setSelectedCategoryIds([]);
      setSelectedFiles([]);
      setFilePreviews([]);

      setTimeout(() => {
        setShowCreateModal(false);
        fetchTours();
        fetchRevenueReport(); // Tải lại biểu đồ sau khi thêm/sửa
        setMessage({ type: '', text: '' });
      }, 2000);

    } catch (error) {
      console.error('Lỗi lưu thông tin tour:', error);
      let errMsg = 'Đã có lỗi xảy ra trong quá trình xử lý dữ liệu. Vui lòng kiểm tra lại!';
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          errMsg = Object.entries(error.response.data)
            .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
            .join(' | ');
        } else if (typeof error.response.data === 'string') {
          errMsg = error.response.data;
        }
      }
      setMessage({ type: 'error', text: errMsg });
    } finally {
      setSubmitting(false);
    }
  };

  const openEditModal = (tour) => {
    setEditMode(true);
    setCurrentTourId(tour.id);
    setFormData({
      title: tour.title || '',
      address: tour.address || '',
      price: tour.price || '',
      departure_date: tour.departure_date || '',
      slots: tour.slots || '',
      latitude: tour.latitude || '',
      longitude: tour.longitude || '',
      description: tour.description || '',
      image_url: tour.image_url || ''
    });
    setSelectedCategoryIds(Array.isArray(tour.categories) ? tour.categories : []);
    setSelectedFiles([]);
    setFilePreviews([]);
    setShowCreateModal(true);
  };

  const handleDeleteTour = async (id) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa tour này không? Mọi dữ liệu đặt chỗ liên quan cũng sẽ bị xóa bỏ hoàn toàn.")) {
      try {
        await deleteProviderTour(id);
        setMessage({ type: 'success', text: 'Đã xóa tour thành công.' });
        fetchTours();
        fetchRevenueReport();
      } catch (error) {
        setMessage({ type: 'error', text: 'Lỗi phát sinh trong hệ thống khi xóa tour.' });
      }
    }
  };

  const openImageManager = (tour) => {
    setSelectedTour(tour);
    setShowImageManager(true);
  };

  const handleDeleteImage = async (imageId) => {
    if (window.confirm("Xóa ảnh này khỏi album trưng bày?")) {
      try {
        await deleteTourImage(imageId);
        fetchTours();
        setSelectedTour(prev => ({
          ...prev,
          tour_images: prev.tour_images.filter(img => img.id !== imageId)
        }));
      } catch (error) {
        alert("Hệ thống không thể xóa ảnh vào lúc này!");
      }
    }
  };

  const handleAddMoreImages = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    try {
      await uploadTourImages(selectedTour.id, files);
      fetchTours();
      setShowImageManager(false);
      setMessage({ type: 'success', text: 'Đã bổ sung bộ sưu tập ảnh thành công.' });
    } catch (error) {
      alert("Lỗi tải tệp tin ảnh lên máy chủ");
    }
  };

  const getTourDisplayImage = (tour) => {
    if (tour.tour_images && tour.tour_images.length > 0) {
      const imgPath = tour.tour_images[0].image;
      if (imgPath.startsWith('http://') || imgPath.startsWith('https://')) {
        return imgPath;
      }
      return `http://127.0.0.1:8000${imgPath}`;
    }
    if (tour.image_url) {
      if (tour.image_url.startsWith('http://') || tour.image_url.startsWith('https://')) {
        return tour.image_url;
      }
      return `http://127.0.0.1:8000${tour.image_url}`;
    }
    return 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80';
  };

  const formatPrice = (value) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
  };

  // ... Toàn bộ logic imports, states, useEffects và các hàm xử lý API bên trên GIỮ NGUYÊN 100% ...

  return (
    <div className="provider-dashboard-container">
      {/* --- CÁC PHẦN HEADER, STATS GRID, BIỂU ĐỒ RECHARTS VÀ BẢNG HÀNH KHÁCH GIỮ NGUYÊN --- */}
      <div className="dashboard-header-section">
        <div>
          <h1 className="dashboard-title">Kênh Nhà Cung Cấp</h1>
          <p className="dashboard-subtitle">Quản lý, theo dõi doanh thu và cấu hình các sản phẩm du lịch độc quyền</p>
        </div>
        <button 
  className="btn-add-tour" 
  onClick={() => {
    setEditMode(false);
    setCurrentTourId(null);
    setFormData({
      title: '', address: '', price: '', departure_date: '', slots: '', latitude: '', longitude: '', description: '', image_url: ''
    });
    setSelectedCategoryIds([]);
    setSelectedFiles([]);
    setFilePreviews([]);
    setShowCreateModal(true);
  }}
  style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
>
  <img 
    src={add} 
    alt="add icon" 
    className="plus-icon"
    style={{ 
    
      width: '18px', 
      height: '18px', 
      objectFit: 'contain',
      /* Ép icon sang sắc trắng để nổi bật trên nền nút xanh ngọc */
      filter: 'brightness(0) invert(1)' 
    }} 
  />
  <span>Đăng Tour Mới</span>
</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card" style={{ background: '#e3f2fd', borderLeft: '5px solid #1e88e5' }}>
          <div className="stat-value" style={{ color: '#1e88e5' }}>{stats.newOrders}</div>
          <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#555' }}>
            <img src={shoppingcart} alt="shopping cart" style={{ width: '17px', height: '17px', objectFit: 'contain' }} />
            <span>Đơn hàng mới cần xử lý</span>
          </div>
        </div>
        <div className="stat-card" style={{ background: '#e8f5e9', borderLeft: '5px solid #43a047' }}>
          <div className="stat-value" style={{ color: '#43a047' }}>{formatPrice(stats.totalRevenue)}</div>
          <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#555' }}>
            <img src={income} alt="income" style={{ width: '17px', height: '17px', objectFit: 'contain' }} />
            <span>Doanh thu tích lũy hệ thống</span>
          </div>
        </div>
        <div className="stat-card info">
          <div className="stat-value">{tours.length}</div>
          <div className="stat-label">Tổng số lượng Tour vận hành</div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '15px', marginBottom: '15px', paddingRight: '5px' }}>
        <select 
          style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid #ced4da', backgroundColor: 'white', fontWeight: '500', outline: 'none', cursor: 'pointer' }}
          value={reportType} 
          onChange={(e) => setReportType(e.target.value)}
        >
          <option value="month">Xem theo Tháng</option>
          <option value="quarter">Xem theo Quý</option>
        </select>
        <select 
          style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid #ced4da', backgroundColor: 'white', fontWeight: '500', outline: 'none', cursor: 'pointer' }}
          value={year} 
          onChange={(e) => setYear(parseInt(e.target.value))}
        >
          <option value={2026}>Năm 2026</option>
          <option value={2025}>Năm 2025</option>
        </select>
      </div>

      <div style={{ display: 'flex', gap: '25px', marginBottom: '35px', flexWrap: 'wrap' }}>
        <div style={{ flex: 2, minWidth: '600px', backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#2c3e50' }}>Biểu đồ phân tích doanh thu ({reportType === 'month' ? 'Từng Tháng' : 'Từng Quý'})</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatPrice(value)} />
                <Legend />
                <Bar dataKey="revenue" name="Doanh thu thực tế (VND)" fill="#43a047" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={{ flex: 1, minWidth: '300px', backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#2c3e50', width: '100%', textAlign: 'left' }}>Tỷ trọng phân bổ thu nhập</h3>

          <div style={{ width: '100%', height: 220 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatPrice(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', gap: '10px', fontSize: '12px', marginTop: '10px', flexWrap: 'wrap', justifyContent: 'center' }}>
            {pieData.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: item.color, borderRadius: '2px' }}></span>
                <span>{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="dashboard-section-wrapper" style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', marginBottom: '35px' }}>
        <h2 className="section-title" style={{ marginTop: 0, marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <img 
            src={calendar} 
            alt="calendar icon" 
            style={{ 
              width: '28px', 
              height: '28px', 
              objectFit: 'contain',
          
              filter: 'invert(37%) sepia(93%) saturate(1463%) hue-rotate(192deg) brightness(97%) contrast(101%)'
            }} 
          />
          <span>Danh sách hành khách sắp khởi hành</span>
        </h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #eceeef' }}>
              <th style={{ padding: '12px', color: '#2c3e50', fontWeight: '600' }}>Tên khách hàng</th>
              <th style={{ padding: '12px', color: '#2c3e50', fontWeight: '600' }}>Tour du lịch đã đặt</th>
              <th style={{ padding: '12px', color: '#2c3e50', fontWeight: '600', textAlign: 'center' }}>Ngày khởi hành</th>
            </tr>
          </thead>
          <tbody>
            {upcomingGuests.map(guest => (
              <tr key={guest.id} style={{ borderBottom: '1px solid #f1f1f1' }}>
                <td style={{ padding: '12px', color: '#333', fontWeight: '500' }}>{guest.name}</td>
                <td style={{ padding: '12px', color: '#555' }}>{guest.tour}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  <span style={{ background: '#fff3e0', padding: '4px 10px', borderRadius: '20px', color: '#e65100', fontSize: '13px', fontWeight: '500' }}>
                    {guest.date}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {message.text && (
        <div className={`alert-box ${message.type === 'success' ? 'success' : 'error'}`}>
          {message.text}
        </div>
      )}

      {/* --- ĐOẠN ĐƯỢC FIX LẠI HIỂN THỊ TRẠNG THÁI ĐỘNG CHO PROVIDER --- */}
      <h2 className="section-title">Hệ thống các Tour đang quản lý</h2>

      {loading ? (
        <div className="loading-spinner">Đang đồng bộ danh sách dữ liệu từ máy chủ...</div>
      ) : tours.length === 0 ? (
        <div className="empty-state">
          <h3>Bạn chưa đăng tải tour nào</h3>
          <p>Hãy bắt đầu quảng bá thương hiệu du lịch của bạn bằng cách thêm tour đầu tiên!</p>
          <button className="btn-add-tour-empty" onClick={() => { setEditMode(false); setSelectedCategoryIds([]); setShowCreateModal(true); }}>Đăng ngay</button>
        </div>
      ) : (
        <div className="tours-grid">
  {tours.map(tour => (
    <div key={tour.id} className="provider-tour-card">
      <Link to={`/tours/${tour.id}`} style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
        <div className="tour-card-image-wrapper">
          <img
            src={getTourDisplayImage(tour)}
            alt={tour.title}
            className="tour-card-image"
          />
          <span className="tour-card-price-badge">{formatPrice(tour.price)}</span>
        </div>
        
        <div className="tour-card-body" style={{ paddingBottom: '0px' }}>
          <h3 className="tour-card-title">{tour.title}</h3>
          
          {tour.category_names?.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
              {tour.category_names.map((name) => (
                <span key={name} style={{ fontSize: '11px', background: '#e0f2fe', color: '#0369a1', padding: '3px 8px', borderRadius: '4px', fontWeight: '500' }}>
                  {name}
                </span>
              ))}
            </div>
          )}

          <div className="tour-card-details">
            <p style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <img src={adress} alt="address" style={{ width: '16px', height: '16px', objectFit: 'contain' ,filter: 'invert(37%) sepia(93%) saturate(1463%) hue-rotate(338deg) brightness(97%) contrast(101%)'}} />
              <span><strong>Địa điểm:</strong> {tour.address}</span>
            </p>

            <p style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <img src={date} alt="date" style={{ width: '16px', height: '16px', objectFit: 'contain',filter: 'invert(37%) sepia(93%) saturate(1463%) hue-rotate(192deg) brightness(97%) contrast(101%)' }} />
              <span><strong>Ngày đi:</strong> {tour.departure_date}</span>
            </p>

            <p style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <img src={ticket} alt="ticket" style={{ width: '16px', height: '16px', objectFit: 'contain', filter: 'invert(37%) sepia(93%) saturate(1463%) hue-rotate(338deg) brightness(97%) contrast(101%)' }} />
              <span><strong>Còn trống:</strong> {tour.slots} chỗ đăng ký</span>
            </p>

            {tour.latitude && tour.longitude && (
              <p className="coordinates-tag" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px' }}>
                <img 
                  src={adress} 
                  alt="coordinates" 
                  style={{ 
                    width: '16px', 
                    height: '16px', 
                    objectFit: 'contain',
                    filter: 'invert(27%) sepia(91%) saturate(5453%) hue-rotate(354deg) brightness(94%) contrast(94%)' 
                  }} 
                />
                <span><strong>Vĩ độ/Kinh độ:</strong> {tour.latitude}, {tour.longitude}</span>
              </p>
            )}
          </div>

          {/* ==========================================================================
             REFACTOR: KHU VỰC TRẠNG THÁI & SỐ LƯỢNG ẢNH TRÊN MỘT HÀNG
             ========================================================================== */}
          <div className="tour-card-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '14px', paddingBottom: '12px', borderBottom: '1px solid #f1f5f9' }}>
            
            {/* Logic trạng thái Soft Mượt mà */}
            {tour.status === 'approved' && (
              <span className="status-badge state-approved" style={{ display: 'flex', alignItems: 'center', gap: '5px', backgroundColor: 'rgba(46, 204, 113, 0.12)', color: '#1e7e34', padding: '5px 10px', borderRadius: '6px', fontWeight: '700', fontSize: '11.5px' }}>
                <span style={{ width: '6px', height: '6px', background: '#2ecc71', borderRadius: '50%' }}></span>
                Đang hoạt động
              </span>
            )}
            
            {tour.status === 'rejected' && (
              <span className="status-badge state-rejected" style={{ display: 'flex', alignItems: 'center', gap: '5px', backgroundColor: 'rgba(231, 76, 60, 0.12)', color: '#b21f1f', padding: '5px 10px', borderRadius: '6px', fontWeight: '700', fontSize: '11.5px' }}>
                <span style={{ width: '6px', height: '6px', background: '#e74c3c', borderRadius: '50%' }}></span>
                Bị từ chối
              </span>
            )}
            
            {(tour.status === 'pending' || !tour.status) && (
              <span className="status-badge state-pending" style={{ display: 'flex', alignItems: 'center', gap: '5px', backgroundColor: 'rgba(241, 196, 15, 0.15)', color: '#856404', padding: '5px 10px', borderRadius: '6px', fontWeight: '700', fontSize: '11.5px' }}>
                <span style={{ width: '6px', height: '6px', background: '#f1c40f', borderRadius: '50%' }}></span>
                Chờ duyệt
              </span>
            )}

            {/* Khung số lượng hình ảnh tối giản */}
            {tour.tour_images && tour.tour_images.length > 0 && (
              <span className="images-count-badge" style={{ display: 'flex', alignItems: 'center', gap: '5px', background: '#f1f5f9', color: '#64748b', padding: '5px 10px', borderRadius: '6px', fontSize: '11.5px', fontWeight: '600' }}>
                <img 
                  src={camera} 
                  alt="camera icon" 
                  style={{ width: '13px', height: '13px', objectFit: 'contain', filter: 'invert(45%) sepia(10%) saturate(300%) hue-rotate(180deg)' }} 
                />
                <span>{tour.tour_images.length} hình ảnh</span>
              </span>
            )}

          </div>
        </div>
      </Link>

      {/* ==========================================================================
         REFACTOR: KHU VỰC 3 NÚT CHỨC NĂNG HÀNH ĐỘNG CAO CẤP
         ========================================================================== */}
      <div className="tour-card-body" style={{ paddingTop: '0px', paddingBottom: '16px' }}>
        <div className="tour-card-actions" style={{ display: 'flex', gap: '10px', marginTop: '12px', padding: '0 20px' }}>
  
  {/* NÚT SỬA */}
  <button 
    onClick={() => openEditModal(tour)} 
    style={{ 
      flex: 1, 
      height: '36px', 
      border: '1px solid #cbd5e1', 
      borderRadius: '8px', 
      backgroundColor: '#ffffff', 
      color: '#334155', 
      cursor: 'pointer', 
      fontWeight: '600', 
      fontSize: '13px', 
      transition: 'all 0.2s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '6px'
    }}
    onMouseEnter={(e) => { 
      e.currentTarget.style.background = '#f8fafc'; 
      e.currentTarget.style.borderColor = '#94a3b8';
      // Đổi màu icon sang xanh thương hiệu khi hover nút
      e.currentTarget.querySelector('.btn-icon').style.filter = 'invert(67%) sepia(87%) saturate(373%) hue-rotate(58deg) brightness(97%) contrast(87%)';
    }}
    onMouseLeave={(e) => { 
      e.currentTarget.style.background = '#ffffff'; 
      e.currentTarget.style.borderColor = '#cbd5e1';
      // Trả icon về màu xám đen mặc định
      e.currentTarget.querySelector('.btn-icon').style.filter = 'invert(24%) sepia(16%) saturate(1391%) hue-rotate(180deg) brightness(93%) contrast(89%)';
    }}
  >
    <img 
      src={pencil} 
      alt="edit" 
      className="btn-icon"
      style={{ 
        width: '14px', 
        height: '14px', 
        objectFit: 'contain',
        filter: 'invert(24%) sepia(16%) saturate(1391%) hue-rotate(180deg) brightness(93%) contrast(89%)',
        transition: 'filter 0.2s ease'
      }} 
    />
    <span>Sửa</span>
  </button>
  
  {/* NÚT ẢNH */}
  <button 
    onClick={() => openImageManager(tour)} 
    style={{ 
      flex: 1, 
      height: '36px', 
      border: '1px solid #cbd5e1', 
      borderRadius: '8px', 
      backgroundColor: '#ffffff', 
      color: '#334155', 
      cursor: 'pointer', 
      fontWeight: '600', 
      fontSize: '13px', 
      transition: 'all 0.2s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '6px'
    }}
    onMouseEnter={(e) => { 
      e.currentTarget.style.background = '#f8fcf8'; 
      e.currentTarget.style.borderColor = '#94a3b8';
      // Đổi màu icon sang xanh thương hiệu khi hover nút
      e.currentTarget.querySelector('.btn-icon').style.filter = 'invert(37%) sepia(99%) saturate(1989%) hue-rotate(97deg) brightness(95%) contrast(104%)';
    }}
    onMouseLeave={(e) => { 
      e.currentTarget.style.background = '#ffffff'; 
      e.currentTarget.style.borderColor = '#cbd5e1';
      // Trả icon về màu xám đen mặc định
      e.currentTarget.querySelector('.btn-icon').style.filter = 'invert(24%) sepia(16%) saturate(1391%) hue-rotate(180deg) brightness(93%) contrast(89%)';
    }}
  >
    <img 
      src={image} 
      alt="images" 
      className="btn-icon"
      style={{ 
        width: '14px', 
        height: '14px', 
        objectFit: 'contain',
        filter: 'invert(24%) sepia(16%) saturate(1391%) hue-rotate(180deg) brightness(93%) contrast(89%)',
        transition: 'filter 0.2s ease'
      }} 
    />
    <span>Ảnh</span>
  </button>
  
  {/* NÚT XÓA */}
  <button 
    onClick={() => handleDeleteTour(tour.id)} 
    style={{ 
      flex: 1, 
      height: '36px', 
      border: 'none', 
      borderRadius: '8px', 
      backgroundColor: '#ef4444', 
      color: 'white', 
      cursor: 'pointer', 
      fontWeight: '600', 
      fontSize: '13px', 
      transition: 'all 0.2s ease', 
      boxShadow: '0 2px 8px rgba(239, 68, 68, 0.15)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '6px'
    }}
    onMouseEnter={(e) => { e.currentTarget.style.background = '#dc2626'; }}
    onMouseLeave={(e) => { e.currentTarget.style.background = '#ef4444'; }}
  >
    <img 
      src={trash} 
      alt="delete" 
      style={{ 
        width: '14px', 
        height: '14px', 
        objectFit: 'contain',
        filter: 'brightness(0) invert(1)' /* Luôn giữ trắng nguyên bản trên nền đỏ */
      }} 
    />
    <span>Xóa</span>
  </button>

</div>
      </div>

    </div>
  ))}
</div>
      
      
      )}

      {/* --- TOÀN BỘ CÁC MODAL CREATE VÀ IMAGE MANAGER BÊN DƯỚI GIỮ NGUYÊN --- */}
      {showCreateModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{editMode ? 'CẬP NHẬT THÔNG TIN TOUR' : 'ĐĂNG KÝ PHÁT HÀNH TOUR MỚI'}</h2>
              <button className="btn-close-modal" onClick={() => {
                setShowCreateModal(false);
                setSelectedCategoryIds([]);
                setSelectedFiles([]);
                setFilePreviews([]);
              }}>×</button>
            </div>

            <form onSubmit={handleSubmit} className="create-tour-form">
              <div className="form-row-2">
                <div className="form-group">
                  <label htmlFor="title">Tên sản phẩm hành trình: <span className="required">*</span></label>
                  <input type="text" id="title" name="title" value={formData.title} onChange={handleInputChange} placeholder="Ví dụ: Tour Đảo Phú Quốc 3 Ngày 2 Đêm" required />
                </div>
                <div className="form-group">
                  <label htmlFor="address">Địa điểm / Chi nhánh: <span className="required">*</span></label>
                  <input type="text" id="address" name="address" value={formData.address} onChange={handleInputChange} placeholder="Ví dụ: Phú Quốc, Kiên Giang" required />
                </div>
              </div>

              <div className="form-group">
                <label>Loại hình tour (danh mục):</label>
                {allCategories.length === 0 ? (
                  <p style={{ fontSize: '13px', color: '#888', margin: '6px 0' }}>
                    Chưa có danh mục. Admin thêm tại tab <strong>Loại Tour</strong> trước (Biển, Núi, Văn hóa…).
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '8px' }}>
                    {allCategories.map((cat) => (
                      <label
                        key={cat.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          padding: '8px 12px',
                          borderRadius: '8px',
                          border: selectedCategoryIds.includes(cat.id) ? '2px solid #3498db' : '1px solid #ddd',
                          background: selectedCategoryIds.includes(cat.id) ? '#ebf5fb' : '#fff',
                          cursor: 'pointer',
                          fontSize: '14px',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={selectedCategoryIds.includes(cat.id)}
                          onChange={() => toggleCategory(cat.id)}
                        />
                        {cat.name}
                      </label>
                    ))}
                  </div>
                )}
              </div>

              <div className="form-row-3">
                <div className="form-group">
                  <label htmlFor="price">Chi phí trọn gói (VNĐ): <span className="required">*</span></label>
                  <input type="number" id="price" name="price" value={formData.price} onChange={handleInputChange} placeholder="Ví dụ: 3500000" required />
                </div>
                <div className="form-group">
                  <label htmlFor="departure_date">Lịch khởi hành: <span className="required">*</span></label>
                  <input type="date" id="departure_date" name="departure_date" value={formData.departure_date} onChange={handleInputChange} required />
                </div>
                <div className="form-group">
                  <label htmlFor="slots">Số lượng giới hạn (Vé): <span className="required">*</span></label>
                  <input type="number" id="slots" name="slots" value={formData.slots} onChange={handleInputChange} placeholder="Ví dụ: 30" required />
                </div>
              </div>

              <div className="form-row-3">
                <div className="form-group">
                  <label htmlFor="image_url">Ảnh xem trước chính (Link URL):</label>
                  <input type="url" id="image_url" name="image_url" value={formData.image_url} onChange={handleInputChange} placeholder="https://example.com/image.jpg" />
                </div>
                <div className="form-group">
                  <label htmlFor="latitude">Vĩ độ (Vị trí bản đồ):</label>
                  <input type="number" step="any" id="latitude" name="latitude" value={formData.latitude} onChange={handleInputChange} placeholder="Ví dụ: 10.2899" />
                </div>
                <div className="form-group">
                  <label htmlFor="longitude">Kinh độ (Vị trí bản đồ):</label>
                  <input type="number" step="any" id="longitude" name="longitude" value={formData.longitude} onChange={handleInputChange} placeholder="Ví dụ: 103.9840" />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="description">Thông tin chi tiết lịch trình công bố: <span className="required">*</span></label>
                <textarea id="description" name="description" rows="4" value={formData.description} onChange={handleInputChange} placeholder="Mô tả chi tiết các ngày đi, điểm tham quan, các khách sạn lưu trú, ăn uống..." required />
              </div>

              <div className="form-group file-upload-section">
                <label>Album lưu trữ bộ ảnh bổ sung:</label>
                <div className="file-input-wrapper">
                  <input type="file" id="album-images" multiple accept="image/*" onChange={handleFileChange} className="file-input-hidden" />
                  <label htmlFor="album-images" className="btn-file-select">📸 Tải ảnh lên từ bộ nhớ ({selectedFiles.length} tệp đã chọn)</label>
                </div>
                {filePreviews.length > 0 && (
                  <div className="file-previews-container">
                    {filePreviews.map((preview, index) => (
                      <div key={index} className="preview-item">
                        <img src={preview} alt={`preview-${index}`} />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="form-actions">
                <button type="button" className="btn-cancel" disabled={submitting} onClick={() => { setShowCreateModal(false); setSelectedFiles([]); setFilePreviews([]); }}>Hủy bỏ</button>
                <button type="submit" className="btn-submit" disabled={submitting}>
                  {submitting ? 'Đang thực thi đồng bộ dữ liệu...' : (editMode ? 'Cập Nhật Ngay' : 'Phát Hành Tour')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showImageManager && selectedTour && (
        <div className="modal-backdrop">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h2>HỆ THỐNG QUẢN LÝ ALBUM ẢNH</h2>
              <button className="btn-close-modal" onClick={() => setShowImageManager(false)}>×</button>
            </div>
            <div className="image-manager-body" style={{ padding: '20px' }}>
              <div className="current-images-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px', marginBottom: '25px' }}>
                {selectedTour.tour_images && selectedTour.tour_images.length > 0 ? (
                  selectedTour.tour_images.map(img => {
                    const imgUrl = (img.image.startsWith('http://') || img.image.startsWith('https://')) ? img.image : `http://127.0.0.1:8000${img.image}`;
                    return (
                      <div key={img.id} style={{ position: 'relative', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                        <img src={imgUrl} alt="tour item" style={{ width: '100%', height: '120px', objectFit: 'cover', display: 'block' }} />
                        <button onClick={() => handleDeleteImage(img.id)} style={{ position: 'absolute', top: '5px', right: '5px', background: 'rgba(231, 76, 60, 0.9)', color: 'white', border: 'none', borderRadius: '50%', width: '28px', height: '28px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }} title="Xóa ảnh này ngay">×</button>
                      </div>
                    );
                  })
                ) : (
                  <p style={{ gridColumn: '1 / -1', textAlign: 'center', color: '#7f8c8d' }}>Chưa cập nhật hình ảnh nào vào album trưng bày.</p>
                )}
              </div>
              <div className="add-more-images" style={{ borderTop: '1px solid #eee', paddingTop: '20px' }}>
                <h4 style={{ marginBottom: '10px', color: '#2c3e50' }}>Tải lên bổ sung tệp ảnh mới:</h4>
                <input type="file" multiple accept="image/*" onChange={handleAddMoreImages} style={{ display: 'block', width: '100%', padding: '10px', border: '2px dashed #bdc3c7', borderRadius: '8px', cursor: 'pointer' }} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}