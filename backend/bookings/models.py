from django.db import models
from django.conf import settings
from tours.models import Tour

# class Booking(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
#     number_of_people = models.IntegerField()
#     status = models.CharField(max_length=20, default='PENDING')
#     created_at = models.DateTimeField(auto_now_add=True)
