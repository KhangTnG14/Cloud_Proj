import os
import sys
import subprocess
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

def export_all_data_to_csv():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        script_path = os.path.join(backend_dir, 'export_to_csv.py')

        if not os.path.exists(script_path):
            print(f"[CSV] Khong tim thay file: {script_path}")
            return

        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        # Sử dụng đúng logic run kiểm tra tiến trình đồng bộ nguyên bản của bạn
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode == 0:
            print("[CSV] Kich hoat dong bo 6 file Analytics thanh cong!")
        else:
            print("[CSV] Pipeline gap loi khi chay qua n nhat!")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("[CSV] Script chay qua 30 giay!")
    except Exception as e:
        print(f"[CSV] Loi: {e}")

@receiver(post_save)
@receiver(post_delete)
def auto_pipeline_trigger(sender, instance, **kwargs):
    model_name = sender.__name__
    
    # 🔥 KHỚP 100% THEO LEADER SCHEMA: Theo dõi toàn bộ biến động của cả 6 phân hệ dữ liệu Analytics
    TARGET_MODELS = ['User', 'Tour', 'Booking', 'Payment', 'Revenue', 'Review']

    if model_name in TARGET_MODELS:
        print(f"[Signal] Phat hien bang Analytics [{model_name}] co thay doi -> Dang dong bo...")
        transaction.on_commit(export_all_data_to_csv)