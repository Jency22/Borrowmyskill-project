from django.db import models
from django.contrib.auth.models import User


# 🔹 SKILL MODEL (MAIN)
class Skill(models.Model):
    name = models.CharField(max_length=100,default='Default Skill')
    description = models.TextField()
    price = models.IntegerField()
    category = models.CharField(max_length=100,default='General')
    image = models.ImageField(upload_to='skill_images/', null=True, blank=True)

    def __str__(self):
        return self.name


# 🔹 BOOKING MODEL
class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"


# 🔹 REVIEW MODEL (for later use)
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skill.name} - {self.rating}⭐"

# 🔹 FAQ MODEL (FOR CHATBOT)
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question
