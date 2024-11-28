from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager

# Base User model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True, default='', unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # User roles
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)  # Flag for doctor users
    is_patient = models.BooleanField(default=False)  # Flag for patient users

    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Hospital Model
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    established_date = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to='hospital_logos/', null=True, blank=True)

    def __str__(self):
        return self.name


# Doctor Model
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name="doctors")
    specialty = models.CharField(max_length=100, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    certifications = models.TextField(null=True, blank=True)
    availability = models.TextField(null=True, blank=True)  # e.g., "Mon-Fri: 9am-5pm"

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


# Patient Model
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    doctors = models.ManyToManyField(Doctor, related_name="patients")  # Patients can be treated by multiple doctors
    medical_history = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# OTP Model
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp')
    otp = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp}"
