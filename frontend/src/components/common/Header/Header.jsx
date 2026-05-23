import React, { useState } from 'react'; 
import { Link, useLocation, useNavigate } from 'react-router-dom'; 
import Logo from '../../../assets/logo.png'; 
import Search from '../../../assets/search.png';
import User from '../../../assets/user.png';
import Order from '../../../assets/order.png';
import Logout from '../../../assets/logout.png';
import './Header.css';

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate(); 
  const [searchTerm, setSearchTerm] = useState('');

  const token = localStorage.getItem('access_token');
  const username = localStorage.getItem('username');
  const role = localStorage.getItem('role') ? localStorage.getItem('role').toLowerCase() : '';

  const isActive = (path) => location.pathname === path;

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchTerm.trim())}`);
      setSearchTerm(''); 
    }
  };

  return (
    <header className="header-container">
      <nav className="navbar">
        <div className="navbar-logo" onClick={() => navigate('/')}>
          <img src={Logo} alt="Travela Logo" />
          <span>H2KT</span>
        </div>
        
        <ul className="navbar-links">
          <li className={isActive('/') ? 'active' : ''}>
            <Link to="/">Trang Chủ</Link>
          </li>
          <li className={isActive('/introduce') ? 'active' : ''}>
            <Link to="/introduce">Giới Thiệu</Link>
          </li>
          <li className={isActive('/tours') ? 'active' : ''}>
            <Link to="/tours">Tours</Link>
          </li>
          <li className={isActive('/contact') ? 'active' : ''}>
            <Link to="/contact">Liên Hệ</Link>
          </li>
          
          {role === 'provider' && (
            <li className={isActive('/provider/dashboard') ? 'active' : ''}>
              <Link to="/provider/dashboard" >Nhà Cung Cấp</Link>
            </li>
          )}

          {role === 'admin' && (
            <li className={isActive('/admin/dashboard') ? 'active' : ''}>
              <Link to="/admin/dashboard" style={{ color: '#cc2e2e', fontWeight: 'bold' }}>Kênh Admin</Link>
            </li>
          )}
        </ul>

        <div className="navbar-actions">
          <form className="search-wrapper" onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center', background: '#f5f5f5', borderRadius: '20px', padding: '2px 10px', marginRight: '10px' }}>
            <input 
              type="text" 
              placeholder="Tìm tour..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ border: 'none', background: 'transparent', outline: 'none', padding: '5px', width: '120px' }}
            />
            <button type="submit" className="btn-search" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
              <img src={Search} alt="search" />
            </button>
          </form>

          <Link to="/tours" className="btn-book">Book Now ↗</Link>
          
          {/* ==========================================================================
             AUTH SECTION REFACTOR (Hộp tài khoản Dropdown cao cấp tích hợp Icon)
             ========================================================================== */}
          <div className="auth-section">
            {token ? (
              <div className="user-dropdown-wrapper">
                {/* Khu vực kích hoạt khi hover vào */}
                <div className="user-profile-trigger">
                  <img src={User} alt="user" className="auth-icon" />
                  <span className="nav-username">{username}</span>
                  <span className="dropdown-arrow">▾</span>
                </div>

                {/* Hộp menu thả xuống ẩn */}
                <div className="dropdown-menu">
                  <Link to="/profile" className="dropdown-item">
                    <img src={User} alt="profile icon" className="menu-item-icon" />
                    Trang cá nhân
                  </Link>
                  
                  <Link to="/booking-history" className="dropdown-item">
                    <img src={Order} alt="order icon" className="menu-item-icon" />
                    Đơn đặt của tôi
                  </Link>
                  
                  <div className="dropdown-divider"></div>
                  
                  <button 
                    onClick={() => {
                      localStorage.clear();
                      window.location.href = '/login';
                    }} 
                    className="dropdown-item logout-item"
                  >
                    <img src={Logout} alt="logout icon" className="menu-item-icon logout-icon" />
                    Đăng xuất
                  </button>
                </div>
              </div>
            ) : (
              <Link to="/login" className="auth-link login-btn-nav">Đăng nhập</Link>
            )}
          </div>
          {/* ========================================================================== */}

        </div>
      </nav>
    </header>
  );
}