# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

def export_all_data_to_csv():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # .../backend/tours/

        backend_dir = os.path.dirname(current_dir)
        # .../backend/

        project_dir = os.path.dirname(backend_dir)
        # .../Test/

        script_path = os.path.join(project_dir, 'scripts', 'export_to_csv.py')
        # .../Test/scripts/export_to_csv.py

        print(f"[CSV] Script path: {script_path}")  # debug

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
            print("[CSV] Dong bo 6 file Analytics thanh cong!")
        else:
            print("[CSV] Pipeline gap loi!")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("[CSV] Script chay qua 30 giay!")
    except Exception as e:
        print(f"[CSV] Loi: {e}")

@receiver(post_save)
@receiver(post_delete)
def auto_pipeline_trigger(sender, instance, **kwargs):
    if os.environ.get('SKIP_SIGNALS') == 'yes':
        return

    model_name = sender.__name__
    TARGET_MODELS = ['User', 'Tour', 'Booking', 'Payment', 'Revenue', 'Review']

    if model_name in TARGET_MODELS:
        print(f"[Signal] Bang [{model_name}] thay doi -> Dang dong bo CSV...")
        transaction.on_commit(export_all_data_to_csv)