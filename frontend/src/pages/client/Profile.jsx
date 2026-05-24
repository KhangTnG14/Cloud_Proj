import React, { useEffect, useState } from 'react';
import './Profile.css';
import api from '../../api/axios.js';
import ProfileSidebar from '../../components/profile/ProfileSidebar';
import ProfileInfo from '../../components/profile/ProfileInfo';
import BookingHistory from '../../components/profile/BookingHistory';
import ChangePassword from '../../components/profile/ChangePassword';
import MyReviews from './MyReviews';

export default function Profile() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('info');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMe = async () => {
      try {
        const response = await api.get('me/');
        const roleRes = await api.get('users/role/');
        console.log('Role từ API:', response.data?.role);
        console.log('Role từ role API:', roleRes.data);

        setUser({ ...response.data, role: roleRes.data.role });
      } catch (error) {
        console.error('Lỗi lấy thông tin cá nhân:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchMe();

    const interval = setInterval(() => {
      api.get('me/');
    }, 20000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!user || loading) return;
    const currentRole = user?.role?.toLowerCase();

    if (
      (currentRole === 'admin' || currentRole === 'provider') &&
      (activeTab === 'history' || activeTab === 'reviews')
    ) {
      setActiveTab('info');
    }
  }, [user, activeTab, loading]);

  if (loading) return <div className="loading">Đang tải...</div>;

  const currentRole = user?.role?.toLowerCase();
  const isRestricted = currentRole === 'admin' || currentRole === 'provider';

  return (
    <div className="profile-dashboard">
      <ProfileSidebar activeTab={activeTab} onChangeTab={setActiveTab} user={user} />

      <div className="profile-main">
        {activeTab === 'info' && <ProfileInfo user={user} onProfileUpdated={setUser} />}

        {activeTab === 'history' && !isRestricted && <BookingHistory />}

        {activeTab === 'password' && <ChangePassword />}

        {activeTab === 'reviews' && !isRestricted && <MyReviews />}
      </div>
    </div>
  );
}