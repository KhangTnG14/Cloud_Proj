import React from 'react';
import { Navigate } from 'react-router-dom';
import { isRegularCustomer } from '../../utils/roleUtils';

export default function CustomerOnlyRoute({ children }) {
  if (!isRegularCustomer()) {
    const role = (localStorage.getItem('role') || '').toLowerCase();
    if (role === 'admin' || role === 'staff') {
      return <Navigate to="/admin/dashboard" replace />;
    }
    if (role === 'provider' || role === 'creator') {
      return <Navigate to="/provider/dashboard" replace />;
    }
    return <Navigate to="/" replace />;
  }

  return children;
}
