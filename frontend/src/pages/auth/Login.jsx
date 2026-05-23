import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axiosClient from '../../api/axiosClient';
import './Login.css';
import travelImg from '../../assets/travel.png';

export default function Login() {
  const navigate = useNavigate();

  // GIỮ NGUYÊN: State quản lý dữ liệu Form
  const [loginData, setLoginData] = useState({
    username: '',
    password: ''
  });

  const [errorMsg, setErrorMsg] = useState('');

  // GIỮ NGUYÊN: Hàm bắt sự kiện thay đổi input
  const handleChange = (e) => {
    setLoginData({ ...loginData, [e.target.name]: e.target.value });
  };

  // CẬP NHẬT: Hàm xử lý Đăng nhập tích hợp phân quyền động
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosClient.post('users/login/', loginData);

      console.log("Dữ liệu đăng nhập thành công:", response.data);
      
      // 1. Lưu dữ liệu vào localStorage
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('username', response.data.username);
      localStorage.setItem('role', response.data.role);

      // 2. Cập nhật ngay Token vào header axiosClient để tránh lỗi bất đồng bộ khi chuyển trang
      if (axiosClient.defaults.headers.common) {
        axiosClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      }

      setErrorMsg('');

      // 3. Logic điều hướng động dựa trên role từ Backend trả về
      const userRole = response.data.role?.toLowerCase(); 
      
      if (userRole === 'admin' || userRole === 'staff') {
        console.log("Tài khoản quyền quản trị -> Chuyển hướng sang Admin Dashboard");
        navigate('/admin/dashboard');
      } else {
        console.log("Tài khoản quyền khách hàng -> Chuyển hướng về Trang chủ");
        navigate('/');
      }

    } catch (error) {
      console.error("Lỗi đăng nhập:", error.response?.data);
      setErrorMsg("Sai tài khoản hoặc mật khẩu!");
    }
  };

  return (
    <div className="login-container">
      {/* IMAGE SECTION (Bên trái) */}
      <div className="login-image-section">
        <img src={travelImg} alt="Travel Illustration" className="illustration" />
      </div>

      {/* FORM SECTION (Bên phải) */}
      <div className="login-form-section">
        <div className="form-wrapper">
          <h2 className="form-title">ĐĂNG NHẬP</h2>

          <form className="login-form" onSubmit={handleSubmit}>
            {/* USERNAME */}
            <div className="input-group">
              <label>Tên đăng nhập: <span>*</span></label>
              <input
                type="text"
                name="username"
                placeholder="Nhập tên đăng nhập"
                value={loginData.username}
                onChange={handleChange}
                className={errorMsg ? "input-error" : ""}
                required
              />
            </div>

            {/* PASSWORD */}
            <div className="input-group">
              <label>Mật khẩu: <span>*</span></label>
              <input
                type="password"
                name="password"
                placeholder="Nhập mật khẩu"
                value={loginData.password}
                onChange={handleChange}
                className={errorMsg ? "input-error" : ""}
                required
              />
            </div>

            {/* ERROR MESSAGE */}
            {errorMsg && <p className="error-message">{errorMsg}</p>}

            {/* OPTIONS (Nhớ mật khẩu & Quên mật khẩu) */}
            <div className="form-options">
              <label className="remember-me">
                <input type="checkbox" name="remember" />
                <span>Nhớ mật khẩu</span>
              </label>
              <Link to="/forgot-password" className="forgot-link">
                Quên mật khẩu
              </Link>
            </div>

            {/* BUTTON SUBMIT */}
            <button type="submit" className="btn-login">
              ĐĂNG NHẬP
            </button>

            {/* REGISTER FOOTER */}
            <div className="register-footer">
              <p>Chưa có tài khoản?</p>
              <Link to="/register" className="register-link">
                Đăng ký ngay
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}