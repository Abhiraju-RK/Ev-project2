from django.shortcuts import render,redirect,get_object_or_404
from . models import Client
from django.contrib.auth.models import User
from django.contrib import messages
from  django.contrib.auth import authenticate,login,logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from staff.models import AdminUser,Station,AvailableSlot,Booking,Contact
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.urls import reverse

# Create your views here.
def index(request):
    return render(request,'app/index.html')

def user_index(request):
    return render(request,'app/user_home.html')

def user_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_pass = request.POST.get('confirm_pass')
        phone = request.POST.get('phone')

        if not username or not email or not password or not confirm_pass or not phone:
            messages.error(request, "All fields are required!")
            return redirect('user_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Email already exists!')
            return redirect('user_register')

        if confirm_pass != password:
            messages.error(request, 'Passwords did not match!')
            return redirect('user_register')

        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, 'Phone number must be exactly 10 digits and contain only numbers!')
            return redirect('user_register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        Client.objects.create(user=user, phone=phone)

        messages.success(request, "Client registered successfully!")
        return redirect('user_login')

    return render(request, 'app/user_register.html')

def user_login(request):
    if request.method == "POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        try:
            user_obj=User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request,'You are  not registerd')
            return redirect('user_register')
        if  not Client.objects.filter(user=user_obj).exists():
            messages.error(request, 'You are not registered as an user !')
            return redirect('user_register')

        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,f'{user.username} successfully login ')
            return redirect('user_index')
        else:
            messages.error(request, 'Invalid email or password!')
    return render(request,'app/user_login.html')
        
def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def user_profile(request):
    user=request.user
    if request.method == "POST":
        if "user_update" in request.POST:
            user.username=request.POST.get('username',user.username)
        
            user.email=request.POST.get('email',user.email)
            user.phone=request.POST.get('phone',user.phone)
            user.save()
            messages.success(request,'Profile update successfully ')
            return redirect('user_profile')
        elif "user_pass" in request.POST:
            current_password=request.POST.get('current_password')
            new_password=request.POST.get('new_password')
            confirm_password=request.POST.get('confirm_password')

            if confirm_password!=new_password:
                messages.error(request,'Invalid password !!')
                return redirect('user_profile')
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect!")
                return redirect('user_profile')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully!")

        return redirect('user_profile')
    
    return render(request, 'app/user_profile.html',)

@login_required
def user_station_list(request):
    user_stations=Station.objects.all()
    return render(request,"app/user_station_list.html",{'user_stations':user_stations})


@login_required
def user_slot_list(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    slots = AvailableSlot.objects.filter(station=station)
    return render(request, 'app/user_slot_list.html', {'slots': slots, 'station': station})


@login_required
def book_slot(request, book_id):
    client = Client.objects.get(user=request.user)
    slot = get_object_or_404(AvailableSlot, id=book_id)

    if request.method == 'POST':
        booking_date_str = request.POST.get('booking_date')
        booking_time_str = request.POST.get('booking_time')
        duration=int(request.POST.get('duration_minutes'))

        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            booking_time = datetime.strptime(booking_time_str, "%H:%M").time()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date or time format.")
            return redirect('book_slot', book_id=book_id)

        if not slot.is_available(booking_date, booking_time):
            messages.error(request, "This station is already booked at this time. Please choose a different time.")
            return redirect('book_slot', book_id=book_id)
        
        # Calculate total price (slot.price is per 30 minutes)
        total_price=(duration // 30) * slot.price
        booking=Booking.objects.create(
            client=client,
            slot=slot,
            booked_at=timezone.now(),
            booking_date=booking_date,
            booking_time=booking_time,
            duration_minutes=duration,
            total_price=total_price
        )

        messages.success(request, "Slot booked successfully!")
        return redirect('dummy_payment',booking_id=booking.id)

    return render(request, 'app/book_slot.html', {'slot': slot})

@login_required
def dummy_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, client__user=request.user)

    if request.method == 'POST':
        # Simulate a "payment"
        booking.payment_status = "Completed"  # If you have a field for this
        booking.save()

        messages.success(request, "Payment completed successfully!")
        return redirect('user_slot_bookings')

    return render(request, 'app/dummy_payment.html', {'booking': booking})

@login_required
def user_slot_bookings(request):
    client=Client.objects.get(user=request.user)
    bookings=Booking.objects.filter(client=client)
    return render(request,'app/user_slot_bookings.html',{'bookings':bookings})

@login_required
def search_station(request):
    query=request.GET.get('q','').strip()
    stations=Station.objects.all()
    if query:
        stations=stations.filter(
            Q(location__icontains=query) |
            Q(city__icontains=query) |
            Q(name__icontains=query)
        ) if query else Station.objects.all()
    return render(request, 'app/search_list.html', {'stations': stations, 'query': query})
    

@login_required
def contact(request):
    user=get_object_or_404(Client,user=request.user)
    if request.method == "POST":
        name=request.POST.get('name')
        mail=request.POST.get('mail')
        phone=request.POST.get('phone')
        message=request.POST.get('message')

        contacts=Contact.objects.create(user=user,name=name,mail=mail,phone=phone,message=message)
        contacts.save()
        messages.success(request,'Your message is send successfuly our team contact you shortly')
        return redirect('user_index')
    return render(request,'app/contact.html')

@login_required
def about_us(request):
    return render(request,'app/about.html')