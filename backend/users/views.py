from rest_framework import status, generics
from rest_framework.response import Response
from .serializers import RegisterSerializer, UpdateProfileSerializer, UserSerializer, ForgotPasswordSerializer, VerifyOTPSerializer, ResetPasswordSerializer, ChangePasswordSerializer
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PasswordResetOTP, User
from django.core.mail import send_mail
import logging
import random
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from datetime import date
logger = logging.getLogger('app_logger')
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from tours.models import Tour, Booking, Payment
import cloudinary.uploader 

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Đăng ký thành công!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class  nView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)

            user_role = "admin" if (user.is_superuser or user.is_staff) else user.role
            
            # Fix lỗi tiếng Việt ghi log không dấu trên Windows (Tránh lỗi charmap crash)
            logger.info(f"Người dùng {username} đã đăng nhập thành công với tư cách: {user_role}")
            from .logging_utils import log_system_action
            log_system_action(
                request,
                "Đăng nhập",
                f"Tài khoản: {username} — Vai trò: {user_role}",
                user=user,
            )
            
            return Response({
                "message": "Đăng nhập thành công!",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "username": user.username,
                "role": user_role  # Trả về giá trị đã qua xử lý phân quyền
            }, status=status.HTTP_200_OK)
            
        logger.warning(f"Thu dang nhap that bai cho tai khoan: {username}")
        return Response({"error": "Sai tài khoản hoặc mật khẩu"}, status=status.HTTP_400_BAD_REQUEST)
