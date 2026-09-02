from django.urls import path
from . import views

urlpatterns = [
    path('login/',        views.login,        name='login'),
    path('register/',     views.register,     name='register'),
    path('destinations/', views.destinations, name='destinations'),
    path('packages/',     views.packages,     name='packages'),
    path('bookings/',     views.bookings,     name='bookings'),
    path('reviews/',      views.reviews,      name='reviews'),
    path('recommend/',    views.ai_recommend, name='recommend'),
]