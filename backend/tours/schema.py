from pydantic import BaseModel
from typing import List

class RevenueData(BaseModel):
    label: str            # Ví dụ: "Tháng 01", "Quý 1"
    total_revenue: float  # Tổng tiền doanh thu
    total_bookings: int   # Số lượng đơn hàng thành công

class RevenueResponse(BaseModel):
    year: int
    report_type: str      # "month" hoặc "quarter"
    data: List[RevenueData]