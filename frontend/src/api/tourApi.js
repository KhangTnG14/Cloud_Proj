import axiosClient from './axiosClient';

const MEDIA_BASE = 'http://127.0.0.1:8000';
const DEFAULT_TOUR_IMAGE = 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e';

export const formatTourImageUrl = (url) => {
    if (!url) return null;
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    return `${MEDIA_BASE}${url.startsWith('/') ? url : `/${url}`}`;
};

export const getTourDisplayImage = (tour, fallback = DEFAULT_TOUR_IMAGE) => {
    if (tour?.tour_images?.length > 0) {
        const fromUpload = formatTourImageUrl(tour.tour_images[0].image);
        if (fromUpload) return fromUpload;
    }
    if (tour?.image_url) {
        const fromUrl = formatTourImageUrl(tour.image_url);
        if (fromUrl) return fromUrl;
    }
    return fallback;
};

export const isCustomerTourVisible = (tour) => {
    if (tour.status !== 'approved') return false;
    if (Number(tour.slots) <= 0) return false;
    if (tour.departure_date) {
        const now = new Date();
        const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
        if (tour.departure_date <= today) return false;
    }
    return true;
};

// Lấy danh sách tất cả tour (Khang đã làm)
export const getTours = async() => {
    const response = await axiosClient.get('tours/');
    return Array.isArray(response.data) ? response.data : [];
};

export const getCategories = async () => {
    const response = await axiosClient.get('tours/categories/');
    return Array.isArray(response.data) ? response.data : [];
};

// Lấy chi tiết 1 tour dựa trên ID (Hà dùng cái này)
export const getTourById = async(id) => {
    const response = await axiosClient.get(`tours/${id}/`);
    return response.data;
};
// gọi API xử lí thông báo người dùng (Hà làm)
export const createBooking = async(data) => {
    // Phải gửi kèm Token trong Header để Tân xác thực
    const response = await axiosClient.post('/bookings/', data);
    return response.data;
};

// Upload nhiều ảnh cho tour (Nhiệm vụ Khang)
export const uploadTourImages = async(tourId, files) => {
    const formData = new FormData();
    // Gắn các file vào field 'images' giống như Backend đang chờ
    files.forEach(file => {
        formData.append('images', file);
    });

    const token = localStorage.getItem('access_token');

    const response = await axiosClient.post(`tours/${tourId}/upload-images/`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
        },
    });
    return response.data;
};

// --- THÊM HÀM CHO NGÀY 13 (HÀ & KHANG) ---

// // Lấy danh sách đơn hàng của người dùng đang đăng nhập
// export const getMyBookings = async() => {
//     const response = await axiosClient.get('tours/my-bookings/');
//     return response.data;
// };

// Hủy đơn hàng dựa trên ID
export const cancelBooking = async(id) => {
    const response = await axiosClient.patch(`tours/bookings/${id}/`);
    return response.data;
};

// call API tạo liên kết thanh toán VNPay
const handleProcessPayment = async() => {
    try {
        // Gọi API của Khánh để lấy link
        const res = await axiosClient.post('/create-payment/', { booking_id: bookingId });

        if (res.data.payment_url) {
            // Chuyển hướng trình duyệt sang VNPay
            window.location.href = res.data.payment_url;
        }
    } catch (error) {
        alert("Không thể tạo liên kết thanh toán. Vui lòng thử lại!");
    }
};

// --- NGÀY 18: API ĐÁNH GIÁ TOUR (KHANG) ---
export const addReview = async (tourId, data) => {
    // data: { rating, content }
    const response = await axiosClient.post(`tours/${tourId}/reviews/`, data);
    return response.data;
};

export const getMyBookings = async () => {
  const response = await axiosClient.get('tours/my-bookings/');
  return response.data;
};

export const updateProfile = async (data) => {
  const response = await axiosClient.put('users/profile/', data);
  return response.data;
};

export const changePassword = async (data) => {
  const response = await axiosClient.post('users/change-password/', data);
  return response.data;
};

export const getMyBookingsFlat = async () => {
  const response = await axiosClient.get('tours/my-bookings/');
  const bookings = response.data.bookings;
  return [
    ...bookings.upcoming,
    ...bookings.completed,
    ...bookings.cancelled,
    ...bookings.pending
  ];
};

// --- NGÀY 21: PROVIDER CREATOR API ---
export const getProviderTours = async () => {
  const response = await axiosClient.get('tours/provider/tours/');
  return response.data;
};

export const createProviderTour = async (data) => {
  const response = await axiosClient.post('tours/provider/tours/', data);
  return response.data;
};

// --- NGÀY 22: PROVIDER EDIT/DELETE & IMAGE MANAGEMENT ---
export const updateProviderTour = async (id, data) => {
  const response = await axiosClient.put(`tours/provider/tours/${id}/`, data);
  return response.data;
};

export const deleteProviderTour = async (id) => {
  const response = await axiosClient.delete(`tours/provider/tours/${id}/`);
  return response.data;
};

export const deleteTourImage = async (imageId) => {
  const response = await axiosClient.delete(`tours/provider/tours/images/${imageId}/`);
  return response.data;
};
