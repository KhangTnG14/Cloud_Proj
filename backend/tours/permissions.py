from rest_framework import permissions

class IsAdminOrProvider(permissions.BasePermission):
    def has_permission(self, request, view):
        # Nếu là phương thức đọc dữ liệu (GET) thì cho qua (nhưng thực tế get_permissions đã xử lý rồi)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # CHỐT CHẶN: Chỉ cho phép nếu user là Staff (is_staff=True) hoặc Superuser
        # hansusan0410 tạo được tour là vì tài khoản này đang bị tích ô "Staff status" trong Admin.
        return bool(request.user and request.user.is_staff)

class IsProvider(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'PROVIDER' or request.user.role == 'ADMIN')
        )