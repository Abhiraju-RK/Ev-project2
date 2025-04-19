from django.contrib import admin
from . models import AdminUser,Station,AvailableSlot,Booking
from user.models import Client
# Register your models here.

class AdminBooking(admin.ModelAdmin):
    list_display = ['client', 'slot', 'booking_date']
class AdminStaff(admin.ModelAdmin):
    list_display = ['user', 'phone']
class AdminAvailableSlot(admin.ModelAdmin):
    list_display = ['station', 'name', 'price']
class AdminStation(admin.ModelAdmin):
    list_display = ['name', 'district', 'location']
class AdminClient(admin.ModelAdmin):
    list_display = ['email', 'phone']

admin.site.register(AdminUser,AdminStaff)
admin.site.register(AvailableSlot,AdminAvailableSlot)
admin.site.register(Booking,AdminBooking)
admin.site.register(Client,AdminClient)
admin.site.register(Station,AdminStation)