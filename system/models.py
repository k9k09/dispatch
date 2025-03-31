from django.db import models
from django.contrib.auth.models import User

# User Profile for Clients and Drivers
class Profile(models.Model):
    USER_TYPES = (
        ('client', 'Client'),
        ('driver', 'Driver'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

    class Meta:
        ordering = ['user__username']

# Motorcycle Model (Includes GPS Tracking)
class Motorcycle(models.Model):
    driver = models.OneToOneField(
        Profile, 
        on_delete=models.CASCADE, 
        related_name="motorcycle"
    )
    plate_number = models.CharField(max_length=20, unique=True)
    latitude = models.FloatField(default=0.0)  # GPS Latitude
    longitude = models.FloatField(default=0.0)  # GPS Longitude
    availability = models.BooleanField(default=True)  # Indicates if the motorcycle is available
    distance = models.FloatField(default=0.0)  # Distance from a reference point (can be updated dynamically)

    def __str__(self):
        return f"{self.plate_number} - {self.driver.user.username}"

    class Meta:
        ordering = ['plate_number']

# Ride Request Model (With GPS Coordinates)
class RideRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    client = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'client'}, 
        related_name="client_rides"
    )
    driver = models.ForeignKey(
        Profile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'user_type': 'driver'}, 
        related_name="driver_rides"
    )
    pickup_location = models.CharField(max_length=255, blank=True, null=True)
    dropoff_location = models.CharField(max_length=255, blank=True, null=True)
    pickup_latitude = models.FloatField(default=0.0)
    pickup_longitude = models.FloatField(default=0.0)
    dropoff_latitude = models.FloatField(default=0.0)
    dropoff_longitude = models.FloatField(default=0.0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    distance_km = models.FloatField(default=0.0)  # Distance in kilometers

    def __str__(self):
        return f"Ride {self.id} - {self.client.user.username} ({self.status})"

    class Meta:
        ordering = ['-created_at']

# Payment Model
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile_money', 'Mobile Money'),
    )
    ride = models.OneToOneField(RideRequest, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.amount} ({self.method})"

    class Meta:
        ordering = ['-timestamp']

# Ratings and Reviews Model
class Rating(models.Model):
    ride = models.OneToOneField(RideRequest, on_delete=models.CASCADE)
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="client_ratings")
    driver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="driver_ratings")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} - {self.driver.user.username}"

    class Meta:
        ordering = ['-created_at']