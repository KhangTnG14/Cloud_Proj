import React from 'react';
import './ProfileSidebar.css';

export default function ProfileSidebar({ activeTab, onChangeTab, user }) {
  const currentRole = user?.role?.toLowerCase();
  const isRestricted = currentRole === 'admin' || currentRole === 'provider';

  return (
    <aside className="profile-sidebar">
      <div className="sidebar-user">
        <img
          src={user?.avatar || 'https://www.w3schools.com/howto/img_avatar.png'}
          alt={user?.username || 'Avatar'}
          className="sidebar-avatar"
        />
        <h3>{user?.username || 'Người dùng'}</h3>
        <span className="sidebar-role">
          {currentRole === 'admin'
            ? 'ADMIN'
            : currentRole === 'provider'
            ? 'PROVIDER'
            : 'CUSTOMER'}
        </span>
      </div>

      <div className="sidebar-menu">
        <button
          className={activeTab === 'info' ? 'active' : ''}
          onClick={() => onChangeTab('info')}
        >
          Thông tin
        </button>

        {!isRestricted && (
          <button
            className={activeTab === 'history' ? 'active' : ''}
            onClick={() => onChangeTab('history')}
          >
            Lịch sử đặt tour
          </button>
        )}

        <button
          className={activeTab === 'password' ? 'active' : ''}
          onClick={() => onChangeTab('password')}
        >
          Đổi mật khẩu
        </button>

        {!isRestricted && (
          <button
            className={activeTab === 'reviews' ? 'active' : ''}
            onClick={() => onChangeTab('reviews')}
          >
            Đánh giá của tôi
          </button>
        )}
      </div>
    </aside>
  );
}