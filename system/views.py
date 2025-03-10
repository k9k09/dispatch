from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Motorcycle
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Profile, Motorcycle, RideRequest, Payment, Rating
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.timezone import now

@csrf_exempt
def update_driver_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        driver_id = data.get('driver_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        try:
            motorcycle = Motorcycle.objects.get(driver_id=driver_id)
            motorcycle.latitude = latitude
            motorcycle.longitude = longitude
            motorcycle.save()
            return JsonResponse({'status': 'success'})
        except Motorcycle.DoesNotExist:
            return JsonResponse({'error': 'Motorcycle not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# Home View - for clients and drivers to view available rides, etc.
def home(request):
    motorcycles = Motorcycle.objects.filter(availability=True)
    return render(request, 'home.html', {'motorcycles': motorcycles})

# Create Ride Request (Client)
@login_required
def create_ride_request(request):
    if request.method == "POST":
        client = request.user.profile
        pickup_location = request.POST.get('pickup_location')
        dropoff_location = request.POST.get('dropoff_location')

        ride_request = RideRequest.objects.create(
            client=client,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            pickup_latitude=request.POST.get('pickup_latitude'),
            pickup_longitude=request.POST.get('pickup_longitude'),
            dropoff_latitude=request.POST.get('dropoff_latitude'),
            dropoff_longitude=request.POST.get('dropoff_longitude')
        )
        return redirect('ride_detail', ride_id=ride_request.id)
    return render(request, 'create_ride_request.html')

# View Ride Request details (both client and driver can view)
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
        # Create payment
        payment = Payment.objects.create(
            ride=ride_request,
            amount=ride_request.fare,
            method=request.POST.get('payment_method')
        )
        return redirect('ride_detail', ride_id=ride_request.id)
    return JsonResponse({'error': 'Ride cannot be completed'}, status=400)

# Add Rating for Ride
@login_required
def add_rating(request, ride_id):
    ride_request = get_object_or_404(RideRequest, id=ride_id)
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        review_text = request.POST.get('review')
        if 1 <= int(rating_value) <= 5:
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
