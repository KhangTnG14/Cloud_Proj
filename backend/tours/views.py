from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, permissions, status, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Sum
from .models import Tour, TourImage, Booking, Transaction, Payment, Revenue
from .serializers import BookingSerializer, TourSerializer, TourImageSerializer, BookingDetailSerializer, BookingListSerializer
from .permissions import IsAdminOrProvider, IsProvider
import logging
from rest_framework import permissions
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import date
logger = logging.getLogger('app_logger')
from django.conf import settings
from .email_service import send_ticket_email
from django.contrib.auth import get_user_model
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from rest_framework.permissions import IsAdminUser
User = get_user_model()
class ProviderTourView(generics.ListCreateAPIView):
    serializer_class = TourSerializer
    permission_classes = [IsProvider]

    def get_queryset(self):
        # [NGÀY 20 - KHÁNH]: Tối ưu N+1 query và lọc theo người tạo (Provider)
        return Tour.objects.filter(creator=self.request.user).select_related('creator').prefetch_related(
            'tour_images',
            'reviews',
            'reviews__user',
            'categories',
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,status='pending')

class ProviderTourDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TourSerializer
    permission_classes = [IsProvider]

    def get_queryset(self):
        # Provider xem được tất cả tour của mình (kể cả pending, rejected để họ còn sửa hoặc xem lý do)
        return Tour.objects.filter(creator=self.request.user).order_by('-id')

# CHỈ DÙNG MỘT CLASS NÀY CHO CẢ XEM DANH SÁCH VÀ TẠO TOUR
class TourCreateView(generics.ListCreateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrProvider()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        # [NGÀY 20 - KHÁNH]: Tối ưu N+1 query
        queryset = Tour.objects.select_related('creator').prefetch_related(
            'tour_images',
            'reviews',
            'reviews__user',
            'categories',
        ).all()
        
        query = self.request.query_params.get('search')
        min_p = self.request.query_params.get('min_price')
        max_p = self.request.query_params.get('max_price')
        d_date = self.request.query_params.get('departure_date')
        s_date = self.request.query_params.get('start_date')
        category_id = self.request.query_params.get('category')

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(address__icontains=query))
        if min_p:
            queryset = queryset.filter(price__gte=min_p)
        if max_p:
            queryset = queryset.filter(price__lte=max_p)
        if d_date:
            queryset = queryset.filter(departure_date=d_date)
        if s_date:
            queryset = queryset.filter(departure_date=s_date)
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
            
        return queryset.distinct()
    def perform_create(self, serializer):
        # Tự động gán người tạo cho tour mới
        serializer.save(creator=self.request.user, status='pending')

# GIỮ NGUYÊN API LỌC NÂNG CAO CỦA KHANG
class TourFilterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('search')
        min_p = request.query_params.get('min_price')
        max_p = request.query_params.get('max_price')
        d_date = request.query_params.get('departure_date')
        category_id = request.query_params.get('category')

        tours = Tour.objects.select_related('creator').prefetch_related(
            'tour_images',
            'reviews',
            'reviews__user',
            'categories',
        ).all()

        if query:
            tours = tours.filter(Q(title__icontains=query) | Q(address__icontains=query))
        
        if min_p: tours = tours.filter(price__gte=min_p)
        if max_p: tours = tours.filter(price__lte=max_p)
        if d_date: tours = tours.filter(departure_date=d_date)
        if category_id:
            tours = tours.filter(categories__id=category_id)

        serializer = TourSerializer(tours.distinct(), many=True, context={'request': request})
        return Response(serializer.data)

# GIỮ NGUYÊN CHI TIẾT VÀ BOOKING
class TourDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny] 
    
    def get(self, request, pk):
        try:
            # [NGÀY 20 - KHÁNH]: Tối ưu N+1 query
            tour = Tour.objects.select_related('creator').prefetch_related(
                'tour_images', 
                'reviews',
                'reviews__user'
            ).get(pk=pk)
            return Response(TourSerializer(tour, context={'request': request}).data)
        except Tour.DoesNotExist:
            return Response({"error": "Không tìm thấy!"}, status=404)
