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
        backend_dir = os.path.dirname(current_dir)
        project_dir = os.path.dirname(backend_dir)

        # 1. Đường dẫn tới 2 file script của bạn
        csv_script = os.path.join(project_dir, 'scripts', 'export_to_csv.py')
        s3_script = os.path.join(project_dir, 'scripts', 'incremental_export.py')

        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        # --- BƯỚC 1: CHẠY EXPORT RA CSV LOCAL ---
        if os.path.exists(csv_script):
            print(f"[CSV] Đang chạy script xuất CSV: {csv_script}")
            csv_result = subprocess.run(
                [sys.executable, csv_script],
                capture_output=True,
                text=True,
                timeout=180,
                env=env
            )
            
            if csv_result.returncode == 0:
                print("[CSV] Đồng bộ 6 file Analytics thành công!")
                
                # --- BƯỚC 2: TỰ ĐỘNG KÍCH HOẠT S3 PIPELINE NGAY SAU ĐÓ ---
                if os.path.exists(s3_script):
                    print(f"[AWS S3] Phát hiện file CSV mới, đang kích hoạt Pipeline lên S3...")
                    # Chạy với tham số 'once' để đẩy dữ liệu lên S3 rồi thoát ngay lập tức
                    s3_result = subprocess.run(
                        [sys.executable, s3_script, 'once'],
                        capture_output=True,
                        text=True,
                        timeout=45,
                        env=env
                    )
                    
                    if s3_result.returncode == 0:
                        print("[AWS S3] Upload dữ liệu mới lên S3 Data Lake thành công!")
                    else:
                        print("[AWS S3] Pipeline S3 gặp lỗi!")
                        print(s3_result.stderr)
                else:
                    print(f"[AWS S3] Không tìm thấy file script S3: {s3_script}")
            else:
                print("[CSV] Pipeline CSV gặp lỗi, hủy lệnh đẩy lên S3!")
                print(csv_result.stderr)
        else:
            print(f"[CSV] Không tìm thấy file xuất CSV: {csv_script}")

    except subprocess.TimeoutExpired:
        print("[Signal Timeout] Script chạy quá thời gian quy định!")
    except Exception as e:
        print(f"[Signal Error] Lỗi hệ thống: {e}")

@receiver(post_save)
@receiver(post_delete)
def auto_pipeline_trigger(sender, instance, **kwargs):
    if os.environ.get('SKIP_SIGNALS') == 'yes':
        return

    model_name = sender.__name__
    TARGET_MODELS = ['User', 'Tour', 'Booking', 'Payment', 'Revenue', 'Review']

    if model_name in TARGET_MODELS:
        print(f"[Signal] Bảng [{model_name}] thay đổi -> Đang chuẩn bị kích hoạt chuỗi đồng bộ (CSV + S3)...")
        # Đợi database lưu thành công (commit) mới kích hoạt script chạy ngầm để tránh lỗi khóa DB
        transaction.on_commit(export_all_data_to_csv)