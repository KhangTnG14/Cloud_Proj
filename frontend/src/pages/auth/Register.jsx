import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axiosClient from '../../api/axiosClient';
import './Register.css';
import travelImg from '../../assets/travel.png';

export default function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    role: 'CUSTOMER'
  });

  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrorMsg(''); // Xóa lỗi khi user nhập lại
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Kiểm tra mật khẩu
    if (formData.password !== formData.confirmPassword) {
      setErrorMsg("Mật khẩu xác nhận không khớp!");
      return;
    }

    if (formData.password.length < 8) {
      setErrorMsg("Mật khẩu phải có ít nhất 8 ký tự!");
      return;
    }

    try {
      await axiosClient.post('users/register/', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        phone: formData.phone,
        role: formData.role
      });

      setErrorMsg('');
      setSuccessMsg("Đăng ký thành công! Đang chuyển sang đăng nhập...");

      setTimeout(() => {
        navigate('/login');
      }, 1500);

    } catch (error) {
      console.error("Lỗi đăng ký:", error.response?.data);

      const data = error.response?.data;
      
      if (data) {
        // Tổng hợp tất cả lỗi từ Backend DRF trả về thành một chuỗi văn bản
        const messages = [];

        if (data.email) messages.push(`Email: ${data.email[0]}`);
        if (data.phone) messages.push(`Số điện thoại: ${data.phone[0]}`);
        if (data.password) messages.push(`Mật khẩu: ${data.password[0]}`);
        if (data.username) messages.push(`Tên đăng nhập: ${data.username[0]}`);
        if (data.message) messages.push(data.message);
        if (data.error) messages.push(data.error);

        setErrorMsg(messages.length > 0 ? messages.join(' | ') : "Đăng ký thất bại!");
      } else {
        setErrorMsg("Đăng ký thất bại! Vui lòng thử lại.");
      }
      
      setSuccessMsg('');
    }
  };

  return (
    <div className="register-container">
      {/* IMAGE SECTION (Bên trái) */}
      <div className="register-image-section">
        <img src={travelImg} alt="Travel Illustration" className="illustration" />
      </div>

      {/* FORM SECTION (Bên phải) */}
      <div className="register-form-section">
        <div className="reg-form-wrapper">
          <h2 className="reg-form-title">ĐĂNG KÝ</h2>

          <form className="register-form" onSubmit={handleSubmit}>

            {/* USERNAME */}
            <div className="reg-input-group">
              <label>Tên đăng nhập: <span>*</span></label>
              <input
                type="text"
                name="username"
                placeholder="Nhập tên đăng nhập"
                value={formData.username}
                onChange={handleChange}
                className={errorMsg ? "input-error" : ""}
                required
              />
            </div>

            {/* PHONE */}
            <div className="reg-input-group">
              <label>Số điện thoại: <span>*</span></label>
              <input
                type="text"
                name="phone"
                placeholder="Nhập số điện thoại"
                value={formData.phone}
                onChange={handleChange}
                className={errorMsg ? "input-error" : ""}
                required
              />
            </div>

            {/* EMAIL */}
            <div className="reg-input-group">
              <label>Email: <span>*</span></label>
              <input
                type="email"
                name="email"
                placeholder="Nhập địa chỉ email"
                value={formData.email}
                onChange={handleChange}
                className={errorMsg ? "input-error" : ""}
                required
              />
            </div>

            {/* ROLE RADIO SELECTION */}
            <div className="reg-input-group">
              <label>Bạn là:</label>
              <div className="role-options">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="role"
                    value="CUSTOMER"
                    checked={formData.role === 'CUSTOMER'}
                    onChange={handleChange}
                  />
                  Khách du lịch
                </label>

                <label className="radio-label">
                  <input
                    type="radio"
                    name="role"
                    value="PROVIDER"
                    checked={formData.role === 'PROVIDER'}
                    onChange={handleChange}
                  />
                  Nhà cung cấp
                </label>
              </div>
            </div>

            {/* PASSWORD */}
            <div className="reg-input-group">
              <label>Mật khẩu: <span>*</span></label>
              <input
                type="password"
                name="password"
                placeholder="Nhập mật khẩu (tối thiểu 8 ký tự)"
                value={formData.password}
                onChange={handleChange}
                className={errorMsg ? "input-error" : ""}
                required
              />
            </div>

            {/* CONFIRM PASSWORD */}
            <div className="reg-input-group">
              <label>Nhập lại mật khẩu: <span>*</span></label>
              <input
                type="password"
                name="confirmPassword"
                placeholder="Xác nhận lại mật khẩu"
                value={formData.confirmPassword}
                onChange={handleChange}
                className={errorMsg ? "input-error" : ""}
                required
              />
            </div>

            {/* ERROR MESSAGE */}
            {errorMsg && <p className="error-message">{errorMsg}</p>}

            {/* SUCCESS MESSAGE */}
            {successMsg && <p className="success-message">{successMsg}</p>}

            {/* BUTTON SUBMIT */}
            <button type="submit" className="btn-finish">
              HOÀN TẤT
            </button>

            {/* FOOTER */}
            <div className="login-footer">
              <p>Đã có tài khoản?</p>
              <Link to="/login" className="login-now-link">
                Đăng nhập ngay
              </Link>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
}