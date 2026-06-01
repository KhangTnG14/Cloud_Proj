import os
import glob

exported_dir = r'C:\Test\backend\exported_data'

for csv_file in glob.glob(os.path.join(exported_dir, '*.csv')):
    # Đọc với utf-8-sig (bỏ BOM)
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Ghi lại với utf-8 thuần
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    
    print(f"[OK] Converted: {os.path.basename(csv_file)}")

print("Xong!")