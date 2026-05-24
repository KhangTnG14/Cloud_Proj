import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axiosClient from '../../api/axiosClient';
import './ForgotPassword.css';
import travelImg from '../../assets/travel.png';

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0); // 0: Email, 1: OTP, 2: New Password
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Gửi y/c lấy mã OTP
  const handleRequestOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    try {
      await axiosClient.post('users/forgot-password/', { email });
      setSuccessMsg(`Mã OTP đã được gửi đến ${email}`);
      setStep(1);
    } catch (error) {
      if (error.response?.data?.email) {
        setErrorMsg('Email không hợp lệ.');
      } else {
        const detail = error.response?.data?.error || error.response?.data?.message || error.message;
        setErrorMsg(`Lỗi: ${detail}`);
      }
    } finally {
      setLoading(false);
    }
  };

  // Xác thực mã OTP
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    try {
      await axiosClient.post('users/verify-otp/', { email, otp });
      setSuccessMsg('Xác thực thành công. Vui lòng đặt mật khẩu mới.');
      setStep(2);
    } catch (error) {
      if (error.response?.data?.otp) {
        setErrorMsg('Mã OTP phải có 6 chữ số.');
      } else {
        setErrorMsg(error.response?.data?.error || 'Mã OTP không đúng hoặc đã hết hạn.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Đặt lại mật khẩu mới
  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setErrorMsg('Mật khẩu nhập lại không khớp.');
      return;
    }
    setLoading(true);
    setErrorMsg('');
    try {
      await axiosClient.post('users/reset-password/', { 
        email, 
        otp, 
        new_password: newPassword 
      });
      alert('Đặt lại mật khẩu thành công! Vui lòng đăng nhập lại.');
      navigate('/login');
    } catch (error) {
      if (error.response?.data?.new_password) {
        setErrorMsg('Mật khẩu quá yếu hoặc không hợp lệ.');
      } else {
        setErrorMsg(error.response?.data?.error || 'Có lỗi xảy ra khi đặt lại mật khẩu.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-container">
      {/* IMAGE SECTION (Bên trái) */}
      <div className="forgot-password-image-section">
        <img src={travelImg} alt="Travel Illustration" className="illustration" />
      </div>

      {/* FORM SECTION (Bên phải) */}
      <div className="forgot-password-form-section">
        <div className="form-wrapper">
          <h2 className="form-title">QUÊN MẬT KHẨU</h2>
          
          {successMsg && <div className="success-message">{successMsg}</div>}

          {/* STEP 0: NHẬP EMAIL */}
          {step === 0 && (
            <form onSubmit={handleRequestOTP}>
              <p className="form-subtitle">Nhập email của bạn để nhận mã xác thực (OTP).</p>
              <div className="input-group">
                <label>Email: <span>*</span></label>
                <input
                  type="email"
                  placeholder="Nhập email của bạn"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={errorMsg ? "input-error" : ""}
                  required
                />
              </div>
              {errorMsg && <p className="error-message">{errorMsg}</p>}
              <button type="submit" className="btn-submit" disabled={loading}>
                {loading ? 'ĐANG GỬI...' : 'GỬI MÃ XÁC THỰC'}
              </button>
            </form>
          )}

          {/* STEP 1: NHẬP OTP */}
          {step === 1 && (
            <form onSubmit={handleVerifyOTP}>
              <p className="form-subtitle">Vui lòng nhập mã OTP 6 chữ số đã được gửi qua email.</p>
              <div className="input-group">
                <label>Mã OTP: <span>*</span></label>
                <input
                  type="text"
                  placeholder="Nhập mã OTP"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  maxLength={6}
                  className={errorMsg ? "input-error" : ""}
                  required
                />
              </div>
              {errorMsg && <p className="error-message">{errorMsg}</p>}
              <button type="submit" className="btn-submit" disabled={loading}>
                {loading ? 'ĐANG XÁC THỰC...' : 'XÁC THỰC MÃ'}
              </button>
              <button type="button" className="btn-back-link" onClick={() => { setStep(0); setErrorMsg(''); }}>
                Quay lại nhập Email
              </button>
            </form>
          )}

          {/* STEP 2: NHẬP MẬT KHẨU MỚI */}
          {step === 2 && (
            <form onSubmit={handleResetPassword}>
              <p className="form-subtitle">Đặt mật khẩu mới cho tài khoản của bạn.</p>
              <div className="input-group">
                <label>Mật khẩu mới: <span>*</span></label>
                <input
                  type="password"
                  placeholder="Nhập mật khẩu mới"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className={errorMsg ? "input-error" : ""}
                  required
                  minLength={8}
                />
              </div>
              <div className="input-group">
                <label>Nhập lại mật khẩu: <span>*</span></label>
                <input
                  type="password"
                  placeholder="Nhập lại mật khẩu mới"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={errorMsg ? "input-error" : ""}
                  required
                />
              </div>
              {errorMsg && <p className="error-message">{errorMsg}</p>}
              <button type="submit" className="btn-submit" disabled={loading}>
                {loading ? 'ĐANG CẬP NHẬT...' : 'ĐỔI MẬT KHẨU'}
              </button>
            </form>
          )}

          {/* REGISTER FOOTER */}
          <div className="register-footer">
            <Link to="/login" className="register-link">
              Quay lại đăng nhập
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}