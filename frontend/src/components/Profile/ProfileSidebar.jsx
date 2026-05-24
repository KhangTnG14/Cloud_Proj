import React from 'react';
import './ProfileSidebar.css';
import { isRegularCustomer } from '../../utils/roleUtils';

export default function ProfileSidebar({ activeTab, onChangeTab, user }) {
  const isRegularUser = isRegularCustomer(user);

  return (
    <aside className="profile-sidebar">
      <div className="sidebar-user">
        <img
          src={user?.avatar || 'https://www.w3schools.com/howto/img_avatar.png'}
          alt={user?.username || 'Avatar'}
          className="sidebar-avatar"
        />
        <h3>{user?.username || 'Người dùng'}</h3>
        <span className="sidebar-role">{user?.role || 'CUSTOMER'}</span>
      </div>

      <div className="sidebar-menu">
        <button
          className={activeTab === 'info' ? 'active' : ''}
          onClick={() => onChangeTab('info')}
        >
          Thông tin
        </button>
        {isRegularUser && (
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

        <button
          className={activeTab === 'reviews' ? 'active' : ''}
          onClick={() => onChangeTab('reviews')}
        >
          Đánh giá của tôi
        </button>
      </div>
    </aside>
  );
}