from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Profile, Motorcycle, RideRequest, Payment, Rating
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, logout
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def home(request):
    motorcycles = Motorcycle.objects.all()  # Removed filter for availability

    return render(request, 'index.html', {'motorcycles': motorcycles})

# User Authentication Views
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone = request.POST.get('phone', '').strip()  # Get phone and strip whitespace
            if phone:  # Only create profile if phone is provided
                Profile.objects.create(

                user=user,
                phone=phone,
                user_type='client'  # Default to client
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

# Driver Location Update (GPS Tracking)
@csrf_exempt
def update_driver_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            driver_id = data.get('driver_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            if not all([driver_id, latitude, longitude]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            motorcycle = Motorcycle.objects.get(driver_id=driver_id)
            motorcycle.latitude = float(latitude)
            motorcycle.longitude = float(longitude)
            motorcycle.save()

            return JsonResponse({'status': 'success'})
        except Motorcycle.DoesNotExist:
            return JsonResponse({'error': 'Motorcycle not found'}, status=404)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid data format'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

# Create Ride Request (Client)
@login_required
def create_ride_request(request):
    if request.method == "POST":
        client = request.user.profile
        ride_request = RideRequest.objects.create(
            client=client,
            pickup_location=request.POST.get('pickup_location'),
            dropoff_location=request.POST.get('dropoff_location'),
            pickup_latitude=float(request.POST.get('pickup_latitude', 0.0)),
            pickup_longitude=float(request.POST.get('pickup_longitude', 0.0)),
            dropoff_latitude=float(request.POST.get('dropoff_latitude', 0.0)),
            dropoff_longitude=float(request.POST.get('dropoff_longitude', 0.0))
        )
        return redirect('ride_detail', ride_id=ride_request.id)
    return render(request, 'create_ride_request.html')

# View Ride Request details
@login_required
def ride_detail(request, ride_id):
    ride_request = get_object_or_404(RideRequest, id=ride_id)
    return render(request, 'ride_detail.html', {'ride_request': ride_request})

# Accept Ride Request (Driver)
@login_required
def accept_ride_request(request, ride_id):
    ride_request = get_object_or_404(RideRequest, id=ride_id)
    if ride_request.status == 'pending' and ride_request.driver is None:
        ride_request.driver = request.user.profile
        ride_request.status = 'accepted'
        ride_request.save()
        return redirect('ride_detail', ride_id=ride_request.id)

    return JsonResponse({'error': 'Ride request already accepted or unavailable'}, status=400)

# Complete Ride Request (Driver)
@login_required
def complete_ride(request, ride_id):
    ride_request = get_object_or_404(RideRequest, id=ride_id)

    if ride_request.status == 'ongoing' and ride_request.driver == request.user.profile:
        ride_request.status = 'completed'
        ride_request.save()

        # Create Payment Record
        Payment.objects.create(
            ride=ride_request,
            amount=ride_request.fare,
            method=request.POST.get('payment_method', 'cash')  # Default to cash if not specified
        )
        return redirect('ride_detail', ride_id=ride_request.id)

    return JsonResponse({'error': 'Ride cannot be completed'}, status=400)

# Add Rating for Ride
@login_required
def add_rating(request, ride_id):
    ride_request = get_object_or_404(RideRequest, id=ride_id)

    if request.method == 'POST':
        rating_value = int(request.POST.get('rating', 0))
        review_text = request.POST.get('review')

        if 1 <= rating_value <= 5:
            Rating.objects.create(
                ride=ride_request,
                client=ride_request.client,
                driver=ride_request.driver,
                rating=rating_value,
                review=review_text
            )
            return redirect('ride_detail', ride_id=ride_request.id)

        return JsonResponse({'error': 'Invalid rating value'}, status=400)

    return render(request, 'add_rating.html', {'ride_request': ride_request})

# User Dashboard
@login_required
def dashboard(request):
    try:
        profile = request.user.profile  # Attempt to access the user's profile
        context = {
            'total_rides': RideRequest.objects.filter(client=profile).count(),

        'total_distance': 487,
        'total_spent': 345,
        'recent_bookings': RideRequest.objects.filter(client=request.user.profile).order_by('-created_at')[:5],
        'nearby_bikes': Motorcycle.objects.filter(availability=True).order_by('distance')[:5]
    }
        return render(request, 'dashboard.html', context)
    except Profile.DoesNotExist:
        return redirect('signup')  # Redirect to signup if the profile does not exist


# Book a Bike (Client)
@login_required
def book_bike(request, bike_id):
    if request.method == 'POST':
        try:
            # Book the bike (This needs actual model implementation)
            return JsonResponse({
                'status': 'success',
                'message': 'Booking confirmed',
                'booking_id': bike_id  # Return actual booking ID in production
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # If GET request, display bike details
    bike_details = next(
        (bike for bike in [
            {'id': 1, 'name': 'Harley Davidson Iron 883', 'price': 40, 
             'image': 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=600&h=400'},
            {'id': 2, 'name': 'Ducati Monster', 'price': 50, 
             'image': 'https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&w=600&h=400'},
            {'id': 3, 'name': 'BMW R1250GS', 'price': 55, 
             'image': 'https://images.unsplash.com/photo-1609630875171-b1321377ee65?auto=format&fit=crop&w=600&h=400'}
        ] if bike['id'] == bike_id),
        None
    )

    if not bike_details:
        raise PermissionDenied("Bike not found")

    return render(request, 'find_riders.html', {'bike': bike_details})
