from rest_framework import serializers
from .models import User, SystemLog
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(
        error_messages={
            'unique': 'Tên đăng nhập này đã tồn tại. Vui lòng chọn tên khác.'
        }
    )
    phone = serializers.CharField(
        required=False, allow_blank=True, allow_null=True,
        error_messages={
            'unique': 'Số điện thoại này đã được đăng ký. Vui lòng dùng số khác.'
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'phone', 'role')

    def validate_password(self, value):
        # Validate mật khẩu yếu (ít nhất 8 ký tự, có 1 chữ cái và 1 số)
        if len(value) < 8:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Mật khẩu phải bao gồm cả chữ và số.")
        return value

    def validate_username(self, value):
        # Kiểm tra tên đăng nhập đã tồn tại chưa
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Tên đăng nhập này đã được đăng ký. Vui lòng chọn tên khác.")
        return value

    def validate_email(self, value):
        # Kiểm tra email đã tồn tại trong hệ thống chưa
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được đăng ký. Vui lòng dùng email khác.")
        return value

    def validate_phone(self, value):
        # Kiểm tra số điện thoại đã tồn tại trong hệ thống chưa
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Số điện thoại này đã được đăng ký. Vui lòng dùng số khác.")
        return value

    def create(self, validated_data):
        # Mã hóa mật khẩu trước khi lưu
        user = User.objects.create_user(**validated_data)
        return user

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

#XAT THUC OTP
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'avatar', 'role', 'is_staff')

class UpdateProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        required=False, allow_blank=True,
        error_messages={
            'unique': 'Số điện thoại này đã được đăng ký. Vui lòng dùng số khác.'
        }
    )
    avatar = serializers.URLField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('phone', 'avatar', 'email')  # email read-only cho xem thôi
        read_only_fields = ['email']
    
    def validate_phone(self, value):
        if value:  # Chỉ validate nếu có giá trị
            user = self.instance
            if User.objects.filter(phone=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("Số điện thoại này đã được đăng ký!")
        return value
    
    def update(self, instance, validated_data):
        instance.phone = validated_data.get('phone', instance.phone)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Mật khẩu mới và xác nhận không khớp.'
            })
        return data

class SystemLogSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = SystemLog
        fields = ['id', 'user', 'username', 'email', 'action', 'details', 'ip_address', 'created_at']