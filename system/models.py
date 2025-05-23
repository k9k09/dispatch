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
        
class Trip(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    ride_type = models.CharField(max_length=50, default='Standard')  # e.g., Standard, Express, Share
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_location} to {self.to_location} - {self.status}"

    class Meta:
        ordering = ['-date', '-time']
        
class Ride(models.Model):
    RIDE_TYPES = (
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('share', 'Share'),
    )
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rider_rides', null=True, blank=True)
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    ride_type = models.CharField(max_length=20, choices=RIDE_TYPES, default='standard')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.from_location} to {self.to_location} - {self.ride_type}"

class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=50)  # e.g., Visa, MasterCard
    last_four = models.CharField(max_length=4)
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_type} ending in {self.last_four}"

    @property
    def icon(self):
        if "visa" in self.card_type.lower():
            return "credit-card"
        elif "mastercard" in self.card_type.lower():
            return "credit-card"
        return "credit-card"  # Default icon

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride_id = models.CharField(max_length=100)  # Link to a ride
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"
    

