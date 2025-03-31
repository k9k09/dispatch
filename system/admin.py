from django.contrib import admin
from .models import Profile, Motorcycle, RideRequest, Payment, Rating

# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone')
    search_fields = ('user__username', 'phone')
    list_filter = ('user_type',)

# Motorcycle Admin
@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'driver')  # Removed 'color' and 'availability'
    search_fields = ('plate_number', 'driver__user__username')
    list_filter = ()  # Removed 'availability'

# RideRequest Admin
@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'driver', 'status', 'fare', 'created_at')
    search_fields = ('client__user__username', 'driver__user__username')
    list_filter = ('status', 'created_at')

# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('ride', 'amount', 'method', 'timestamp')
    search_fields = ('ride__client__user__username', 'method')
    list_filter = ('method', 'timestamp')

# Rating Admin
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('ride', 'client', 'driver', 'rating', 'created_at')
    search_fields = ('client__user__username', 'driver__user__username')
    list_filter = ('rating', 'created_at')
