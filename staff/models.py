from django.db import models
from user.models import Client
from django.contrib.auth.models import User
# Create your models here.

class AdminUser(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=15,blank=True,null=True)
    is_superuser=models.BooleanField(default=False)


    def __str__(self):
        return self.user.username
    


class Location(models.Model):
    DISTRICT_CHOICES=[
        ('Thiruvanathapuram','Thiruvanathapuram'),
        ('Kollam','Kollam'),
    ]
    user=models.ForeignKey(AdminUser,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    district=models.CharField(max_length=200,choices=DISTRICT_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.district})"

class Station(models.Model):
    user=models.ForeignKey(AdminUser,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    district=models.CharField(max_length=200,choices=Location.DISTRICT_CHOICES)
    location=models.ForeignKey(Location,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class AvailableSlot(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    is_booked = models.BooleanField(default=False)

    def is_available(self,booking_date,booking_time):
        return not Booking.objects.filter(
            slot__station=self.station,
            booking_date=booking_date,
            booking_time=booking_time,
        ).exists()

class Booking(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    slot = models.ForeignKey(AvailableSlot, on_delete=models.CASCADE)
    booked_at = models.DateTimeField()
    booking_date=models.DateField(null=True,blank=True)
    booking_time=models.TimeField(null=True,blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)  # User can choose 30, 60, 90, etc.
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')

    def __str__(self):
        return f"{self.client.user.username} booked {self.slot}"

class Contact(models.Model):
    user=models.ForeignKey(Client,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    mail=models.EmailField()
    phone=models.CharField(max_length=15,default=False,null=False)
    message=models.TextField()

    def __str__(self):
        return self.name
    