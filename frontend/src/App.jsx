import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Home from './pages/client/Home';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import Introduce from "./pages/client/Introduce";
import Header from './components/common/Header/Header';
import TourDetail from './pages/client/TourDetail/TourDetail';
import Profile from './pages/client/Profile';
import SearchResult from './pages/client/SearchResult/SearchResult';
import ToursPage from './components/tour/ToursPage';
import MyOrders from './pages/client/MyOrders/MyOrders';
import PaymentSelection from './pages/client/Payment/PaymentSelection';
import PaymentResult from './pages/client/Payment/PaymentResult';
import Contact from './pages/client/Contact/Contact';
import MyReviews from './pages/client/MyReviews';
import ProviderDashboard from './pages/provider/ProviderDashboard';
import ProviderCustomers from './pages/provider/ProviderCustomers';
import AdminDashboard from './pages/admin/AdminDashboard';
import BookingHistory from './components/profile/BookingHistory';
import CustomerOnlyRoute from './components/auth/CustomerOnlyRoute';

function AppContent() {
  const location = useLocation();
  // Ẩn Navbar trên trang đăng nhập, đăng ký và quên mật khẩu
  const hideNavbar = ['/login', '/register', '/forgot-password'].includes(location.pathname);

  return (
    <>
      {!hideNavbar && <Header />}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/introduce" element={<Introduce />} />
        <Route path="/tours" element={<ToursPage />} />
        <Route path="/tours/:id" element={<TourDetail />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/search" element={<SearchResult />} />
        <Route path="/my-orders" element={<MyOrders />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/booking-history" element={<CustomerOnlyRoute><BookingHistory /></CustomerOnlyRoute>} />
        <Route path="/payment/:bookingId" element={<PaymentSelection />} />
        <Route path="/payment-result" element={<PaymentResult />} />
        <Route path="/my-reviews" element={<CustomerOnlyRoute><MyReviews /></CustomerOnlyRoute>} />
        <Route path="/provider/dashboard" element={<ProviderDashboard />} />
        <Route path="/provider/customers" element={<ProviderCustomers />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
      </Routes>
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;