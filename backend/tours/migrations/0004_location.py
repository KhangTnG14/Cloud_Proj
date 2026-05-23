from django.db import migrations, models


DEFAULT_LOCATIONS = [
    ("Hà Nội", 21.0285, 105.8542),
    ("Hồ Chí Minh", 10.8231, 106.6297),
    ("Đà Nẵng", 16.0471, 108.2068),
    ("Nha Trang", 12.2388, 109.1967),
    ("Đà Lạt", 11.9404, 108.4583),
    ("Phú Quốc", 10.2899, 103.9840),
]


def seed_locations(apps, schema_editor):
    Location = apps.get_model('tours', 'Location')
    for name, lat, lng in DEFAULT_LOCATIONS:
        Location.objects.get_or_create(name=name, defaults={'lat': lat, 'lng': lng})


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0003_category_tour_categories'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Tên tỉnh/thành')),
                ('lat', models.FloatField(verbose_name='Vĩ độ')),
                ('lng', models.FloatField(verbose_name='Kinh độ')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Tỉnh/Thành',
                'verbose_name_plural': 'Các tỉnh/thành',
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(seed_locations, migrations.RunPython.noop),
    ]