class ForgotPasswordView(APIView):
    """
    API yêu cầu gửi mã OTP qua Email để quên mật khẩu
    """
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Kiểm tra user tồn tại
            if not User.objects.filter(email=email).exists():
                return Response({"error": "Không tìm thấy người dùng với email này"}, status=status.HTTP_404_NOT_FOUND)
            
            # Tạo mã OTP 6 chữ số
            otp_code = str(random.randint(100000, 999999))
            
            # Xóa mã OTP cũ (nếu có) và tạo mã mới để reset thời gian 5 phút
            PasswordResetOTP.objects.filter(email=email).delete()
            PasswordResetOTP.objects.create(email=email, otp=otp_code)

            # Gửi Email
            subject = 'Mã OTP đặt lại mật khẩu của bạn'
            message = f'Mã OTP của bạn là: {otp_code}. Mã này có hiệu lực trong 5 phút.'
            email_from = None # Sẽ lấy từ settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            try:
                send_mail(subject, message, email_from, recipient_list)
                return Response({"message": "Mã OTP đã được gửi về email của bạn!"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"Lỗi gửi mail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    """
    API xác thực mã OTP gửi qua Email
    """
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            try:
                otp_obj = PasswordResetOTP.objects.filter(email=email, otp=otp).latest('created_at')
                
                if otp_obj.is_expired():
                    return Response({"error": "Mã OTP đã hết hạn"}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({"message": "Mã OTP chính xác!"}, status=status.HTTP_200_OK)
            except PasswordResetOTP.DoesNotExist:
                return Response({"error": "Mã OTP không đúng"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    API đặt lại mật khẩu mới sau khi đã xác thực OTP
    """
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']

            try:
                # Kiểm tra lại OTP lần nữa cho chắc chắn
                otp_obj = PasswordResetOTP.objects.filter(email=email, otp=otp).latest('created_at')
                
                if otp_obj.is_expired():
                    return Response({"error": "Mã OTP đã hết hạn"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Cập nhật mật khẩu
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Xóa OTP sau khi dùng xong
                PasswordResetOTP.objects.filter(email=email).delete()
                
                return Response({"message": "Đặt lại mật khẩu thành công!"}, status=status.HTTP_200_OK)
                
            except PasswordResetOTP.DoesNotExist:
                return Response({"error": "Xác thực không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        """
        Cập nhật profile user (phone, avatar)
        """
        serializer = UpdateProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True  # Allow partial update
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Cập nhật profile thành công!",
                "user": UserSerializer(request.user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """
        Lấy thông tin profile hiện tại
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": "Mật khẩu cũ không chính xác."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Đổi mật khẩu thành công!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-id')
        user_list = []
        
        for u in users:
            # --- 1. XÁC ĐỊNH ROLE CHUẨN ---
            # Model có choices: ADMIN, PROVIDER, CUSTOMER
            if u.is_superuser or u.is_staff:
                role = 'admin'
            elif u.role == User.PROVIDER: # Kiểm tra hằng số PROVIDER trong model
                role = 'provider'
            else:
                role = 'user' # Mặc định là khách hàng (CUSTOMER)
                
            # --- 2. XÁC ĐỊNH STATUS ---
            if u.is_superuser or u.is_staff:
                status = 'Active' 
            elif hasattr(u, 'is_approved') and not u.is_approved: 
                # Lưu ý: Chỉ kiểm tra nếu model của bạn thực sự có trường is_approved
                status = 'Pending'
            elif u.is_active:
                status = 'Active'
            else:
                status = 'Banned'

            user_list.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': role, 
                'status': status,
                'is_superuser': u.is_superuser,
                'is_staff': u.is_staff
            })
            
        return Response(user_list)
class AdminSystemStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_tours = Tour.objects.count()
        
        # Doanh thu sàn = tổng giao dịch thanh toán thành công (khớp tab Nhật ký Giao dịch)
        total_revenue = Payment.objects.filter(
            status__in=['SUCCESS', 'success', 'COMPLETED', 'completed']
        ).aggregate(total=Sum('amount'))['total']

        if not total_revenue:
            # Fallback: đơn đã xác nhận (trước khi có bản ghi Payment)
            total_revenue = Booking.objects.filter(
                status='confirmed'
            ).aggregate(total=Sum('total_price'))['total'] or 0
        else:
            total_revenue = total_revenue or 0

        return Response({
            "success": True,
            "data": {
                "total_users": total_users,
                "total_tours": total_tours,
                "total_revenue": float(total_revenue)
            }
        }, status=status.HTTP_200_OK)
class ToggleUserStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            
            # Không cho phép tự khóa chính mình hoặc khóa các Admin khác
            if user.is_superuser or user.is_staff:
                return Response({'error': 'Không thể thay đổi trạng thái của tài khoản Quản trị!'}, status=400)
            
            # Logic xử lý xoay vòng trạng thái
            if getattr(user, 'is_approved', True) == False:
                user.is_approved = True
                user.is_active = True
            else:
                user.is_active = not user.is_active
                
            user.save()
            
            from .logging_utils import log_system_action
            log_system_action(
                request,
                f"Thay đổi trạng thái tài khoản {user.username}",
                f"Trạng thái mới: {'Kích hoạt' if user.is_active else 'Khóa'}",
            )

            return Response({'message': 'Cập nhật trạng thái thành công'})
        except User.DoesNotExist:
            return Response({'error': 'Người dùng không tồn tại'}, status=404)

from .models import SystemLog
from .serializers import SystemLogSerializer

class AdminSystemLogListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        logs = SystemLog.objects.all().order_by('-created_at')[:100]  # Get last 100 logs
        serializer = SystemLogSerializer(logs, many=True)
        return Response(serializer.data)
class UserRoleView(APIView):
    """
    API xác định vai trò thực sự của user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = 'user' # Mặc định
        
        if user.is_superuser or user.is_staff:
            role = 'admin'
        elif hasattr(user, 'role') and user.role:
            role = user.role.lower()
            
        return Response({
            "username": user.username,
            "role": role,
            "is_admin": user.is_superuser or user.is_staff
        })



# backend/users/views.py — THÊM VÀO CUỐI



# UPDATE DAY 19: Thêm API upload ảnh đại diện lên Cloudinary
class UploadAvatarView(APIView):
    """
    POST /api/users/upload-avatar/
    Nhận file ảnh từ thiết bị → upload lên Cloudinary → trả về URL → lưu vào user.avatar
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Hỗ trợ nhận file

    def post(self, request):
        # 1. Kiểm tra có file không
        file = request.FILES.get("avatar")
        if not file:
            return Response(
                {"detail": "Vui lòng chọn file ảnh."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Kiểm tra định dạng file
        ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        if file.content_type not in ALLOWED_TYPES:
            return Response(
                {"detail": "Chỉ chấp nhận file JPG, PNG, WEBP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Kiểm tra dung lượng (tối đa 2MB)
        MAX_SIZE = 2 * 1024 * 1024  # 2MB
        if file.size > MAX_SIZE:
            return Response(
                {"detail": "File quá lớn. Tối đa 2MB."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 4. Upload lên Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                folder="tourgo/avatars",          # Lưu vào folder riêng
                public_id=f"user_{request.user.id}",  # Tên file theo user ID
                overwrite=True,                    # Ghi đè nếu đã có
                transformation=[
                    {"width": 300, "height": 300,
                     "crop": "fill", "gravity": "face"}  # Crop vuông, focus mặt
                ]
            )

            # 5. Lấy URL từ kết quả upload
            avatar_url = upload_result.get("secure_url")

            # 6. Lưu URL vào database
            request.user.avatar = avatar_url
            request.user.save(update_fields=["avatar"])

            return Response({
                "message": "Upload ảnh đại diện thành công!",
                "avatar_url": avatar_url,
                "user": UserSerializer(request.user).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Upload thất bại: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )