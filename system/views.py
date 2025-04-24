from datetime import timezone
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Ride  # Add this if missing
from .models import PaymentMethod  # Add this if missing
from .models import Transaction  # Add this if missing
from .models import Profile, Motorcycle, RideRequest, Payment, Rating
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, logout
from django.utils.timezone import timezone, now
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.db.models import Sum, Count, Avg, Max, Min



def home(request):
    return render(request, 'landingpage.html')

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
    return render(request, 'client/signup.html', {'form': form})

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
    return render(request, 'client/login.html', {'form': form})

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
    return render(request, 'client/ride_detail.html', {'ride_request': ride_request})

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

    return render(request, 'client/add_rating.html', {'ride_request': ride_request})



# User Dashboard
@login_required
def dashboard(request):
    try:
        profile = request.user.profile  # Attempt to access the user's profile
        
        # Get recent bookings by this user
        recent_bookings = RideRequest.objects.filter(client=profile).order_by('-created_at')[:5]
        
        # Get available motorcycles sorted by distance
        nearby_bikes = Motorcycle.objects.filter(availability=True).order_by('distance')[:5]
        
        # Calculate total spent from payments
        total_spent = Payment.objects.filter(ride__client=profile).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        # Get completed rides
        completed_rides = RideRequest.objects.filter(
            client=profile, 
            status='completed'
        )
        
        # Count total completed rides
        total_rides = completed_rides.count()
        
        # Calculate total distance from completed rides
        total_distance = completed_rides.aggregate(
            total=models.Sum('distance_km')
        )['total'] or 0
        
        context = {
            'total_rides': total_rides,
            'total_distance': total_distance,
            'total_spent': total_spent,
            'recent_bookings': recent_bookings,
            'nearby_bikes': nearby_bikes,
            'profile': profile,
        }
        return render(request, 'client/index.html', context)
    except Profile.DoesNotExist:
        # Create a profile for the user if one doesn't exist
        profile = Profile.objects.create(
            user=request.user,
            phone=f"temp-{request.user.id}",  # Use a unique phone placeholder
            user_type='client'  # Default to client
        )
        messages.success(request, "Your profile has been created. Please update your phone number.")
        return redirect('dashboard')  # Redirect back to dashboard with the new profile

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

    return render(request, 'client/find_riders.html', {'bike': bike_details})



@login_required
def client_profile(request):
    profile = get_object_or_404(Profile, user=request.user, user_type='client')
    context = {
        'profile': profile,
    }
    return render(request, 'client/Profile.html', context)

from .models import Trip
@login_required
def my_trips(request):
    # Fetch trips for the logged-in user
    trips = Trip.objects.filter(user=request.user)
    
    context = {
        'trips': trips,
    }
    return render(request, 'client/my_trips.html', context)

@login_required
def request_ride(request):
    if request.method == 'POST':
        # Extract form data
        from_location = request.POST.get('from_location')
        to_location = request.POST.get('to_location')
        ride_type = request.POST.get('ride_type', 'Standard')
        date = request.POST.get('date', now().date())  # Default to today if not provided
        time = request.POST.get('time', now().time())  # Default to now if not provided
        price = request.POST.get('price', 250)  # Default price, adjust based on ride_type in real app

        # Create a new Trip instance
        trip = Trip(
            user=request.user,
            from_location=from_location,
            to_location=to_location,
            date=date,
            time=time,
            price=price,
            ride_type=ride_type,
            status='Pending'
        )
        trip.save()

        # Redirect to My Trips page after successful submission
        return redirect('my_trips')

    # For GET request, render the form
    return render(request, 'client/request_ride.html')

@login_required
def find_rides(request):
    # Get search parameters from GET request
    from_location = request.GET.get('from', '')
    to_location = request.GET.get('to', '')
    ride_type = request.GET.get('ride_type', '')

    # Filter rides based on search criteria
    rides = Ride.objects.filter(status='available')
    
    if from_location:
        rides = rides.filter(from_location__icontains=from_location)
    if to_location:
        rides = rides.filter(to_location__icontains=to_location)
    if ride_type:
        rides = rides.filter(ride_type=ride_type)

    context = {
        'rides': rides,
    }
    return render(request, 'client/find_rides.html', context)

@login_required
def book_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, status='available')
    
    if request.method == 'POST':
        # Book the ride
        ride.rider = request.user
        ride.status = 'booked'
        ride.save()
        return redirect('dashboard')  # Redirect to dashboard or a confirmation page
    
    # For GET request, you might want to show a confirmation page
    context = {
        'ride': ride,
    }
    return render(request, 'client/book_ride.html', context)  # You'll need to create this template if you want a confirmation step

