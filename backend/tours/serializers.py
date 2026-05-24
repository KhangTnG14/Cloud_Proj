from rest_framework import serializers
from .models import Booking, Tour, TourImage, Review, Payment, Category, Location
from datetime import date
from django.utils.text import slugify

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        if not validated_data.get('slug') and validated_data.get('name'):
            base_slug = slugify(validated_data['name']) or 'category'
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            validated_data['slug'] = slug
        return super().create(validated_data)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'lat', 'lng', 'created_at']
        read_only_fields = ['created_at']

class TourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ['id', 'image', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    tour_title = serializers.CharField(source='tour.title', read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'tour', 'tour_title','rating', 'content', 'created_at']
        read_only_fields = ['user', 'tour', 'created_at']

class TourSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='creator.username')
    creator_phone = serializers.ReadOnlyField(source='creator.phone')
    tour_images = TourImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    category_names = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = '__all__'
        read_only_fields = ['creator']
        extra_kwargs = {
            'status': {'read_only': True},
            'categories': {'required': False},
        }

    def get_category_names(self, obj):
        return list(obj.categories.values_list('name', flat=True))

from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        # Chặn mọi tác động từ Frontend vào các trường hệ thống tự tính
        read_only_fields = ['user', 'total_price', 'status', 'booking_date']

    def validate(self, data):
        tour = data.get('tour')
        num_people = data.get('number_of_people')
        
        # Lấy ngày từ dữ liệu thô gửi lên để kiểm tra
        input_date = self.initial_data.get('booking_date') 

        # 1. TÁCH LỖI NGÀY KHỞI HÀNH
        if input_date and str(input_date) != str(tour.departure_date):
            raise serializers.ValidationError({
                "date_error": f"Ngày khởi hành không hợp lệ! Tour này cố định ngày {tour.departure_date}."
            })

        # 2. TÁCH LỖI SỐ LƯỢNG NGƯỜI
        if num_people is not None:
            if num_people < 1 or num_people > 100:
                raise serializers.ValidationError({
                    "people_error": "Số lượng người đặt phải nằm trong khoảng từ 1 đến 100 người."
                })

        # 3. TÁCH LỖI HẾT LƯỢT ĐẶT (SLOTS)
        if tour and tour.slots <= 0:
            raise serializers.ValidationError({
                "slot_error": "Xin lỗi, tour này hiện đã hết lượt đặt!"
            })
            
        return data

    def create(self, validated_data):
        # Lấy thông tin từ context và tour
        user = self.context['request'].user
        tour = validated_data['tour']
        
        # NGHIỆP VỤ 1: Trừ slot trực tiếp vào model Tour
        tour.slots -= 1 
        tour.save()

        # NGHIỆP VỤ 2: Ép dữ liệu hệ thống (Backend làm chủ)
        validated_data['user'] = user
        validated_data['total_price'] = tour.price
        validated_data['booking_date'] = tour.departure_date

        # NGHIỆP VỤ 3: Lưu vào DB và RETURN BOOKING (Quan trọng)
        # Sử dụng super().create để Django xử lý việc lưu và trả về instance vừa tạo
        booking = super().create(validated_data)
        
        return booking
    
# ---------- DAY 19 -----------
class BookingListSerializer(serializers.ModelSerializer):
    tour_title = serializers.CharField(source='tour.title', read_only=True)
    tour_address = serializers.CharField(source='tour.address', read_only=True)
    tour_image = serializers.URLField(source='tour.image_url', read_only=True)
    tour_departure_date = serializers.DateField(source='tour.departure_date', read_only=True)
    tour_price = serializers.DecimalField(
        source='tour.price',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    status_display = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id', 'tour_id', 'tour_title', 'tour_address', 'tour_image',
            'tour_departure_date', 'number_of_people', 'total_price',
            'tour_price', 'status', 'status_display', 'category', 'booking_date', 'created_at'
        )

    def get_status_display(self, obj):
        if obj.status == 'pending' and obj.payments.filter(status='AWAITING_ADMIN').exists():
            return 'Chờ Admin xác nhận TT'
        status_map = {
            'pending': 'Chờ thanh toán',
            'confirmed': 'Đã xác nhận',
            'cancelled': 'Đã hủy',
        }
        return status_map.get(obj.status, obj.status)

    def get_category(self, obj):
        from datetime import date
        today = date.today()

        if obj.status == 'cancelled':
            return 'cancelled'
        elif obj.tour.departure_date and obj.tour.departure_date > today and obj.status == 'confirmed':
            return 'upcoming'
        elif obj.tour.departure_date and obj.tour.departure_date <= today and obj.status == 'confirmed':
            return 'completed'
        return 'pending'

# --- THÊM SERIALIZER CHO NGÀY 13 (TÂN) ---
class BookingDetailSerializer(serializers.ModelSerializer):
    tour_details = TourSerializer(source='tour', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'total_price', 'status']


class PaymentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='booking.user.username')
    tour_title = serializers.ReadOnlyField(source='booking.tour.title')
    booking_id = serializers.ReadOnlyField(source='booking.id')

    class Meta:
        model = Payment
        fields = [
            'id', 'booking_id', 'username', 'tour_title', 'amount', 
            'payment_method', 'status', 'transaction_code', 'vnp_txn_ref', 'created_at'
        ]


class AdminBookingSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_email = serializers.ReadOnlyField(source='user.email')
    user_phone = serializers.ReadOnlyField(source='user.phone')
    tour_title = serializers.ReadOnlyField(source='tour.title')
    payment_awaiting = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'username', 'user_email', 'user_phone',
            'tour', 'tour_title', 'number_of_people', 'total_price',
            'booking_date', 'status', 'payment_awaiting', 'created_at',
        ]

    def get_payment_awaiting(self, obj):
        return obj.payments.filter(status='AWAITING_ADMIN').exists()

