from django.contrib import admin
from django.urls import path
from system.views import home, login_view, signup, logout_view  # Importing logout view

urlpatterns = [  
    path('', home, name='home'),  # Adding home URL pattern
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('signup/', signup, name='signup'),  # Correctly linking to the signup view
    path('logout/', logout_view, name='logout'),  # Linking to the logout view
]
