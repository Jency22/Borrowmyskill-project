from django.urls import path
from core.views import (
    home, login, register, logout_view, dashboard, profile_view, 
    my_bookings, booking, payment, payment_success, review_booking, 
    chatbot_api
)

urlpatterns = [
    path('', home, name='home'),

    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('my-bookings/', my_bookings, name='my_bookings'),

    path('booking/<int:skill_id>/', booking, name='booking'),
    path('payment/<int:booking_id>/', payment, name='payment'),
    
    path('payment-success/<int:booking_id>/', payment_success, name='payment_success'),
    path('review/<int:booking_id>/', review_booking, name='review_booking'),
    
    # API endpoints
    path('api/chatbot/', chatbot_api, name='chatbot_api'),
]