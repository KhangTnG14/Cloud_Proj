# backend/tours/email_service.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def format_currency(amount):
    """Format số tiền sang dạng VND dễ đọc."""
    try:
        return f"{int(amount):,} VNĐ".replace(",", ".")
    except (ValueError, TypeError):
        return f"{amount} VNĐ"


def send_ticket_email(booking):
    """
    Gửi email vé điện tử cho khách khi thanh toán thành công.
    
    Args:
        booking: instance của model Booking
    """
    try:
        customer = booking.user
        tour = booking.tour

        # Lấy email khách hàng
        customer_email = customer.email
        if not customer_email:
            logger.warning(f"[Email] Booking {booking.id}: khách hàng không có email.")
            return False

        # Tên hiển thị
        customer_name = (
            f"{customer.first_name} {customer.last_name}".strip()
            or customer.username
        )

        # Chuẩn bị context cho template
        context = {
            "customer_name": customer_name,
            "booking_code": f"TG{booking.id:06d}",  # ví dụ: TG000042
            "tour_name": tour.title,
            "departure_date": (
                booking.booking_date.strftime("%d/%m/%Y")
                if hasattr(booking, 'booking_date') and booking.booking_date
                else tour.departure_date.strftime("%d/%m/%Y") if hasattr(tour, 'departure_date') else "N/A"
            ),
            "duration": getattr(tour, 'duration', 'N/A'),
            "departure_location": getattr(tour, 'departure_location', 'N/A'),
            "num_people": getattr(booking, 'num_people', 1),
            "guide_name": getattr(tour, 'guide_name', 'Sẽ thông báo sau'),
            "payment_method": _get_payment_method_display(booking),
            "total_price": format_currency(booking.total_price),
            "frontend_url": getattr(settings, 'FRONTEND_URL', 'http://localhost:5173'),
        }

        # Render HTML từ template
        html_content = render_to_string('tours/ticket_email.html', context)

        # Nội dung text thuần (fallback)
        text_content = (
            f"Xin chào {customer_name},\n\n"
            f"Đặt tour thành công!\n"
            f"Mã đặt tour: TG{booking.id:06d}\n"
            f"Tour: {tour.title}\n"
            f"Tổng tiền: {format_currency(booking.total_price)}\n\n"
            f"Cảm ơn bạn đã sử dụng dịch vụ TourGo!"
        )

        # Tạo và gửi email
        subject = f"[TourGo] Vé điện tử - {tour.title} | Mã: TG{booking.id:06d}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"[Email] Gửi vé thành công → {customer_email} | Booking #{booking.id}")
        return True

    except Exception as e:
        logger.error(f"[Email] Lỗi gửi email booking #{booking.id}: {str(e)}")
        return False


def _get_payment_method_display(booking):
    """Lấy tên phương thức thanh toán dễ đọc."""
    method_map = {
        'vnpay': 'VNPay',
        'momo': 'MoMo',
        'cash': 'Tiền mặt',
        'bank_transfer': 'Chuyển khoản ngân hàng',
        'credit_card': 'Thẻ tín dụng',
    }
    # Lấy từ Payment model liên quan
    try:
        payment = booking.payments.filter(status='SUCCESS').last()
        if payment:
            method = getattr(payment, 'payment_method', None)
            if method:
                return method_map.get(method.lower(), method)
    except Exception:
        pass
    return 'Online'