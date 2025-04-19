from django.urls import path
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('user_index',views.user_index,name='user_index'),
    path('user_register',views.user_register,name='user_register'),
    path('user_login',views.user_login,name='user_login'),
    path('user_logout',views.user_logout,name='user_logout'),
    path('user_profile',views.user_profile,name='user_profile'),

    path('user_station_list',views.user_station_list,name='user_station_list'),
    path('book_slot/<int:book_id>/',views.book_slot,name='book_slot'),
    path('user_slot_bookings',views.user_slot_bookings,name='user_slot_bookings'),
    path('user_station_list/<int:station_id>/user_slot_list',views.user_slot_list,name='user_slot_list'),
    path('search_station',views.search_station,name='search_station'),
    path('dummy_payment/<int:booking_id>/',views.dummy_payment,name='dummy_payment'),

    path('contact',views.contact,name='contact'),
    path('about_us',views.about_us,name='about_us'),
]