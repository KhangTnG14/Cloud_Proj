from django.apps import AppConfig
import os
import sys
import subprocess

class ToursConfig(AppConfig):
    name = 'tours'

    def ready(self):
        import tours.signals

        if os.environ.get('RUN_MAIN') == 'true':
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(current_dir)
                script_path = os.path.join(backend_dir, 'export_to_csv.py')

                if os.path.exists(script_path):
                    subprocess.run(
                        [sys.executable, script_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    print("[CSV] Du lieu da duoc cap nhat khi khoi dong server!")
                else:
                    print(f"[CSV] Khong tim thay file: {script_path}")
            except Exception as e:
                print(f"[CSV] Loi khi export: {e}")