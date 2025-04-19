from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from . models import AdminUser,Station,AvailableSlot,Booking,Location,Contact
from user.models import Client
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User

# Create your views here.
def admin_home(request):
    return render(request,'app/admin_home.html')

def admin_register(request):
    if request.method == "POST":
        username=request.POST.get("username")
        email=request.POST.get('email')
        password=request.POST.get('password')
        confrim_pass=request.POST.get('confirm_pass')
        phone=request.POST.get('phone')
        is_superuser=request.POST.get('is_superuser')=='on'

        if not username or not email or not password or not confrim_pass or not phone:
            messages.error(request,"All feild requires  !!")
            return redirect('admin_register')
        if User.objects.filter(username=username).exists():
            messages.error(request,"Email Already exists !!")
            return redirect('admin_register')
        if not phone.isdigit() or len(phone)!=10:
            messages.error(request,"Phone number must have 10 digit !!")
            return redirect('admin_register')
        if confrim_pass!=password:
            messages.error(request,"Password doesnt match !!")
            return redirect('admin_register')

        if len(password)<5:
            messages.error(request,"Password must be above five character !!")
            return redirect('admin_register')
        
        user=User.objects.create_user(username=username,email=email,password=password)
        user.is_superuser=is_superuser
        user.is_staff=is_superuser
        user.save()

        AdminUser.objects.create(user=user,phone=phone,is_superuser=is_superuser)

        messages.success(request,"Register Successfully")
        return redirect('admin_login')
    return render(request, 'app/admin_register.html') 

def admin_login(request):
    if request.method == "POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        try:
            user_obj=User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request,'You are  not registerd')
            return redirect('admin_register')
        if not AdminUser.objects.filter(user=user_obj).exists():
            messages.error(request, 'You are not registered as an Admin!')
            return redirect('admin_register')
        
        user=authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            messages.success(request,f'{user.username} successfully login ')
            return redirect('admin_home')
        else:
            messages.error(request, 'Invalid Username or password!')
    return render(request,'app/admin_login.html')

def admin_logout(request):
    logout(request)
    return redirect('index')

@login_required
def staff_profile(request):
    user=request.user
    if request.method == "POST":
        if "staff_update" in request.POST:
            user.username=request.POST.get('username',user.username)
        
            user.email=request.POST.get('email',user.email)
            user.phone=request.POST.get('phone',user.phone)
            user.save()
            messages.success(request,'Profile update successfully ')
            return redirect('staff_profile')
        elif "staff_pass" in request.POST:
            current_password=request.POST.get('current_password')
            new_password=request.POST.get('new_password')
            confirm_password=request.POST.get('confirm_password')

            if confirm_password!=new_password:
                messages.error(request,'Invalid password !!')
                return redirect('staff_profile')
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect!")
                return redirect('staff_profile')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully!")

        return redirect('staff_profile')
    
    return render(request, 'app/staff_profile.html',)

@login_required
def station_list(request):
    stations=Station.objects.all()
    return render(request,'app/station_list.html',{'stations':stations})


@login_required
def add_station(request):
    admins = AdminUser.objects.get(user=request.user)
    selected_district = None
    locations = []

    if request.method == "POST":
        name = request.POST.get("name")
        selected_district = request.POST.get("district")
        location_id = request.POST.get("location")

        if name and selected_district and location_id:
            try:
                location = Location.objects.get(id=location_id, district=selected_district)
                Station.objects.create(
                    user=admins,
                    name=name,
                    district=selected_district,
                    location=location
                )
                messages.success(request, "Station added successfully!")
                return redirect('station_list')
            except Location.DoesNotExist:
                messages.error(request, "Invalid location selected.")
        else:
            messages.error(request, "Please fill all fields.")

        # If only district is selected, show filtered locations
        if selected_district:
            locations = Location.objects.filter(district=selected_district)

    districts = Location.objects.values_list('district', flat=True).distinct()
    return render(request, 'app/add_station.html', {
        'districts': districts,
        'locations': locations,
        'selected_district': selected_district
    })

@login_required
def edit_station(request, station_id): 
    staff = AdminUser.objects.get(user=request.user)
    try:
        station = Station.objects.get(id=station_id, user=staff)
    except Station.DoesNotExist:
        messages.error(request, "Station not found or you don't have permission to edit it.")
        return redirect('station_list')

    selected_district = station.district
    locations = Location.objects.filter(district=selected_district)

    if request.method == "POST":
        station.name = request.POST.get('name')
        selected_district = request.POST.get('district')
        location_id = request.POST.get('location')

        if station.name and selected_district and location_id:
            try:
                location = Location.objects.get(id=location_id, district=selected_district)
                station.district = selected_district
                station.location = location
                station.save()
                messages.success(request, "Station edited successfully.")
                return redirect('station_list')
            except Location.DoesNotExist:
                messages.error(request, 'Invalid location selected.')
        else:
            messages.error(request, "Please fill all fields.")

        locations = Location.objects.filter(district=selected_district)

    districts = Location.objects.values_list('district', flat=True).distinct()
    return render(request, 'app/admin_edit_station.html', {
        'station': station,
        'districts': districts,
        'locations': locations,
        'selected_district': selected_district
    })


@login_required
def delete_station(request,station_id):
    staff=AdminUser.objects.get(user=request.user)
    stations=get_object_or_404(Station,id=station_id,user=staff)
    stations.delete()
    return redirect('station_list')




@login_required
def add_slot(request):
    if request.method == "POST":
        name=request.POST.get('name')   
        price=request.POST.get('price')
        station_id=request.POST.get('station')

        try:
            station=Station.objects.get(id=station_id)
            AvailableSlot.objects.create(station=station,name=name,price=price,is_booked=False)
            messages.success(request, "Slot added successfully!")
            return redirect('slot_list',station_id=station.id)
        except Station.DoesNotExist:
            messages.error(request,"Slot dint addedd !!")
    stations=Station.objects.all()
    return render(request,'app/add_slot.html',{'stations':stations})

@login_required
def slot_list(request,station_id):
    station = get_object_or_404(Station, id=station_id)
    slots = AvailableSlot.objects.filter(station=station)
    return render(request,'app/slot_list.html',{'slots':slots})

@login_required
def slot_bookings(request):
    bookings=Booking.objects.all()
    return render(request,'app/slot_bookings.html',{'bookings':bookings})

@login_required
def add_location(request):
    if request.method == "POST":
        district = request.POST.get("district")
        location_name = request.POST.get("location")

        try:
            admin_user = AdminUser.objects.get(user=request.user)  # 🔥 This line fixes the issue

            if district and location_name:
                if district not in dict(Location.DISTRICT_CHOICES):
                    messages.error(request, "Invalid district selected.")
                else:
                    Location.objects.create(user=admin_user, name=location_name, district=district)
                    messages.success(request, "Location added successfully!")
                    return redirect('add_station')  # or whatever your success URL is
            else:
                messages.error(request, "Please fill all fields.")
        except AdminUser.DoesNotExist:
            messages.error(request, "You are not authorized to add a location.")

    return render(request, 'app/add_location.html', {
        'district_choices': Location.DISTRICT_CHOICES
    })