logger = logging.getLogger('app_logger')

@method_decorator(csrf_exempt, name='dispatch')
class BookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # 1. KIỂM TRA QUYỀN CHẶT CHẼ (Chốt chặn tối cao)
        # Lấy role và đưa về chữ in hoa để so sánh, mặc định là chuỗi rỗng nếu không có
        user_role = str(getattr(user, 'role', '')).upper()
        
        # Nếu là siêu quản trị (superuser) hoặc nhân viên (staff) hoặc role không phải CUSTOMER
        if user.is_superuser or user.is_staff or user_role != 'CUSTOMER':
            return Response(
                {"error": "Chỉ tài khoản Khách hàng (Customer) mới có quyền đặt tour! Quản trị viên và Nhà cung cấp không thể thực hiện hành động này."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        tour_id = request.data.get('tour')
        num_people = request.data.get('number_of_people')
        
        if not tour_id or not num_people:
            return Response(
                {"error": "Thiếu thông tin tour hoặc số lượng người!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2. Lấy thông tin tour từ Database để lấy giá gốc và kiểm tra slots
            tour = Tour.objects.get(id=tour_id)
            
            try:
                num_people = int(num_people)
            except (ValueError, TypeError):
                return Response({"error": "Số lượng người không hợp lệ!"}, status=400)

            # 3. Kiểm tra ngày khởi hành (Giữ nguyên logic của Tân)
            if tour.departure_date and tour.departure_date <= date.today():
                return Response(
                    {"error": f"Không thể đặt tour này. Ngày khởi hành ({tour.departure_date}) phải sau ngày hiện tại!"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 4. Kiểm tra số chỗ trống (Mỗi đơn hàng chỉ tính là 1 lượt đặt)
            if tour.slots <= 0:
                return Response({"error": "Tour này hiện đã hết lượt đặt!"}, status=status.HTTP_400_BAD_REQUEST)

            # --- 5. FIX LỖI TÍNH TIỀN & LƯU DỮ LIỆU ---
            # Tạo bản sao dữ liệu để chỉnh sửa
            data = request.data.copy()
            
            # ÉP GIÁ: Bất kể Frontend gửi gì, Backend chỉ lấy giá tour gốc để lưu vào total_price
            data['total_price'] = tour.price 

            # Truyền data đã ép giá vào Serializer
            serializer = BookingSerializer(data=data, context={'request': request})
            
            if serializer.is_valid():
                # Khi gọi save(), hàm create trong Serializer sẽ thực hiện trừ 1 slot
                booking = serializer.save() 

                logger.info(f"Đặt tour thành công: User {request.user} - Tour {tour.title}")
                return Response(
                    {"message": "Đặt tour thành công!", "id": booking.id}, 
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Tour.DoesNotExist:
            return Response({"error": "Không tìm thấy tour!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("Lỗi hệ thống khi đặt tour")
            return Response({"error": f"Lỗi hệ thống: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class TourImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, tour_id):
        try:
            tour = Tour.objects.get(id=tour_id)
            # Cho phép người tạo hoặc admin upload
            if tour.creator != request.user and not request.user.is_staff:
                return Response({"error": "Bạn không có quyền upload ảnh cho tour này"}, status=status.HTTP_403_FORBIDDEN)
            
            files = request.FILES.getlist('images')
            uploaded_images = []
            for f in files:
                img = TourImage.objects.create(tour=tour, image=f)
                uploaded_images.append(TourImageSerializer(img).data)
            
            return Response({
                "message": f"Đã upload thành công {len(uploaded_images)} ảnh.",
                "images": uploaded_images
            }, status=status.HTTP_201_CREATED)
        except Tour.DoesNotExist:
            return Response({"error": "Không tìm thấy tour!"}, status=status.HTTP_404_NOT_FOUND)

class TourImageDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cho phép người tạo (provider) hoặc admin xoá ảnh
        if self.request.user.is_staff:
            return TourImage.objects.all()
        return TourImage.objects.filter(tour__creator=self.request.user)

    def perform_destroy(self, instance):
        # Optional: delete file from storage if needed, but let's just delete the object
        instance.delete()


from rest_framework import generics, permissions
from .models import Booking
from .serializers import BookingSerializer

class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated] # Bắt buộc đăng nhập tại IUH

    def perform_create(self, serializer):
        serializer.save()


# ------ DAY 19 -------------
# PHẦN NAY UPDATE THÊM TỪ PHẦN NGÀY 13 CỦA TÂN & KHÁNH
class UserBookingListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/tours/my-bookings/
        Return all bookings của user, phân loại theo category:
        - upcoming: Sắp đi
        - completed: Đã đi
        - cancelled: Đã hủy
        - pending: Chờ thanh toán
        """
        bookings = Booking.objects.filter(user=request.user).select_related('tour')
        
        # Tính category cho từng booking
        from datetime import date
        today = date.today()
        
        bookings_data = []
        for booking in bookings:
            serializer = BookingListSerializer(booking)
            bookings_data.append(serializer.data)
        
        # Group by category
        result = {
            'upcoming': [],
            'completed': [],
            'cancelled': [],
            'pending': []
        }
        
        for booking_data in bookings_data:
            category = booking_data.get('category', 'pending')
            result[category].append(booking_data)
        
        return Response({
            'message': f'Tổng {len(bookings)} booking',
            'bookings': result
        }, status=status.HTTP_200_OK)

class BookingDetailView(APIView):
    """
    API xem chi tiết và Hủy đơn hàng
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk, user=request.user)
            serializer = BookingDetailSerializer(booking, context={'request': request})
            return Response(serializer.data)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng!"}, status=404)

    def patch(self, request, pk):
        """
        Logic Hủy đơn hàng: Chuyển trạng thái sang 'cancelled' và hoàn trả slots cho Tour
        """
        try:
            booking = Booking.objects.get(pk=pk, user=request.user)

            if booking.status == 'cancelled':
                return Response({"error": "Đơn hàng này đã được hủy trước đó rồi!"}, status=400)

            booking.status = 'cancelled'
            booking.save()

            tour = booking.tour
            tour.slots += 1
            tour.save()

            logger.info(f"Hủy đơn hàng thành công: User {request.user} - Booking ID {pk}")
            return Response({"message": "Hủy đơn hàng thành công!", "status": "cancelled"})

        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng để hủy!"}, status=404)
        


import datetime


class VietQRCreateView(APIView):
    """
    API Tạo mã VietQR - Ngày 15 (Khang)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng"}, status=404)

        # 1. Tạo Transaction mới (Trạng thái Pending)
        txn_ref = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(booking.id)
        Transaction.objects.create(
            booking=booking,
            vnp_txn_ref=txn_ref,
            amount=booking.total_price
        )

        # 2. Tạo link VietQR (Sử dụng VietQR.io)
        # Định dạng: https://img.vietqr.io/image/<BANK_ID>-<ACCOUNT_NO>-<TEMPLATE>.png?amount=<AMOUNT>&addInfo=<CONTENT>&accountName=<NAME>
        bank_id = settings.VIETQR_BANK_ID
        account_no = settings.VIETQR_ACCOUNT_NO
        account_name = settings.VIETQR_ACCOUNT_NAME
        amount = int(booking.total_price)
        content = f"TOURGO{booking.id}" # Nội dung chuyển khoản

        qr_url = f"https://img.vietqr.io/image/{bank_id}-{account_no}-qr_only.png?amount={amount}&addInfo={content}&accountName={account_name}"

        return Response({
            "qr_url": qr_url,
            "bank_id": bank_id,
            "account_no": account_no,
            "account_name": account_name,
            "amount": amount,
            "content": content
        }, status=200)


class BookingConfirmPaymentView(APIView):
    """
    Khách báo đã chuyển khoản VietQR — giữ booking ở pending, chờ Admin duyệt.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(id=pk, user=request.user)
            if booking.status == 'confirmed':
                return Response({"message": "Đơn hàng đã được xác nhận trước đó."}, status=200)
            if booking.status == 'cancelled':
                return Response({"error": "Đơn hàng đã bị hủy."}, status=400)

            txn_ref = f"VIETQR_{booking.id}"
            try:
                txn_ref = booking.transaction.vnp_txn_ref
            except Exception:
                pass

            payment = booking.payments.order_by('-created_at').first()
            if payment:
                payment.status = 'AWAITING_ADMIN'
                payment.payment_method = 'VietQR'
                payment.save()
            else:
                Payment.objects.create(
                    booking=booking,
                    amount=booking.total_price,
                    payment_method='VietQR',
                    status='AWAITING_ADMIN',
                    vnp_txn_ref=txn_ref,
                    transaction_code=txn_ref,
                )

            # Không đổi sang confirmed — Admin bấm "Duyệt thanh toán" mới xác nhận
            return Response({
                "message": "Đã ghi nhận chuyển khoản. Vui lòng chờ Admin xác nhận thanh toán.",
                "status": booking.status,
            }, status=200)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng"}, status=404)

class AdminBookingListView(APIView):
    """
    API Admin: Danh sách tất cả đơn hàng - Ngày 27 (Tân)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser or request.user.role == 'ADMIN'):
            return Response({"error": "Bạn không có quyền truy cập"}, status=403)
        
        search_query = request.query_params.get('search')
        bookings = Booking.objects.all().order_by('-created_at')
        
        if search_query:
            from django.db.models import Q
            try:
                booking_id = int(search_query)
                bookings = bookings.filter(id=booking_id)
            except ValueError:
                bookings = bookings.filter(
                    Q(user__username__icontains=search_query) |
                    Q(tour__title__icontains=search_query)
                )

        from .serializers import AdminBookingSerializer
        serializer = AdminBookingSerializer(bookings, many=True)
        return Response(serializer.data)


class AdminPaymentListView(APIView):
    """
    API Admin: Xem chi tiết các giao dịch tiền tệ (Payment logs) - Ngày 27 (Khánh)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser or request.user.role == 'ADMIN'):
            return Response({"error": "Bạn không có quyền truy cập"}, status=403)

        search_query = request.query_params.get('search')
        payments = Payment.objects.all().order_by('-created_at')
        
        if search_query:
            from django.db.models import Q
            try:
                booking_id = int(search_query)
                payments = payments.filter(Q(booking_id=booking_id) | Q(amount=booking_id))
            except ValueError:
                payments = payments.filter(
                    Q(booking__user__username__icontains=search_query) |
                    Q(booking__tour__title__icontains=search_query) |
                    Q(transaction_code__icontains=search_query) |
                    Q(vnp_txn_ref__icontains=search_query)
                )

        from .serializers import PaymentSerializer
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class AdminApproveBookingView(APIView):
    """
    API Admin: Duyệt thanh toán cho đơn hàng VietQR - Ngày 27 (Khang)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not (request.user.is_staff or request.user.is_superuser or request.user.role == 'ADMIN'):
            return Response({"error": "Bạn không có quyền thực hiện"}, status=403)
        
        try:
            booking = Booking.objects.get(id=pk)
            if booking.status == 'confirmed':
                return Response({"message": f"Đơn hàng #{pk} đã được xác nhận trước đó."}, status=200)

            booking.status = 'confirmed'
            booking.save()

            payment = booking.payments.order_by('-created_at').first()
            if payment:
                payment.status = 'SUCCESS'
                payment.save()
            else:
                payment, _ = Payment.objects.get_or_create(
                    booking=booking,
                    vnp_txn_ref=f"MANUAL_{booking.id}",
                    defaults={
                        'amount': booking.total_price,
                        'payment_method': 'VietQR_Manual',
                        'status': 'SUCCESS',
                        'transaction_code': f"MANUAL_{booking.id}",
                    },
                )
                if payment.status != 'SUCCESS':
                    payment.status = 'SUCCESS'
                    payment.save()

            send_ticket_email(booking)

            from users.logging_utils import log_system_action
            log_system_action(
                request,
                "Admin duyệt thanh toán",
                f"Booking #{booking.id} — {booking.user.username} — {booking.total_price} VNĐ",
            )
            
            # Đồng thời tạo Revenue nếu chưa có
            from .models import Revenue
            if not Revenue.objects.filter(payment=payment).exists():
                creator = booking.tour.creator
                total_amount = booking.total_price
                creator_share = total_amount * 90 / 100 # Ví dụ chia 90% cho Creator
                admin_share = total_amount * 10 / 100   # 10% cho Admin
                Revenue.objects.create(
                    payment=payment,
                    creator=creator,
                    total_amount=total_amount,
                    creator_share=creator_share,
                    admin_share=admin_share
                )
            
            return Response({"message": f"Đã duyệt đơn hàng {pk} thành công!"})
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng"}, status=404)



# backend/tours/views.py — thêm vào cuối file

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, booking_id):
    """
    API Polling: Kiểm tra trạng thái thanh toán theo thời gian thực.
    
    Frontend gọi API này mỗi 3-5 giây để cập nhật UI.
    
    GET /api/bookings/<booking_id>/payment-status/
    
    Response:
    {
        "booking_id": 42,
        "booking_code": "TG000042",
        "booking_status": "confirmed",
        "payment_status": "SUCCESS",
        "payment_method": "VNPay",
        "amount": 5000000,
        "amount_display": "5.000.000 VNĐ",
        "paid_at": "2025-01-16T10:30:00Z",
        "is_paid": true,
        "poll_again": false       ← Frontend dựa vào field này để biết có cần poll tiếp không
    }
    """
    try:
        # Lấy booking — chỉ cho phép xem booking của chính mình
        booking = Booking.objects.select_related('tour', 'user').get(
            id=booking_id,
            user=request.user
        )
    except Booking.DoesNotExist:
        return Response(
            {"error": "Không tìm thấy đơn hàng."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Lấy payment mới nhất liên quan đến booking
    payment = None
    payment_status_value = "PENDING"
    payment_method = None
    amount = None
    paid_at = None

    try:
        payment = booking.payments.order_by('-created_at').first()
        if payment:
            payment_status_value = getattr(payment, 'status', 'PENDING')
            payment_method = getattr(payment, 'payment_method', None)
            amount = getattr(payment, 'amount', None)
            paid_at = getattr(payment, 'updated_at', None) or getattr(payment, 'created_at', None)
    except Exception:
        pass

    # Map payment method sang tên hiển thị
    method_map = {
        'vnpay': 'VNPay',
        'momo': 'MoMo',
        'cash': 'Tiền mặt',
        'bank_transfer': 'Chuyển khoản',
        'credit_card': 'Thẻ tín dụng',
    }
    payment_method_display = method_map.get(
        (payment_method or '').lower(), payment_method or 'Online'
    )

    # Xác định trạng thái tổng thể
    is_paid = booking.status == 'confirmed' and payment_status_value in [
        'SUCCESS', 'success', 'COMPLETED', 'completed',
    ]

    terminal_statuses = [
        'SUCCESS', 'success', 'COMPLETED', 'completed',
        'FAILED', 'failed', 'CANCELLED', 'cancelled',
        'confirmed', 'paid', 'Đã thanh toán', 'cancelled',
    ]
    poll_again = (
        payment_status_value not in terminal_statuses
        and booking.status not in terminal_statuses
    )

    # Format số tiền
    def fmt_currency(val):
        try:
            return f"{int(val):,} VNĐ".replace(",", ".")
        except (ValueError, TypeError):
            return f"{val} VNĐ" if val else "N/A"

    return Response({
        "booking_id": booking.id,
        "booking_code": f"TG{booking.id:06d}",
        "booking_status": booking.status,
        "payment_status": payment_status_value,
        "payment_method": payment_method_display,
        "amount": amount,
        "amount_display": fmt_currency(amount or getattr(booking, 'total_price', None)),
        "tour_name": booking.tour.title,
        "paid_at": paid_at,
        "is_paid": is_paid,
        "poll_again": poll_again,
        "checked_at": timezone.now(),   # Timestamp để debug
    })

# --- PHẦN CỦA KHÁNH (NGÀY 18: ĐÁNH GIÁ TOUR) ---
from .models import Review
from .serializers import ReviewSerializer

class ReviewCreateView(APIView):
    """
    API Gửi đánh giá tour - Ngày 18 (Khánh)
    Điều kiện: Chỉ user đã đặt tour và được 'confirmed' mới được đánh giá.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, tour_id):
        user = request.user
        content = request.data.get('content')
        rating = request.data.get('rating', 5)

        if not content:
            return Response({"error": "Nội dung đánh giá không được để trống"}, status=400)

        # 1. Kiểm tra xem user đã đi tour này chưa (có booking confirmed)
        has_booked = Booking.objects.filter(
            user=user, 
            tour_id=tour_id, 
            status='confirmed'
        ).exists()

        if not has_booked:
            return Response(
                {"error": "Bạn chỉ có thể đánh giá những tour mà bạn đã đặt và thanh toán thành công!"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Tạo đánh giá
        try:
            tour = Tour.objects.get(id=tour_id)
            review = Review.objects.create(
                user=user,
                tour=tour,
                content=content,
                rating=rating
            )
            serializer = ReviewSerializer(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Tour.DoesNotExist:
            return Response({"error": "Không tìm thấy tour!"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# --- PHẦN CỦA TÂN (NGÀY 20: QUẢN LÝ ĐÁNH GIÁ CÁ NHÂN) ---
from rest_framework import generics
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated

class UserReviewListView(generics.ListAPIView):
    """
    GET /api/tours/reviews/me/
    Lấy danh sách các đánh giá do chính user đang đăng nhập viết.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Lọc ra đánh giá của user hiện tại, sắp xếp bài mới nhất lên đầu
        return Review.objects.filter(user=self.request.user).order_by('-created_at')

class UserReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH, DELETE /api/tours/reviews/me/<id>/
    Xem chi tiết, Sửa, Xóa một đánh giá cụ thể của chính user đó.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Bảo mật: Chỉ cho phép truy vấn và thao tác trên review do chính user này tạo
        return Review.objects.filter(user=self.request.user)



class ProviderCustomerListView(APIView):
    # Chỉ cho phép tài khoản đã đăng nhập và là Provider truy cập
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        provider = request.user
        
        # 1. Lấy tất cả các booking thành công của các tour thuộc về provider này
        # Giả định model Tour có trường 'provider' và Model Booking có trường 'status'
        bookings = Booking.objects.filter(
            tour__provider=provider,
            status='Paid' # Hoặc trạng thái đơn hàng thành công trong DB của nhóm
        ).select_related('user', 'tour')

        # 2. Gom dữ liệu khách hàng (tránh trùng lặp nếu 1 khách đặt nhiều tour)
        customers_dict = {}
        for b in bookings:
            customer = b.user
            if customer.id not in customers_dict:
                customers_dict[customer.id] = {
                    "id": customer.id,
                    "customer_name": customer.get_full_name() or customer.username,
                    "email": customer.email,
                    "phone": getattr(customer, 'phone_number', 'N/A'), # Tùy thuộc vào model User của nhóm
                    "booked_tours": []
                }
            
            # Thêm thông tin tour mà khách này đã đặt
            customers_dict[customer.id]["booked_tours"].append({
                "booking_id": b.id,
                "tour_title": b.tour.title,
                "quantity": b.quantity,
                "total_price": b.total_price
            })

        return Response(list(customers_dict.values()))
    

class UpdateTourStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, tour_id):
        try:
            # Chỉ cho phép sửa tour của chính mình
            tour = Tour.objects.get(id=tour_id, provider=request.user)
        except Tour.DoesNotExist:
            return Response({"error": "Không tìm thấy tour hoặc bạn không có quyền"}, status=404)

        # Lấy trạng thái mới từ frontend gửi lên (True/False)
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response({"error": "Thiếu dữ liệu is_active"}, status=400)

        tour.is_active = is_active
        tour.save()

        status_text = "Đang kinh doanh" if tour.is_active else "Tạm dừng"
        return Response({
            "message": f"Đã cập nhật trạng thái tour thành: {status_text}",
            "tour_id": tour.id,
            "is_active": tour.is_active
        })
        
class ProviderRevenueReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        provider = request.user
        current_year = datetime.datetime.now().year

        # 1. Thống kê Doanh thu theo 12 Tháng trong năm hiện tại
        # Sử dụng ExtractMonth để gom nhóm dữ liệu ngay trong Database
        monthly_data = (
            Booking.objects.filter(
                tour__provider=provider,
                status='Paid',
                created_at__year=current_year  # Giả định dùng trường created_at làm mốc thời gian
            )
            .annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(total_revenue=Sum('total_price'))
            .order_by('month')
        )

        # Tạo sẵn mảng dữ liệu 12 tháng mặc định bằng 0
        monthly_report = {m: 0 for m in range(1, 13)}
        for item in monthly_data:
            monthly_report[item['month']] = item['total_revenue']

        # Chuyển đổi định dạng thành mảng JSON mượt mà cho Frontend
        formatted_months = [
            {"month": f"Tháng {m}", "revenue": monthly_report[m]} for m in range(1, 13)
        ]

        # 2. Thống kê Doanh thu theo Quý (Q1, Q2, Q3, Q4)
        quarterly_report = {f"Quý {q}": 0 for q in range(1, 5)}
        for m in range(1, 13):
            quarter = (m - 1) // 3 + 1
            quarterly_report[f"Quý {quarter}"] += monthly_report[m]

        formatted_quarters = [
            {"quarter": q, "revenue": val} for q, val in quarterly_report.items()
        ]

        return Response({
            "year": current_year,
            "monthly": formatted_months,
            "quarterly": formatted_quarters
        })       
class ProviderRevenueView(APIView):
    """
    API Báo cáo doanh thu theo Tháng/Quý dành riêng cho Provider (Tối ưu SQL hóa)
    """
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        provider_id = request.user.id 
        report_type = request.query_params.get('type', 'month')
        year_param = request.query_params.get('year', date.today().year)
        
        try:
            year = int(year_param)
        except ValueError:
            return Response({"error": "Năm truyền vào không hợp lệ, phải là số nguyên."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Tạo câu Query cơ sở lọc đúng dữ liệu của Provider
        bookings_query = Booking.objects.filter(
            tour__creator_id=provider_id,
            status='confirmed',
            booking_date__year=year
        )

        result_data = []

        # 2. XỬ LÝ THEO THÁNG (Khánh tối ưu SQL)
        if report_type == 'month':
            # SQL bóc tách tháng và SUM tổng tiền luôn dưới DB
            monthly_data = bookings_query.annotate(
                month=ExtractMonth('booking_date')
            ).values('month').annotate(
                revenue=Sum('total_price'),
                bookings=Count('id')
            ).order_by('month')

            # Chuyển kết quả database thành dict để map dữ liệu nhanh
            revenue_map = {item['month']: (item['revenue'], item['bookings']) for item in monthly_data}
            
            for month in range(1, 13):
                rev, bks = revenue_map.get(month, (0.0, 0))
                result_data.append({
                    "label": f"Tháng {month:02d}",
                    "total_revenue": float(rev or 0.0), 
                    "total_bookings": bks
                })

        # 3. XỬ LÝ THEO QUÝ
        elif report_type == 'quarter':
            quarter_data = bookings_query.annotate(
                month=ExtractMonth('booking_date')
            ).values('month', 'total_price')

            quarter_map = {1: {"rev": 0.0, "bks": 0}, 2: {"rev": 0.0, "bks": 0}, 3: {"rev": 0.0, "bks": 0}, 4: {"rev": 0.0, "bks": 0}}
            
            for item in quarter_data:
                month = item['month']
                if month:
                    quarter = (month - 1) // 3 + 1
                    quarter_map[quarter]["rev"] += float(item['total_price'] or 0.0)
                    quarter_map[quarter]["bks"] += 1

            for q in range(1, 5):
                result_data.append({
                    "label": f"Quý {q}",
                    "total_revenue": quarter_map[q]["rev"],
                    "total_bookings": quarter_map[q]["bks"]
                })
        else:
            return Response({"error": "Tham số type phải là 'month' hoặc 'quarter'"}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Trả kết quả về cho Hà nhận data vẽ UI
        return Response({
            "year": year,
            "report_type": report_type,
            "data": result_data
        }, status=status.HTTP_200_OK)
class ApproveTourView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, tour_id):
        try:
            tour = Tour.objects.get(id=tour_id)
            action = request.data.get('action') # Nhận các giá trị 'approve', 'reject', hoặc 'pending' từ React
            
            reject_reason = request.data.get('reason', '')
            if action == 'approve':
                tour.status = 'approved'
                log_details = f"Duyệt tour #{tour.id}: {tour.title}"
            elif action == 'reject':
                tour.status = 'rejected'
                log_details = f"Từ chối tour #{tour.id}: {tour.title}"
                if reject_reason:
                    log_details += f" — Lý do: {reject_reason}"
            elif action == 'pending':
                tour.status = 'pending'
                log_details = f"Đưa tour #{tour.id} về chờ duyệt: {tour.title}"
            else:
                return Response({"error": "Hành động không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
                
            tour.save()
            from users.logging_utils import log_system_action
            log_system_action(request, f"Admin {action} tour", log_details)
            return Response({"message": f"Đã cập nhật trạng thái tour sang {tour.status}"}, status=status.HTTP_200_OK)
        except Tour.DoesNotExist:
            return Response({"error": "Không tìm thấy tour này"}, status=status.HTTP_404_NOT_FOUND)
class AdminTourListView(APIView):
    # Chỉ tài khoản có quyền Admin (is_staff=True) mới được phép gọi API này
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            # Lấy toàn bộ tour, sắp xếp theo thời gian tạo mới nhất lên đầu
            tours = Tour.objects.all().order_by('-created_at')
            serializer = TourSerializer(tours, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class TourDetailView(generics.RetrieveAPIView): 
    serializer_class = TourSerializer
    permission_classes = [] # Khách vãng lai cũng xem được

    def get_queryset(self):
        # FIX TẠI ĐÂY: Khách hàng chỉ được xem những tour ĐÃ DUYỆT
        return Tour.objects.filter(status='approved')

from rest_framework import viewsets
from .models import Category, Location
from .serializers import CategorySerializer, LocationSerializer

from users.logging_utils import log_system_action

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminUser()]

    def perform_create(self, serializer):
        loc = serializer.save()
        log_system_action(
            self.request,
            "Thêm mới Tỉnh/Thành",
            f"{loc.name} (lat={loc.lat}, lng={loc.lng})",
        )

    def perform_update(self, serializer):
        loc = serializer.save()
        log_system_action(
            self.request,
            "Cập nhật Tỉnh/Thành",
            f"{loc.name} (lat={loc.lat}, lng={loc.lng})",
        )

    def perform_destroy(self, instance):
        name = instance.name
        instance.delete()
        log_system_action(
            self.request,
            "Xóa Tỉnh/Thành",
            f"Đã xóa: {name}",
        )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminUser()]

    def perform_create(self, serializer):
        category = serializer.save()
        log_system_action(
            self.request,
            "Thêm mới Danh mục",
            f"Tên danh mục: {category.name}",
        )

    def perform_update(self, serializer):
        category = serializer.save()
        log_system_action(
            self.request,
            "Cập nhật Danh mục",
            f"Tên danh mục: {category.name}",
        )

    def perform_destroy(self, instance):
        category_name = instance.name
        instance.delete()
        log_system_action(
            self.request,
            "Xóa Danh mục",
            f"Tên danh mục đã xóa: {category_name}",
        )
