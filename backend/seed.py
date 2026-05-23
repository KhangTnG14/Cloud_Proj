import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from tours.models import Tour, Category, Location
from django.utils.text import slugify

def seed_data():
    print("--- Seeding Sample Data ---")
    
    # 1. Create Creator
    creator, created = User.objects.get_or_create(
        username='creator1',
        defaults={
            'email': 'creator1@example.com',
            'phone': '0912345678',
            'role': 'CREATOR'
        }
    )
    if created:
        creator.set_password('password123')
        creator.save()
        print("- Created user Creator: creator1")
    else:
        print("- User Creator already exists")

    # 2. Create Customer
    customer, created = User.objects.get_or_create(
        username='customer1',
        defaults={
            'email': 'customer1@example.com',
            'phone': '0987654321',
            'role': 'CUSTOMER'
        }
    )
    if created:
        customer.set_password('password123')
        customer.save()
        print("- Created user Customer: customer1")

    # 3. Danh mục tour (Day 28)
    default_categories = ['Biển', 'Núi', 'Văn hóa', 'Ẩm thực', 'Khám phá']
    for name in default_categories:
        cat, created = Category.objects.get_or_create(
            name=name,
            defaults={'slug': slugify(name), 'description': f'Danh mục {name}'},
        )
        if created:
            print(f"- Created Category: {name}")

    # 4. Tỉnh / thành (Day 28)
    default_locations = [
        ("Hà Nội", 21.0285, 105.8542),
        ("Hồ Chí Minh", 10.8231, 106.6297),
        ("Đà Nẵng", 16.0471, 108.2068),
        ("Nha Trang", 12.2388, 109.1967),
        ("Đà Lạt", 11.9404, 108.4583),
        ("Phú Quốc", 10.2899, 103.9840),
    ]
    for name, lat, lng in default_locations:
        loc, created = Location.objects.get_or_create(
            name=name,
            defaults={'lat': lat, 'lng': lng},
        )
        if created:
            print(f"- Created Location: {name}")

    # 5. Create Tours
    tour1, created = Tour.objects.get_or_create(
        title='Tour Du Lich Ha Long 2 Ngay 1 Dem',
        defaults={
            'creator': creator,
            'description': 'Chao mung ban den voi ky nghi tuyet voi tai Vinh Ha Long. Kham pha ve dep ky vi cua thien nhien.',
            'price': 2500000,
            'slots': 20
        }
    )
    if created:
        print("- Created Tour: Ha Long")

    tour2, created = Tour.objects.get_or_create(
        title='Kham Pha Da Lat Mong Mo',
        defaults={
            'creator': creator,
            'description': 'Da Lat voi khong khi trong lanh va nhung thung lung hoa ruc ro dang cho don ban.',
            'price': 1800000,
            'slots': 15
        }
    )
    if created:
        print("- Created Tour: Da Lat")

    print("--- Seeding Completed ---")

if __name__ == "__main__":
    seed_data()
