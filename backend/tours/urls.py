from django.urls import path
from .views import (
    ProviderCustomerListView, ProviderRevenueReportView, TourCreateView, TourDetailAPIView, TourFilterView, 
    TourImageUploadView, BookingView, UpdateTourStatusView,
    UserBookingListView, BookingDetailView,
    VietQRCreateView,
    BookingConfirmPaymentView, AdminBookingListView, AdminApproveBookingView, AdminPaymentListView,
    payment_status, ReviewCreateView, UserReviewListView, UserReviewDetailView,
    ProviderTourView, ProviderTourDetailView, TourImageDeleteView,ProviderRevenueView,ApproveTourView,AdminTourListView, TourDetailView,
    CategoryViewSet, LocationViewSet
)

urlpatterns = [
    # Danh sách / tạo tour — phải đứng trước categories để GET /api/tours/ trả mảng tour
    path('', TourCreateView.as_view(), name='tour-create'),
    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='category-detail'),
    path('locations/', LocationViewSet.as_view({'get': 'list', 'post': 'create'}), name='location-list'),
    path('locations/<int:pk>/', LocationViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='location-detail'),
    # 0. API dành cho Nhà cung cấp (Provider) - Ngày 21 & 22
    path('provider/tours/', ProviderTourView.as_view(), name='provider-tour-list-create'),
    path('provider/tours/<int:pk>/', ProviderTourDetailView.as_view(), name='provider-tour-detail'),
    path('provider/tours/images/<int:pk>/', TourImageDeleteView.as_view(), name='provider-tour-image-delete'),

    # 3. API Đánh giá - Ngày 18 (Tân)
    path('<int:tour_id>/reviews/', ReviewCreateView.as_view(), name='tour-reviews'),

    # 1. Các API liên quan đến Booking (Đặt tour & Thanh toán)
    path('book/', BookingView.as_view(), name='tour-book'),
    path('my-bookings/', UserBookingListView.as_view(), name='user-bookings'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    
    # --- THÊM ROUTE THANH TOÁN ---
    path('create-vietqr/', VietQRCreateView.as_view(), name='vietqr-create'),
    
    # --- MỚI: XÁC NHẬN & ADMIN DUYỆT ---
    path('bookings/<int:pk>/confirm-payment/', BookingConfirmPaymentView.as_view(), name='booking-confirm-payment'),
    path('admin/bookings/', AdminBookingListView.as_view(), name='admin-bookings'),
    path('admin/bookings/<int:pk>/approve/', AdminApproveBookingView.as_view(), name='admin-approve'),
    path('admin/payments/', AdminPaymentListView.as_view(), name='admin-payments'),


    # 2. Các API liên quan đến Tour
    path('filter/', TourFilterView.as_view(), name='tour-filter'),
    path('<int:pk>/', TourDetailAPIView.as_view(), name='tour-detail'),
    path('<int:tour_id>/upload-images/', TourImageUploadView.as_view(), name='tour-upload-images'),
    path('bookings/<int:booking_id>/payment-status/', payment_status, name='payment-status'),
    path('reviews/me/', UserReviewListView.as_view(), name='my-reviews'),
    path('reviews/me/<int:pk>/', UserReviewDetailView.as_view(), name='my-review-detail'),

    path('provider/customers/', ProviderCustomerListView.as_view(), name='provider-customers'),
    path('provider/tours/<int:tour_id>/update-status/', UpdateTourStatusView.as_view(), name='update-tour-status'),
    path('provider/revenue-report/', ProviderRevenueReportView.as_view(), name='provider-revenue-report'),
    path('provider/analytics/revenue/', ProviderRevenueView.as_view(), name='provider-revenue'),
    path('admin/tours/<int:tour_id>/approve/', ApproveTourView.as_view(), name='approve-tour'),
    path('admin/tours/', AdminTourListView.as_view(), name='admin-tour-list'),
    path('tours/<int:pk>/', TourDetailView.as_view(), name='public-tour-detail'),
]