@login_required
def payments(request):
    # Get user's payment methods and transactions
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]  # Last 5 transactions
    
    # Calculate totals
    total_spent = Transaction.objects.filter(user=request.user, status='Completed').aggregate(models.Sum('amount'))['amount__sum'] or 0
    pending_payments = Transaction.objects.filter(user=request.user, status='Pending').aggregate(models.Sum('amount'))['amount__sum'] or 0

    context = {
        'payment_methods': payment_methods,
        'transactions': transactions,
        'total_spent': total_spent,
        'pending_payments': pending_payments,
    }
    return render(request, 'client/payments.html', context)

@login_required
def add_payment_method(request):
    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        # Basic validation (in a real app, use a payment gateway like Stripe)
        try:
            expiry = datetime.datetime.strptime(expiry_date, '%m/%y')
            last_four = card_number[-4:]
            card_type = "Visa" if card_number.startswith('4') else "MasterCard"  # Simplified detection

            PaymentMethod.objects.create(
                user=request.user,
                card_type=card_type,
                last_four=last_four,
                expiry_date=expiry
            )
            messages.success(request, "Payment method added successfully!")
            return redirect('payments')
        except ValueError:
            messages.error(request, "Invalid expiry date format. Use MM/YY.")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")

    return redirect('payments')  # Redirect back if not POST

def driver_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.profile.user_type == 'driver':
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('driver_dashboard')
            else:
                messages.error(request, 'This account is not a driver account.')
    else:
        form = AuthenticationForm()
    return render(request, 'driver/login.html', {'form': form})

def driver_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone = request.POST.get('phone', '').strip()
            plate_number = request.POST.get('plate_number', '').strip()
            if phone and plate_number:
                profile = Profile.objects.create(
                    user=user,
                    phone=phone,
                    user_type='driver'
                )
                Motorcycle.objects.create(
                    driver=profile,
                    plate_number=plate_number,
                    availability=True
                )
                login(request, user)
                messages.success(request, 'Driver account created successfully!')
                return redirect('driver_dashboard')
            else:
                messages.error(request, 'Phone number and plate number are required.')
    else:
        form = UserCreationForm()
    return render(request, 'driver/signup.html', {'form': form})

@login_required
def driver_dashboard(request):
    profile = request.user.profile
    if profile.user_type != 'driver':
        messages.error(request, 'Access denied. Driver account required.')
        return redirect('home')

    # Get available rides
    available_rides = RideRequest.objects.filter(status='pending', driver__isnull=True)

    # Get recent trips
    recent_trips = RideRequest.objects.filter(driver=profile).order_by('-created_at')[:5]

    # Calculate stats
    total_rides = RideRequest.objects.filter(driver=profile, status='completed').count()
    total_earnings = Payment.objects.filter(ride__driver=profile).aggregate(total=Sum('amount'))['total'] or 0
    average_rating = Rating.objects.filter(driver=profile).aggregate(avg=Avg('rating'))['avg'] or 0

    context = {
        'available_rides': available_rides,
        'recent_trips': recent_trips,
        'total_rides': total_rides,
        'total_earnings': total_earnings,
        'average_rating': round(average_rating, 1),
        'profile': profile,
    }
    return render(request, 'driver/driver_dashboard.html', context)

@login_required
def driver_rides(request):
    profile = request.user.profile
    if profile.user_type != 'driver':
        messages.error(request, 'Access denied. Driver account required.')
        return redirect('home')

    rides = RideRequest.objects.filter(driver=profile) | RideRequest.objects.filter(status='pending', driver__isnull=True)
    context = {
        'rides': rides.order_by('-created_at'),
    }
    return render(request, 'driver/rides.html', context)

@login_required
def driver_payments(request):
    profile = request.user.profile
    if profile.user_type != 'driver':
        messages.error(request, 'Access denied. Driver account required.')
        return redirect('home')

    payments = Payment.objects.filter(ride__driver=profile).order_by('-timestamp')
    total_earnings = payments.aggregate(total=Sum('amount'))['total'] or 0
    pending_payments = payments.filter(ride__status='ongoing').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'payments': payments,
        'total_earnings': total_earnings,
        'pending_payments': pending_payments,
    }
    return render(request, 'driver/payments.html', context)

@login_required
@csrf_exempt
def toggle_availability(request):
    if request.method == 'POST':
        profile = request.user.profile
        if profile.user_type != 'driver':
            return JsonResponse({'error': 'Access denied'}, status=403)
        motorcycle = Motorcycle.objects.get(driver=profile)
        motorcycle.availability = not motorcycle.availability
        motorcycle.save()
        return JsonResponse({'status': 'success', 'availability': motorcycle.availability})
    return JsonResponse({'error': 'Invalid request'}, status=400)