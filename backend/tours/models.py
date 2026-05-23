from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên danh mục")
    description = models.TextField(verbose_name="Mô tả", null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Các danh mục"


class Location(models.Model):
    """Tỉnh / thành phố — dùng cho bản đồ và lọc điểm đến (Day 28)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên tỉnh/thành")
    lat = models.FloatField(verbose_name="Vĩ độ")
    lng = models.FloatField(verbose_name="Kinh độ")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tỉnh/Thành"
        verbose_name_plural = "Các tỉnh/thành"
        ordering = ['name']


# --- PHẦN CỦA TÂN VÀ KHANG (QUẢN LÝ TOUR) ---
class Tour(models.Model):
    categories = models.ManyToManyField(Category, blank=True, related_name="tours", verbose_name="Danh mục")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name="Người tạo"
    )
    address = models.CharField(max_length=255, default="Việt Nam")
    title = models.CharField(max_length=255, verbose_name="Tên Tour")
    description = models.TextField(verbose_name="Mô tả")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá")
    
    # TRƯỜNG QUAN TRỌNG ĐỂ LÀM LOGIC LỌC (Khang thêm dòng này)
    departure_date = models.DateField(verbose_name="Ngày khởi hành", null=True, blank=True)
    
    slots = models.IntegerField(verbose_name="Số chỗ")
    image_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="Link ảnh") # Để Hà hiển thị UI cho đẹp

    latitude = models.FloatField(verbose_name="Vĩ độ (Lat)", null=True, blank=True)
    longitude = models.FloatField(verbose_name="Kinh độ (Lng)", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Chờ duyệt'), ('approved', 'Đã duyệt'), ('rejected', 'Từ chối')],
        default='pending' # <--- Đây là chìa khóa: mọi tour mới tạo mặc định sẽ là 'pending'
    )
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Chuyến du lịch"
        verbose_name_plural = "Các chuyến du lịch"

class TourImage(models.Model):
    tour = models.ForeignKey(Tour, related_name='tour_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tour_images/', verbose_name="Ảnh")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.tour.title}"


# --- PHẦN CỦA Hà (MODEL BOOKING) 
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
    ]

    # ForeignKey kết nối User và Tour
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    
    number_of_people = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    booking_date = models.DateField() # Ngày khách chọn đi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tour.title}"
    
    class Meta:
        verbose_name = "Đơn đặt tour"
        verbose_name_plural = "Các đơn đặt tour"
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

# --- PHẦN CỦA TÂN VÀ KHANG (NGÀY 14 & 15: THANH TOÁN VNPAY) ---

class Transaction(models.Model):
    """
    Lưu vết từng lần bấm 'Thanh toán' của khách hàng
    """
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='transaction')
    vnp_txn_ref = models.CharField(max_length=100, unique=True) # Mã tham chiếu gửi sang VNPay
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_info = models.TextField()
    
    # Kết quả trả về từ VNPay
    vnp_response_code = models.CharField(max_length=10, null=True, blank=True)
    vnp_transaction_no = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Txn {self.vnp_txn_ref} - Booking {self.booking.id}"

class Payment(models.Model):
    """
    Lưu thông tin khi thanh toán thành công
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, default="VNPay")
    status = models.CharField(max_length=20, default="PENDING") # PENDING, SUCCESS, FAILED
    transaction_code = models.CharField(max_length=255, null=True, blank=True) # Mã từ VNPay
    vnp_txn_ref = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id}"

class Revenue(models.Model):
    """
    Quản lý doanh thu sàn và hoa hồng của nhà cung cấp (Day 24)
    """
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='revenue')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    creator_share = models.DecimalField(max_digits=12, decimal_places=2) # Tiền nhà cung cấp nhận
    admin_share = models.DecimalField(max_digits=12, decimal_places=2)   # Phí sàn (ví dụ 10%)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Revenue from Payment {self.payment.id}"

class Review(models.Model):
    """
    Model Đánh giá tour - Ngày 18 (Tân)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5) # 1-5 sao
    content = models.TextField(verbose_name="Nội dung đánh giá")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tour.title} - {self.rating} sao"

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Các đánh giá"
        ordering = ['-created_at']


