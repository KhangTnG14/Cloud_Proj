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

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode == 0:
            print("[CSV] Export thanh cong!")
        else:
            print("[CSV] Export that bai!")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("[CSV] Script chay qua 30 giay!")
    except Exception as e:
        print(f"[CSV] Loi: {e}")

@receiver(post_save)
@receiver(post_delete)
def auto_pipeline_trigger(sender, instance, **kwargs):
    model_name = sender.__name__
    
    # 🔥 ĐÃ THÊM: Chỉ thêm duy nhất 'Revenue' vào cuối mảng, giữ nguyên toàn bộ logic cũ
    TARGET_MODELS = ['User', 'Tour', 'Booking', 'Payment', 'Review', 'Revenue']

    if model_name in TARGET_MODELS:
        print(f"[Signal] Bang [{model_name}] thay doi -> Dang cap nhat CSV...")
        transaction.on_commit(export_all_data_to_csv)