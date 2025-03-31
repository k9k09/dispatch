from django import forms
from .models import Profile, RideRequest, Rating, Payment

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'phone', 'user_type']
        widgets = {
            'user': forms.TextInput(attrs={'placeholder': 'Username'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'user_type': forms.Select(choices=Profile.USER_TYPES),
        }

class RideRequestForm(forms.ModelForm):
    class Meta:
        model = RideRequest
        fields = ['pickup_location', 'dropoff_location', 'pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude']
        widgets = {
            'pickup_location': forms.TextInput(attrs={'placeholder': 'Pickup Location'}),
            'dropoff_location': forms.TextInput(attrs={'placeholder': 'Dropoff Location'}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'review': forms.Textarea(attrs={'placeholder': 'Write your review here...'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method']
        widgets = {
            'amount': forms.NumberInput(attrs={'placeholder': 'Amount'}),
            'method': forms.Select(choices=Payment.PAYMENT_METHODS),
        }
