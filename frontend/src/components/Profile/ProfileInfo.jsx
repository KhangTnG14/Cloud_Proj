// frontend/src/components/Profile/ProfileInfo.jsx

import React, { useEffect, useState, useRef } from 'react';
import { updateProfile } from '../../api/tourApi';
import axiosClient from '../../api/axiosClient';
import './ProfileInfo.css';

import cameraIcon from '../../assets/dslr-camera.png';
import loadingIcon from '../../assets/sand-clock.png';
import uploadImage from '../../assets/image.png';
export default function ProfileInfo({ user, onProfileUpdated }) {
  const [phone, setPhone]               = useState(user?.phone || '');
  const [avatarUrl, setAvatarUrl]       = useState(user?.avatar || '');
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [uploading, setUploading]       = useState(false);
  const [loading, setLoading]           = useState(false);
  const [message, setMessage]           = useState('');
  const [error, setError]               = useState('');

  const fileInputRef = useRef();

  useEffect(() => {
    setPhone(user?.phone || '');
    setAvatarUrl(user?.avatar || '');
    setAvatarPreview(null); // Reset preview khi user thay đổi
  }, [user]);

  // ===== XỬ LÝ UPLOAD ẢNH TỪ THIẾT BỊ =====
  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Kiểm tra định dạng
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
      setError('Chỉ chấp nhận file JPG, PNG, WEBP.');
      return;
    }

    // Kiểm tra dung lượng (tối đa 2MB)
    if (file.size > 2 * 1024 * 1024) {
      setError('File quá lớn. Tối đa 2MB.');
      return;
    }

    // Hiện preview ngay lập tức
    setAvatarPreview(URL.createObjectURL(file));
    setError('');
    setMessage('');
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('avatar', file);

      const res = await axiosClient.post('/users/upload-avatar/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      // Cập nhật URL avatar mới từ server
      setAvatarUrl(res.data.avatar_url);
      onProfileUpdated(res.data.user);
      setMessage('Cập nhật ảnh đại diện thành công!');
    } catch (err) {
      setAvatarPreview(null); // Reset preview nếu lỗi
      setError(
        err.response?.data?.detail || 'Upload ảnh thất bại. Vui lòng thử lại.'
      );
    } finally {
      setUploading(false);
    }
  };

  // ===== XỬ LÝ LƯU THÔNG TIN (CHỈ SĐT) =====
  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      const res = await updateProfile({ phone });
      onProfileUpdated(res.user);
      setMessage(res.message || 'Cập nhật thành công');
    } catch (err) {
      setError(
        err.response?.data?.phone ||
        err.response?.data?.detail ||
        'Cập nhật thất bại'
      );
    } finally {
      setLoading(false);
    }
  };

  // Ảnh hiển thị: ưu tiên preview → avatar url → ảnh mặc định
  const displayAvatar = avatarPreview || avatarUrl || 'https://www.w3schools.com/howto/img_avatar.png';

  return (
    <div className="profile-info-card">

      {/* ===== HEADER: Avatar + Tên ===== */}
      <div className="profile-header">
        <div className="avatar-wrapper">
          <img
            src={displayAvatar}
            alt="Avatar"
            className="profile-avatar"
          />
          {/* Nút camera nhỏ góc dưới ảnh */}
          <button
            type="button"
            className="avatar-change-btn"
            onClick={() => fileInputRef.current.click()}
            disabled={uploading}
            title="Đổi ảnh đại diện"
          >
            <img
              src={uploading ? loadingIcon : cameraIcon}
              alt="camera"
              className="icon-small"
            />
          </button>
        </div>
        <h2>{user?.username}</h2>
        <span className="profile-role">{user?.role}</span>
      </div>

      {/* ===== KHU VỰC UPLOAD AVATAR ===== */}
      <div className="avatar-upload-section">
        {/* Input file ẩn */}
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleAvatarUpload}
        />

        {/* Nút upload chính */}
        <button
          type="button"
          className="btn-upload-avatar"
          onClick={() => fileInputRef.current.click()}
          disabled={uploading}
        >
          <img
            src={uploading ? loadingIcon : uploadImage}
            alt="upload"
            className="icon-small"
          />
          {uploading ? 'Đang upload...' : 'Upload từ thiết bị'}
          {/* {uploading ? ' Đang upload...' : ' Upload từ thiết bị'} */}
        </button>

        <p className="upload-hint">JPG, PNG, WEBP · Tối đa 2MB</p>
      </div>

      {/* ===== THÔNG TIN CHI TIẾT ===== */}
      <div className="profile-details">
        <div className="info-item">
          <label>Email:</label>
          <span>{user?.email || 'N/A'}</span>
        </div>
        <div className="info-item">
          <label>Số điện thoại:</label>
          <span>{user?.phone || 'N/A'}</span>
        </div>
        <div className="info-item">
          <label>ID người dùng:</label>
          <span>#{user?.id}</span>
        </div>
      </div>

      {/* ===== FORM CẬP NHẬT SĐT ===== */}
      <form className="profile-update-form" onSubmit={handleSubmit}>
        <label>Số điện thoại mới</label>
        <input
          type="text"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="Nhập số điện thoại"
        />

        <button type="submit" disabled={loading}>
          {loading ? 'Đang lưu...' : 'Lưu thay đổi'}
        </button>

        {message && <div className="success-text">{message}</div>}
        {error && <div className="error-text">{error}</div>}
      </form>
    </div>
  );
}