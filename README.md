# Chạy backend

# 1. Di chuyển vào thư mục backend

cd

# 2. Kích hoạt môi trường ảo

 .\.venv\Scripts\Activate

# 3. Khởi động server

python manage.py runserver

# chạy frontend

npm run dev

# 4. Tạo file ghi nhận sự thay đổi:

python manage.py makemigrations

# 5. Thực thi cập nhật vào Database (SQL Server):

python manage.py migrate

Trang xem / quản lý tỉnh thành (Day 28 — CRUD, Admin tab **Tỉnh / Thành**):

- GET (public): http://127.0.0.1:8000/api/tours/locations/
- POST/DELETE (Admin + token): cùng endpoint

Admin:

- http://127.0.0.1:8000/admin/tours/tour/2/change/

Trang review:

- http://localhost:5173/my-reviews

npm install recharts

Cài thư viện backend

Cài thư viện frontend
npm install

Tai du lieu ve:

python manage.py migrate

python manage.py loaddata users.json

python manage.py loaddata tour.json
## Quick Start

### 1. Ch?y Incremental Export Service
cd scripts/
pip install -r requirements.txt
python incremental_export.py

### 2. Ch?y Databricks Pipeline
- Run 00_verify_real_data.ipynb
- Run 01_bronze_ingestion.ipynb
- Run 02_silver_cleaning.ipynb

