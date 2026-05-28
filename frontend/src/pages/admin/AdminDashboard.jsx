import React, { useEffect, useState } from 'react';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const [stats, setStats] = useState({ total_users: 0, total_tours: 0, total_revenue: 0 });
  const [users, setUsers] = useState([]);
  const [allTours, setAllTours] = useState([]); 
  const [filteredTours, setFilteredTours] = useState([]); 
  const [currentTab, setCurrentTab] = useState('all'); 
  const [mainTab, setMainTab] = useState('tours'); // 'tours', 'users', 'bookings', 'payments'
  const [bookings, setBookings] = useState([]);
  const [payments, setPayments] = useState([]);
  const [bookingSearch, setBookingSearch] = useState('');
  const [paymentSearch, setPaymentSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // Thêm state cho Day 28
  const [categories, setCategories] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryDesc, setNewCategoryDesc] = useState('');
  const [locations, setLocations] = useState([]);
  const [newLocationName, setNewLocationName] = useState('');
  const [newLocationLat, setNewLocationLat] = useState('');
  const [newLocationLng, setNewLocationLng] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (currentTab === 'all') {
      setFilteredTours(allTours);
    } else {
      setFilteredTours(allTours.filter(tour => tour.status === currentTab));
    }
  }, [currentTab, allTours]);

  useEffect(() => {
    if (mainTab === 'bookings') {
      fetchBookings(bookingSearch);
    } else if (mainTab === 'payments') {
      fetchPayments(paymentSearch);
    } else if (mainTab === 'categories') {
      fetchCategories();
    } else if (mainTab === 'locations') {
      fetchLocations();
    } else if (mainTab === 'logs') {
      fetchSystemLogs();
    }
  }, [mainTab]);

  const fetchBookings = async (searchQuery = '') => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    try {
      const url = `http://127.0.0.1:8000/api/tours/admin/bookings/${searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : ''}`;
      const res = await fetch(url, { headers });
      if (res.ok) {
        const data = await res.json();
        setBookings(data);
      }
    } catch (err) {
      console.error("Lỗi tải danh sách đơn hàng:", err);
    }
  };

  const fetchPayments = async (searchQuery = '') => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    try {
      const url = `http://127.0.0.1:8000/api/tours/admin/payments/${searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : ''}`;
      const res = await fetch(url, { headers });
      if (res.ok) {
        const data = await res.json();
        setPayments(data);
      }
    } catch (err) {
      console.error("Lỗi tải lịch sử giao dịch:", err);
    }
  };

  const fetchCategories = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/tours/categories/');
      if (res.ok) {
        const data = await res.json();
        setCategories(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error("Lỗi tải danh mục:", err);
    }
  };

  const fetchSystemLogs = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    try {
      const res = await fetch('http://127.0.0.1:8000/api/users/admin/system-logs/', { headers });
      if (res.ok) {
        const data = await res.json();
        setSystemLogs(data);
      }
    } catch (err) {
      console.error("Lỗi tải System Logs:", err);
    }
  };

  const handleCreateCategory = async () => {
    if (!newCategoryName.trim()) return alert("Tên danh mục không được để trống!");
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      const res = await fetch('http://127.0.0.1:8000/api/tours/categories/', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCategoryName, description: newCategoryDesc })
      });
      if (res.ok) {
        alert("Thêm danh mục thành công!");
        setNewCategoryName('');
        setNewCategoryDesc('');
        fetchCategories();
      } else {
        const errData = await res.json().catch(() => ({}));
        alert(`Lỗi: ${errData.name ? errData.name[0] : 'Không thể tạo danh mục'}`);
      }
    } catch (err) {
      console.error("Lỗi tạo danh mục:", err);
    }
  };

  const fetchLocations = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/tours/locations/');
      if (res.ok) {
        const data = await res.json();
        setLocations(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error("Lỗi tải tỉnh/thành:", err);
    }
  };

  const handleCreateLocation = async () => {
    if (!newLocationName.trim()) return alert("Tên tỉnh/thành không được để trống!");
    const lat = parseFloat(newLocationLat);
    const lng = parseFloat(newLocationLng);
    if (Number.isNaN(lat) || Number.isNaN(lng)) {
      return alert("Vĩ độ và kinh độ phải là số hợp lệ!");
    }
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      const res = await fetch('http://127.0.0.1:8000/api/tours/locations/', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newLocationName.trim(), lat, lng }),
      });
      if (res.ok) {
        alert("Thêm tỉnh/thành thành công!");
        setNewLocationName('');
        setNewLocationLat('');
        setNewLocationLng('');
        fetchLocations();
      } else {
        const errData = await res.json().catch(() => ({}));
        const msg = errData.name?.[0] || errData.detail || errData.lat?.[0] || 'Không thể thêm';
        alert(`Lỗi: ${msg}`);
      }
    } catch (err) {
      console.error("Lỗi tạo tỉnh/thành:", err);
    }
  };

  const handleDeleteLocation = async (id) => {
    if (!window.confirm("Bạn có chắc muốn xóa tỉnh/thành này?")) return;
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/tours/locations/${id}/`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        alert("Xóa tỉnh/thành thành công!");
        fetchLocations();
      } else {
        alert("Xóa thất bại.");
      }
    } catch (err) {
      console.error("Lỗi xóa tỉnh/thành:", err);
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm("Bạn có chắc muốn xóa danh mục này?")) return;
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/tours/categories/${id}/`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        alert("Xóa danh mục thành công!");
        fetchCategories();
      } else {
        alert("Xóa danh mục thất bại.");
      }
    } catch (err) {
      console.error("Lỗi xóa danh mục:", err);
    }
  };

  // 1. HÀM NẠP DATA BAN ĐẦU - BẮT LỖI 401 VÀ AN TOÀN TUYỆT ĐỐI
  const fetchData = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert("Phiên đăng nhập đã hết hạn hoặc bạn không có quyền Admin. Vui lòng đăng nhập lại!");
      setLoading(false);
      return;
    }

    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

    try {
      setLoading(true);
      
      const [statsRes, usersRes, toursRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/users/admin/system-stats/', { headers }), 
        fetch('http://127.0.0.1:8000/api/users/admin/users/', { headers }),        
        fetch('http://127.0.0.1:8000/api/tours/admin/tours/', { headers }).then(async r => {
          if (!r.ok) {
            return fetch('http://127.0.0.1:8000/api/tours/', { headers });
          }
          return r;
        })
      ]);

      if (statsRes.status === 401 || usersRes.status === 401 || toursRes.status === 401) {
        alert("Phiên làm việc Admin đã hết hạn (401). Vui lòng đăng nhập lại hệ thống!");
        return;
      }

      let statsData = { data: { total_users: 0, total_tours: 0, total_revenue: 0 } };
      let usersData = [];
      let toursData = [];

      if (statsRes.ok) statsData = await statsRes.json();
      if (usersRes.ok) usersData = await usersRes.json();
      if (toursRes.ok) toursData = await toursRes.json();

      setStats(statsData.data || { total_users: 0, total_tours: 0, total_revenue: 0 });
      setUsers(Array.isArray(usersData) ? usersData : []);
      setAllTours(Array.isArray(toursData) ? toursData : []);
      fetchLocations();
    } catch (err) {
      console.error("Lỗi đồng bộ dữ liệu hệ thống Admin:", err);
    } finally {
      setLoading(false);
    }
  };

  // 2. HÀM PHÊ DUYỆT TOUR CỦA PROVIDER
  const handleTourAction = async (tourId, action) => {
    const token = localStorage.getItem('access_token');
    if (!token) return alert("Vui lòng đăng nhập tài khoản Admin.");

    let reason = '';
    if (action === 'reject') {
      reason = window.prompt('Nhập lý do từ chối tour (tùy chọn):', '') || '';
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/tours/admin/tours/${tourId}/approve/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, reason }) 
      });

      if (res.status === 401) {
        alert("Thao tác bị từ chối: Phiên đăng nhập Admin đã hết hạn.");
        return;
      }

      if (res.ok) {
        alert("Thao tác phê duyệt trạng thái hành trình thành công!");
        fetchData();
        if (mainTab === 'logs') fetchSystemLogs();
        if (mainTab === 'locations') fetchLocations();
      } else {
        const errData = await res.json().catch(() => ({}));
        alert(`Thất bại: ${errData.error || 'Lỗi từ server: ' + res.status}`);
      }
    } catch (error) {
      console.error("Lỗi kết nối API duyệt tour:", error);
    }
  };

  // 3. HÀM ĐỔI TRẠNG THÁI TÀI KHOẢN (KHÓA/MỞ)
  const handleToggleUserStatus = async (userId) => {
    const token = localStorage.getItem('access_token');
    if (!token) return alert("Vui lòng đăng nhập lại.");

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/users/admin/users/${userId}/toggle-status/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (res.status === 401) {
        alert("Phiên làm việc hết hạn. Không thể đổi trạng thái tài khoản lúc này.");
        return;
      }

      if (res.status === 405) {
        alert("Lỗi 405: Backend chưa cho phép phương thức POST tại URL toggle-status này.");
        return;
      }

      if (res.ok) {
        alert("Cập nhật trạng thái hoạt động tài khoản thành công!");
        fetchData(); 
      } else {
        alert(`Thay đổi trạng thái thất bại. Mã phản hồi: ${res.status}`);
      }
    } catch (error) {
      console.error("Lỗi kết nối API toggle user:", error);
    }
  };

  // 4. HÀM DUYỆT THANH TOÁN ĐƠN HÀNG (DAY 27 - KHANG)
  const handleApproveBooking = async (bookingId) => {
    const token = localStorage.getItem('access_token');
    if (!token) return alert("Vui lòng đăng nhập tài khoản Admin.");
    if (!window.confirm(`Bạn có chắc chắn muốn duyệt thanh toán cho đơn đặt tour #${bookingId}?`)) return;

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/tours/admin/bookings/${bookingId}/approve/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        alert("Duyệt đơn hàng thành công!");
        fetchBookings(bookingSearch);
        fetchPayments(paymentSearch);
        fetchData(); // Cập nhật lại tổng doanh thu
      } else {
        const errData = await res.json().catch(() => ({}));
        alert(`Duyệt thất bại: ${errData.error || 'Lỗi hệ thống'}`);
      }
    } catch (err) {
      console.error("Lỗi kết nối API duyệt đơn hàng:", err);
    }
  };

  const getCountByStatus = (status) => {
    if (status === 'all') return allTours.length;
    return allTours.filter(t => t.status === status).length;
  };

  // HÀM KIỂM TRA QUYỀN LINH HOẠT - KHẮC PHỤC LỖI HIỂN THỊ SAI VAI TRÒ
  const renderRoleBadge = (user) => {
    const roleStr = user.role ? String(user.role).toLowerCase() : 'customer';
    
    if (user.is_superuser || user.is_staff || roleStr === 'admin') {
        return <span className="role-badge role-admin">Quản trị</span>;
    }
    
    if (roleStr === 'provider') {
        return <span className="role-badge role-provider">Nhà cung cấp</span>;
    }
    
    return <span className="role-badge role-user">Khách hàng</span>;
};

  if (loading) return <div className="loading-screen">Đang đồng bộ trung tâm quản trị Admin...</div>;

  return (
    <div className="admin-shell">
      <main className="main-content">
        <h1 className="page-title">Dashboard Tổng quan quản trị</h1>
        
        {/* THỐNG KÊ */}
        <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '25px' }}>
          <div className="stat-card">
            <span className="stat-card-label">Tổng Users Hệ Thống</span>
            <div className="stat-card-value">{stats.total_users}</div>
          </div>
          <div className="stat-card">
            <span className="stat-card-label">Tổng Số Tour Toàn Sàn</span>
            <div className="stat-card-value">{stats.total_tours}</div>
          </div>
          <div className="stat-card">
            <span className="stat-card-label">Tổng Doanh Thu Sàn</span>
            <div className="stat-card-value" style={{ color: '#2ecc71' }}>
              {stats.total_revenue ? stats.total_revenue.toLocaleString() : 0} đ
            </div>
          </div>
        </div>

        {/* ĐIỀU HƯỚNG TABS CHÍNH */}
        <div className="admin-tab-container">
          <button 
            className={`admin-tab-btn ${mainTab === 'tours' ? 'active' : ''}`}
            onClick={() => setMainTab('tours')}
          >
            Quản lý Tour
          </button>
          <button 
            className={`admin-tab-btn ${mainTab === 'users' ? 'active' : ''}`}
            onClick={() => setMainTab('users')}
          >
            Quản lý Người dùng
          </button>
          <button 
            className={`admin-tab-btn ${mainTab === 'bookings' ? 'active' : ''}`}
            onClick={() => setMainTab('bookings')}
          >
            Quản lý Đơn đặt
          </button>
          <button 
            className={`admin-tab-btn ${mainTab === 'payments' ? 'active' : ''}`}
            onClick={() => setMainTab('payments')}
          >
            Nhật ký Giao dịch
          </button>
          <button 
            className={`admin-tab-btn ${mainTab === 'categories' ? 'active' : ''}`}
            onClick={() => setMainTab('categories')}
          >
            Loại Tour
          </button>
          <button 
            className={`admin-tab-btn ${mainTab === 'locations' ? 'active' : ''}`}
            onClick={() => setMainTab('locations')}
          >
            Tỉnh / Thành
          </button>
          <button 
            className={`admin-tab-btn ${mainTab === 'logs' ? 'active' : ''}`}
            onClick={() => setMainTab('logs')}
          >
            Nhật ký Hệ thống
          </button>
        </div>

        {/* TAB 1: QUẢN LÝ TOUR */}
        {mainTab === 'tours' && (
          <section className="chart-section">
            <div className="chart-card" style={{ width: '100%' }}>
              <p className="chart-card-title" style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>
                Quản lý phê duyệt trạng thái hành trình từ nhà cung cấp
              </p>
              
              <div className="status-tabs-container" style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '1px solid #e0e0e0', paddingBottom: '10px' }}>
                <button onClick={() => setCurrentTab('all')} style={{ padding: '8px 16px', border: 'none', background: currentTab === 'all' ? '#3498db' : '#f1f2f6', color: currentTab === 'all' ? '#fff' : '#2c3e50', borderRadius: '4px', cursor: 'pointer', fontWeight: '500' }}>
                  Tất cả ({getCountByStatus('all')})
                </button>
                <button onClick={() => setCurrentTab('pending')} style={{ padding: '8px 16px', border: 'none', background: currentTab === 'pending' ? '#f1c40f' : '#f1f2f6', color: currentTab === 'pending' ? '#fff' : '#2c3e50', borderRadius: '4px', cursor: 'pointer', fontWeight: '500' }}>
                  Chờ duyệt ({getCountByStatus('pending')})
                </button>
                <button onClick={() => setCurrentTab('approved')} style={{ padding: '8px 16px', border: 'none', background: currentTab === 'approved' ? '#2ecc71' : '#f1f2f6', color: currentTab === 'approved' ? '#fff' : '#2c3e50', borderRadius: '4px', cursor: 'pointer', fontWeight: '500' }}>
                  Đang hoạt động ({getCountByStatus('approved')})
                </button>
                <button onClick={() => setCurrentTab('rejected')} style={{ padding: '8px 16px', border: 'none', background: currentTab === 'rejected' ? '#e74c3c' : '#f1f2f6', color: currentTab === 'rejected' ? '#fff' : '#2c3e50', borderRadius: '4px', cursor: 'pointer', fontWeight: '500' }}>
                  Từ chối ({getCountByStatus('rejected')})
                </button>
              </div>
              
              {filteredTours.length === 0 ? (
                <p style={{ textAlign: 'center', padding: '30px', color: '#7f8c8d', fontStyle: 'italic' }}>Không có chương trình tour nào ứng với trạng thái lọc này.</p>
              ) : (
                <table className="user-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6', textAlign: 'left' }}>
                      <th style={{ padding: '12px' }}>Tên hành trình</th>
                      <th style={{ padding: '12px' }}>Giá niêm yết</th>
                      <th style={{ padding: '12px' }}>Trạng thái</th>
                      <th style={{ padding: '12px', textAlign: 'center' }}>Thao tác kiểm duyệt nhanh</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTours.map(tour => (
                      <tr key={tour.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                        <td style={{ padding: '12px', fontWeight: '500' }}>{tour.title}</td>
                        <td style={{ padding: '12px' }}>{tour.price ? tour.price.toLocaleString() : 0} đ</td>
                        <td style={{ padding: '12px' }}>
                          {tour.status === 'approved' && <span style={{ color: '#2ecc71', backgroundColor: '#e8f8f0', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '13px' }}>Đang hoạt động</span>}
                          {tour.status === 'pending' && <span style={{ color: '#f1c40f', backgroundColor: '#fef9e7', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '13px' }}>Chờ duyệt</span>}
                          {tour.status === 'rejected' && <span style={{ color: '#e74c3c', backgroundColor: '#fceae9', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '13px' }}>Từ chối</span>}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                            <button onClick={() => handleTourAction(tour.id, 'approve')} style={{ backgroundColor: tour.status === 'approved' ? '#bdc3c7' : '#2ecc71', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: tour.status === 'approved' ? 'not-allowed' : 'pointer' }} disabled={tour.status === 'approved'}>Duyệt</button>
                            <button onClick={() => handleTourAction(tour.id, 'pending')} style={{ backgroundColor: tour.status === 'pending' ? '#bdc3c7' : '#f1c40f', color: '#333', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: tour.status === 'pending' ? 'not-allowed' : 'pointer' }} disabled={tour.status === 'pending'}>Chờ</button>
                            <button onClick={() => handleTourAction(tour.id, 'reject')} style={{ backgroundColor: tour.status === 'rejected' ? '#bdc3c7' : '#e74c3c', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: tour.status === 'rejected' ? 'not-allowed' : 'pointer' }} disabled={tour.status === 'rejected'}>Từ chối</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        )}

        {/* TAB 2: QUẢN LÝ THÀNH VIÊN */}
        {mainTab === 'users' && (
          <section className="chart-section">
            <div className="chart-card">
              <p className="chart-card-title">Quản trị danh sách thành viên hệ thống</p>
              <table className="user-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Phân quyền vai trò</th>
                    <th style={{ textAlign: 'center' }}>Thao tác trạng thái nhanh</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => {
                    const isAdmin = u.username === 'admin' || u.username === 'khanh' || u.is_superuser === true || u.is_staff === true || (u.role && u.role.toLowerCase() === 'admin');
                    return (
                      <tr key={u.id}>
                        <td>{u.username}</td>
                        <td>{u.email || '---'}</td>
                        <td>
                          {isAdmin ? (
                            <span className="role-badge role-admin">Quản trị</span>
                          ) : u.role === 'provider' ? (
                            <span className="role-badge role-provider">Nhà cung cấp</span>
                          ) : (
                            <span className="role-badge role-user">Khách hàng</span>
                          )}
                        </td>
                        <td style={{ textAlign: 'center' }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '15px' }}>
                            {u.status === 'Active' && (
                              <span style={{ color: '#2ecc71', backgroundColor: 'rgba(46, 204, 113, 0.15)', padding: '5px 12px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', display: 'inline-block', minWidth: '100px' }}>
                                Đã kích hoạt
                              </span>
                            )}
                            {u.status === 'Banned' && (
                              <span style={{ color: '#e74c3c', backgroundColor: 'rgba(231, 76, 60, 0.15)', padding: '5px 12px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', display: 'inline-block', minWidth: '100px' }}>
                                Đang bị khóa
                              </span>
                            )}
                            {(u.status === 'Pending' || (!u.status && !u.is_active && !isAdmin)) && (
                              <span style={{ color: '#f1c40f', backgroundColor: 'rgba(241, 196, 15, 0.15)', padding: '5px 12px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', display: 'inline-block', minWidth: '100px' }}>
                                Chờ duyệt
                              </span>
                            )}
                            {isAdmin ? (
                              <span style={{ color: '#7f8c8d', fontSize: '12px', fontStyle: 'italic', minWidth: '110px', display: 'inline-block' }}>
                                Không thể thao tác
                              </span>
                            ) : (
                              <button 
                                onClick={() => handleToggleUserStatus(u.id)}
                                style={{ 
                                  backgroundColor: u.status === 'Active' ? '#e74c3c' : u.status === 'Banned' ? '#2ecc71' : '#3498db', 
                                  color: 'white', 
                                  border: 'none', 
                                  padding: '6px 14px', 
                                  borderRadius: '4px', 
                                  cursor: 'pointer',
                                  fontSize: '12px',
                                  fontWeight: '600',
                                  minWidth: '110px',
                                  transition: 'all 0.2s ease-in-out'
                                }}
                              >
                                {u.status === 'Active' ? 'Khóa lại' : u.status === 'Banned' ? 'Mở khóa ngay' : 'Phê duyệt'}
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* TAB 3: QUẢN LÝ ĐƠN HÀNG (DAY 27 - HÀ & KHANG) */}
        {mainTab === 'bookings' && (
          <section className="chart-section">
            <div className="chart-card" style={{ width: '100%' }}>
              <p className="chart-card-title" style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>
                Quản lý danh sách đơn đặt tour toàn hệ thống
              </p>
              
              {/* TÌM KIẾM ĐƠN HÀNG THEO MÃ/TÊN (KHANG CONNECT) */}
              <div className="admin-search-wrapper">
                <input 
                  type="text" 
                  className="admin-search-input"
                  placeholder="Tìm kiếm theo Mã đơn hàng (Booking ID), tên khách hàng hoặc tên Tour..."
                  value={bookingSearch}
                  onChange={(e) => setBookingSearch(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchBookings(bookingSearch)}
                />
                <button 
                  className="admin-search-btn"
                  onClick={() => fetchBookings(bookingSearch)}
                >
                  Tìm kiếm
                </button>
              </div>

              {bookings.length === 0 ? (
                <p style={{ textAlign: 'center', padding: '30px', color: '#7f8c8d', fontStyle: 'italic' }}>Không tìm thấy đơn đặt tour nào phù hợp.</p>
              ) : (
                <table className="user-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#23272a', textAlign: 'left' }}>
                      <th style={{ padding: '12px' }}>Mã đơn</th>
                      <th style={{ padding: '12px' }}>Tên Tour</th>
                      <th style={{ padding: '12px' }}>Khách hàng</th>
                      <th style={{ padding: '12px' }}>Liên hệ</th>
                      <th style={{ padding: '12px' }}>Ngày đi</th>
                      <th style={{ padding: '12px' }}>Số người</th>
                      <th style={{ padding: '12px' }}>Tổng tiền</th>
                      <th style={{ padding: '12px' }}>Trạng thái</th>
                      <th style={{ padding: '12px', textAlign: 'center' }}>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bookings.map(b => (
                      <tr key={b.id} style={{ borderBottom: '1px solid #2d3238' }}>
                        <td style={{ padding: '12px', fontWeight: 'bold', color: '#3498db' }}>#{b.id}</td>
                        <td style={{ padding: '12px', fontWeight: '500' }}>{b.tour_title}</td>
                        <td style={{ padding: '12px' }}>{b.username}</td>
                        <td style={{ padding: '12px', fontSize: '13px', color: '#99aab5' }}>
                          <div>{b.user_email}</div>
                          <div>{b.user_phone || 'N/A'}</div>
                        </td>
                        <td style={{ padding: '12px' }}>{b.booking_date}</td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>{b.number_of_people}</td>
                        <td style={{ padding: '12px', fontWeight: 'bold' }}>{Number(b.total_price).toLocaleString()} đ</td>
                        <td style={{ padding: '12px' }}>
                          {b.status === 'confirmed' && <span style={{ color: '#2ecc71', backgroundColor: 'rgba(46, 204, 113, 0.15)', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '13px' }}>Đã xác nhận</span>}
                          {b.status === 'pending' && b.payment_awaiting && (
                            <span style={{ color: '#e67e22', backgroundColor: 'rgba(230, 126, 34, 0.15)', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '13px' }}>Chờ Admin duyệt TT</span>
                          )}
                          {b.status === 'pending' && !b.payment_awaiting && (
                            <span style={{ color: '#f1c40f', backgroundColor: 'rgba(241, 196, 15, 0.15)', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '13px' }}>Chờ thanh toán</span>
                          )}
                          {b.status === 'cancelled' && <span style={{ color: '#e74c3c', backgroundColor: 'rgba(231, 76, 60, 0.15)', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '13px' }}>Đã hủy</span>}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          {b.status === 'pending' && b.payment_awaiting && (
                            <button 
                              onClick={() => handleApproveBooking(b.id)}
                              style={{ backgroundColor: '#2ecc71', color: '#ffffff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' }}
                            >
                              Duyệt thanh toán
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        )}

        {/* TAB 4: NHẬT KÝ GIAO DỊCH (DAY 27 - HÀ & KHÁNH) */}
        {mainTab === 'payments' && (
          <section className="chart-section">
            <div className="chart-card" style={{ width: '100%' }}>
              <p className="chart-card-title" style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>
                Lịch sử giao dịch thanh toán trên hệ thống
              </p>

              {/* TÌM KIẾM GIAO DỊCH */}
              <div className="admin-search-wrapper">
                <input 
                  type="text" 
                  className="admin-search-input"
                  placeholder="Tìm kiếm theo mã giao dịch, số tiền, tên khách hàng..."
                  value={paymentSearch}
                  onChange={(e) => setPaymentSearch(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchPayments(paymentSearch)}
                />
                <button 
                  className="admin-search-btn"
                  onClick={() => fetchPayments(paymentSearch)}
                >
                  Tìm kiếm
                </button>
              </div>

              {payments.length === 0 ? (
                <p style={{ textAlign: 'center', padding: '30px', color: '#7f8c8d', fontStyle: 'italic' }}>Không có lịch sử giao dịch nào phù hợp.</p>
              ) : (
                <table className="user-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#23272a', textAlign: 'left' }}>
                      <th style={{ padding: '12px' }}>Mã GD</th>
                      <th style={{ padding: '12px' }}>Mã Đơn</th>
                      <th style={{ padding: '12px' }}>Khách hàng</th>
                      <th style={{ padding: '12px' }}>Hành trình</th>
                      <th style={{ padding: '12px' }}>Số tiền</th>
                      <th style={{ padding: '12px' }}>Phương thức</th>
                      <th style={{ padding: '12px' }}>Mã tham chiếu (VNPay)</th>
                      <th style={{ padding: '12px' }}>Thời gian</th>
                      <th style={{ padding: '12px' }}>Trạng thái</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payments.map(p => (
                      <tr key={p.id} style={{ borderBottom: '1px solid #2d3238' }}>
                        <td style={{ padding: '12px', fontWeight: 'bold' }}>#{p.id}</td>
                        <td style={{ padding: '12px', color: '#3498db', fontWeight: '500' }}>#{p.booking_id}</td>
                        <td style={{ padding: '12px' }}>{p.username}</td>
                        <td style={{ padding: '12px' }}>{p.tour_title}</td>
                        <td style={{ padding: '12px', fontWeight: 'bold', color: '#2ecc71' }}>{Number(p.amount).toLocaleString()} đ</td>
                        <td style={{ padding: '12px' }}>{p.payment_method}</td>
                        <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '13px' }}>{p.transaction_code || '---'}</td>
                        <td style={{ padding: '12px', fontSize: '13px', color: '#99aab5' }}>{new Date(p.created_at).toLocaleString('vi-VN')}</td>
                        <td style={{ padding: '12px' }}>
                          {p.status.toUpperCase() === 'SUCCESS' ? (
                            <span style={{ color: '#2ecc71', backgroundColor: 'rgba(46, 204, 113, 0.15)', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px' }}>Thành công</span>
                          ) : p.status.toUpperCase() === 'PENDING' ? (
                            <span style={{ color: '#f1c40f', backgroundColor: 'rgba(241, 196, 15, 0.15)', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px' }}>Đang chờ</span>
                          ) : (
                            <span style={{ color: '#e74c3c', backgroundColor: 'rgba(231, 76, 60, 0.15)', padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px' }}>Thất bại</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        )}

        {/* TAB 5: LOẠI TOUR (DANH MỤC) */}
        {mainTab === 'categories' && (
          <section className="chart-section">
            <div className="chart-card" style={{ width: '100%' }}>
              <p className="chart-card-title" style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>
                Quản lý loại tour (Biển, Núi, Văn hóa…)
              </p>

              <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <input 
                  type="text" 
                  className="admin-search-input"
                  placeholder="Tên danh mục mới (VD: Biển, Núi...)"
                  value={newCategoryName}
                  onChange={(e) => setNewCategoryName(e.target.value)}
                  style={{ flex: 1 }}
                />
                <input 
                  type="text" 
                  className="admin-search-input"
                  placeholder="Mô tả..."
                  value={newCategoryDesc}
                  onChange={(e) => setNewCategoryDesc(e.target.value)}
                  style={{ flex: 2 }}
                />
                <button 
                  className="admin-search-btn"
                  onClick={handleCreateCategory}
                >
                  Thêm Danh Mục
                </button>
              </div>

              {categories.length === 0 ? (
                <p style={{ textAlign: 'center', padding: '30px', color: '#7f8c8d', fontStyle: 'italic' }}>Chưa có danh mục nào.</p>
              ) : (
                <table className="user-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#23272a', textAlign: 'left' }}>
                      <th style={{ padding: '12px', width: '60px' }}>ID</th>
                      <th style={{ padding: '12px', width: '200px' }}>Tên Danh Mục</th>
                      <th style={{ padding: '12px' }}>Mô tả</th>
                      <th style={{ padding: '12px', textAlign: 'center', width: '120px' }}>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categories.map(c => (
                      <tr key={c.id} style={{ borderBottom: '1px solid #2d3238' }}>
                        <td style={{ padding: '12px', fontWeight: 'bold' }}>#{c.id}</td>
                        <td style={{ padding: '12px', fontWeight: 'bold', color: '#3498db' }}>{c.name}</td>
                        <td style={{ padding: '12px', color: '#99aab5' }}>{c.description || '---'}</td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <button 
                            onClick={() => handleDeleteCategory(c.id)}
                            style={{ backgroundColor: '#e74c3c', color: '#ffffff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' }}
                          >
                            Xóa
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        )}

        {/* TAB 6: TỈNH / THÀNH */}
        {mainTab === 'locations' && (
          <section className="chart-section">
            <div className="chart-card" style={{ width: '100%' }}>
              <p className="chart-card-title" style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>
                Quản lý Tỉnh / Thành phố (tọa độ bản đồ)
              </p>

              <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
                <input
                  type="text"
                  className="admin-search-input"
                  placeholder="Tên tỉnh/thành (VD: Huế, Cần Thơ...)"
                  value={newLocationName}
                  onChange={(e) => setNewLocationName(e.target.value)}
                  style={{ flex: '1 1 200px' }}
                />
                <input
                  type="number"
                  step="any"
                  className="admin-search-input"
                  placeholder="Vĩ độ (lat)"
                  value={newLocationLat}
                  onChange={(e) => setNewLocationLat(e.target.value)}
                  style={{ flex: '0 1 140px' }}
                />
                <input
                  type="number"
                  step="any"
                  className="admin-search-input"
                  placeholder="Kinh độ (lng)"
                  value={newLocationLng}
                  onChange={(e) => setNewLocationLng(e.target.value)}
                  style={{ flex: '0 1 140px' }}
                />
                <button className="admin-search-btn" onClick={handleCreateLocation}>
                  Thêm Tỉnh/Thành
                </button>
              </div>
              <p style={{ fontSize: '13px', color: '#99aab5', marginBottom: '16px' }}>
                Gợi ý tọa độ: tra Google Maps → chuột phải điểm → copy lat/lng. API public: GET /api/tours/locations/
              </p>

              {locations.length === 0 ? (
                <p style={{ textAlign: 'center', padding: '30px', color: '#7f8c8d', fontStyle: 'italic' }}>
                  Chưa có tỉnh/thành. Chạy migrate hoặc thêm mới bên trên.
                </p>
              ) : (
                <table className="user-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#23272a', textAlign: 'left' }}>
                      <th style={{ padding: '12px', width: '60px' }}>ID</th>
                      <th style={{ padding: '12px', width: '200px' }}>Tên</th>
                      <th style={{ padding: '12px', width: '120px' }}>Vĩ độ</th>
                      <th style={{ padding: '12px', width: '120px' }}>Kinh độ</th>
                      <th style={{ padding: '12px', textAlign: 'center', width: '120px' }}>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {locations.map((loc) => (
                      <tr key={loc.id} style={{ borderBottom: '1px solid #2d3238' }}>
                        <td style={{ padding: '12px', fontWeight: 'bold' }}>#{loc.id}</td>
                        <td style={{ padding: '12px', fontWeight: 'bold', color: '#2ecc71' }}>{loc.name}</td>
                        <td style={{ padding: '12px', fontFamily: 'monospace' }}>{loc.lat}</td>
                        <td style={{ padding: '12px', fontFamily: 'monospace' }}>{loc.lng}</td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <button
                            onClick={() => handleDeleteLocation(loc.id)}
                            style={{ backgroundColor: '#e74c3c', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' }}
                          >
                            Xóa
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        )}

        {/* TAB 7: NHẬT KÝ HỆ THỐNG */}
        {mainTab === 'logs' && (
          <section className="chart-section">
            <div className="chart-card" style={{ width: '100%' }}>
              <p className="chart-card-title" style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>
                Nhật ký Hệ thống (System Logs)
              </p>

              {systemLogs.length === 0 ? (
                <p style={{ textAlign: 'center', padding: '30px', color: '#7f8c8d', fontStyle: 'italic' }}>Không có nhật ký nào.</p>
              ) : (
                <table className="user-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#23272a', textAlign: 'left' }}>
                      <th style={{ padding: '12px', width: '180px' }}>Thời gian</th>
                      <th style={{ padding: '12px', width: '150px' }}>Người dùng</th>
                      <th style={{ padding: '12px', width: '200px' }}>Hành động</th>
                      <th style={{ padding: '12px' }}>Chi tiết</th>
                      <th style={{ padding: '12px', width: '120px' }}>IP Address</th>
                    </tr>
                  </thead>
                  <tbody>
                    {systemLogs.map(log => (
                      <tr key={log.id} style={{ borderBottom: '1px solid #2d3238' }}>
                        <td style={{ padding: '12px', fontSize: '13px', color: '#99aab5' }}>{new Date(log.created_at).toLocaleString('vi-VN')}</td>
                        <td style={{ padding: '12px', fontWeight: 'bold', color: log.username ? '#2ecc71' : '#e74c3c' }}>{log.username || 'Hệ thống'}</td>
                        <td style={{ padding: '12px', fontWeight: '500', color: '#3498db' }}>{log.action}</td>
                        <td style={{ padding: '12px', fontSize: '13px' }}>{log.details || '---'}</td>
                        <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '13px' }}>{log.ip_address || '---'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}