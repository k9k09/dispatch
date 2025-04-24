from django.urls import path
from . import views

urlpatterns = [
    # Home view
    path('', views.home, name='home'),
    
    # Auth views
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('book-bike/<int:bike_id>/', views.book_bike, name='book_bike'),
    path('payments/', views.payments, name='payments'),
    path('payments/add/', views.add_payment_method, name='add_payment_method'),
    
    
    # Ride request views
    path('create-ride/', views.create_ride_request, name='create_ride_request'),
    path('ride/<int:ride_id>/', views.ride_detail, name='ride_detail'),
    path('ride/<int:ride_id>/accept/', views.accept_ride_request, name='accept_ride_request'),
    path('ride/<int:ride_id>/complete/', views.complete_ride, name='complete_ride'),
    path('ride/<int:ride_id>/rate/', views.add_rating, name='add_rating'),
    path('profile/', views.client_profile, name='client_profile'),
    path('my-trips/', views.my_trips, name='my_trips'),
    path('request-ride/', views.request_ride, name='request_ride'),
    path('find-rides/', views.find_rides, name='find_rides'),
    path('book-ride/<int:ride_id>/', views.book_ride, name='book_ride'),
    
    # Existing URLs...
    path('driver/login/', views.driver_login, name='driver_login'),
    path('driver/signup/', views.driver_signup, name='driver_signup'),
    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/rides/', views.driver_rides, name='driver_rides'),
    path('driver/ride/<int:ride_id>/accept/', views.accept_ride_request, name='accept_ride_request'),
    path('driver/ride/<int:ride_id>/complete/', views.complete_ride, name='complete_ride'),
    path('driver/payments/', views.driver_payments, name='driver_payments'),
    path('driver/update-location/', views.update_driver_location, name='update_driver_location'),
    
    path('driver/toggle-availability/', views.toggle_availability, name='toggle_availability'),
]
