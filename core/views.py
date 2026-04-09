from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import razorpay
import json
from django.conf import settings
from core.models import Skill, Booking, Review
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.conf import settings



# HOME
def home(request):
    skills = Skill.objects.all()
    return render(request, 'home.html', {'skills': skills})


# LOGIN
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# REGISTER
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        User.objects.create_user(username=username, password=password)
        return redirect('/login/')

    return render(request, 'register.html')


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def dashboard(request):
    skills = Skill.objects.all()

    # SEARCH
    q = request.GET.get('q')
    if q:
        skills = skills.filter(name__icontains=q)

    # CATEGORY
    category = request.GET.get('category')
    if category:
        skills = skills.filter(category=category)

    # PRICE
    price = request.GET.get('price')
    if price == 'low':
        skills = skills.filter(price__lt=500)
    elif price == 'mid':
        skills = skills.filter(price__gte=500, price__lte=2000)
    elif price == 'high':
        skills = skills.filter(price__gt=2000)

    # SAFE BOOKINGS
    if request.user.is_authenticated:
        bookings = Booking.objects.filter(user=request.user)
    else:
        bookings = []

    return render(request, 'dashboard.html', {
        'skills': skills,
        'bookings': bookings
    })

@login_required
def profile_view(request):
    return render(request, 'profile.html')

# BOOKING (🔥 FULLY WORKING)
def booking(request, skill_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    skill = Skill.objects.get(id=skill_id)

    if request.method == "POST":
        date = request.POST.get("date")
        time = request.POST.get("time")

        booking = Booking.objects.create(
            user=request.user,
            skill=skill,
            date=date,
            time=time
        )

        return redirect('payment', booking_id=booking.id)

    return render(request, 'booking.html', {'skill': skill})


# MY BOOKINGS PAGE
def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    bookings = Booking.objects.filter(user=request.user)

    return render(request, 'my_bookings.html', {'bookings': bookings})
def payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    if request.method == "POST":
        booking.status = "Confirmed"
        booking.save()

        return redirect('payment_success', booking_id=booking.id)

    # Convert amount to paise for Razorpay
    amount = int(booking.skill.price * 100)

    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay Order
    payment_data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_rcptid_{booking.id}",
    }
    
    razorpay_order = client.order.create(data=payment_data)
    razorpay_order_id = razorpay_order['id']

    context = {
        'booking': booking,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': amount,
        'currency': 'INR'
    }

    return render(request, 'payment.html', context)

# PAYMENT SUCCESS PAGE
def payment_success(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return render(request, 'payment_success.html', {'booking': booking})

# REVIEW VIEW
def review_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        Review.objects.create(
            user=request.user,
            skill=booking.skill,
            rating=rating,
            comment=comment
        )
        # Booking could be marked as "Reviewed" logically or just returned
        return redirect('my_bookings')
        
    return render(request, 'review_booking.html', {'booking': booking})


def get_skills_data():
    skills = Skill.objects.all()

    data = ""
    for skill in skills:
        data += f"{skill.title} - ₹{skill.price}. {skill.description}\n"

    return data
from core.models import Skill, FAQ

def chatbot_reply(user_message):
    msg = user_message.lower()

    # 🔍 Search in FAQ database first
    faqs = FAQ.objects.all()
    for faq in faqs:
        if faq.question.lower() in msg or msg in faq.question.lower():
            return faq.answer

    # 🔍 Search in title (or name)
    skills = Skill.objects.filter(name__icontains=msg)

    # 🔍 Also search in description
    if not skills:
        skills = Skill.objects.filter(description__icontains=msg)

    # ✅ If skills found
    if skills.exists():
        reply = "Here are some skills I found:\n\n"
        for skill in skills[:5]:
            reply += f"{skill.name} - ₹{skill.price}\n"
        return reply

    # 💬 General responses fallback
    if "hi" in msg or "hello" in msg:
        return "Hi 👋 How can I help you today?"

    elif "book" in msg:
        return "You can book a skill by clicking the 'Book Now' button."

    elif "price" in msg:
        return "Prices depend on the skill. You can check each skill card."

    elif "categories" in msg:
        return "We offer Cooking, Music, Fitness, Repair, Education and more."

    else:
        return "Sorry, I couldn't find an answer to that. Try asking about specific skills like 'cooking' or 'python'."
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        message = request.POST.get("message")
        reply = chatbot_reply(message)
        return JsonResponse({"reply": reply})