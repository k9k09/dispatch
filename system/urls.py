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

    # Ride request views
    path('create-ride/', views.create_ride_request, name='create_ride_request'),
    path('ride/<int:ride_id>/', views.ride_detail, name='ride_detail'),
    path('ride/<int:ride_id>/accept/', views.accept_ride_request, name='accept_ride_request'),
    path('ride/<int:ride_id>/complete/', views.complete_ride, name='complete_ride'),
    path('ride/<int:ride_id>/rate/', views.add_rating, name='add_rating'),
]
