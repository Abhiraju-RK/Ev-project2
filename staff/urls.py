from django.urls import path
from . import views

urlpatterns = [
    path('admin_home',views.admin_home,name='admin_home'),
    path('admin_register',views.admin_register,name='admin_register'),
    path('admin_login',views.admin_login,name='admin_login'),
    path('admin_logout',views.admin_logout,name='admin_logout'),
    path('staff_profile',views.staff_profile,name='staff_profile'),

    path('station_list',views.station_list,name='station_list'),
    path('add_station',views.add_station,name='add_station'),
    path('edit_station/<int:station_id>/', views.edit_station, name='edit_station'),
    path('add_slot',views.add_slot,name='add_slot'),
    path('slot_list/<int:station_id>/',views.slot_list,name='slot_list'),
    path('slot_bookings',views.slot_bookings,name='slot_bookings'),

    path('add_location',views.add_location,name='add_location'),
    path('edit_station/<int:station_id>/', views.edit_station, name='edit_station'),
    path('delete_station/<int:station_id>/', views.delete_station, name='delete_station'),
]
