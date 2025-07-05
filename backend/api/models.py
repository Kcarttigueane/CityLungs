from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

class Measurement(models.Model):
    location_name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    timestamp = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pressure = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    pm25 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pm10 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    no2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    so2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    co = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    o3 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    aqi = models.IntegerField(null=True, blank=True)
    traffic_level = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True, blank=True
    )
    source = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'measurements'
        indexes = [
            models.Index(fields=['location_name', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

class Prediction(models.Model):
    location_name = models.CharField(max_length=255)
    prediction_timestamp = models.DateTimeField(auto_now_add=True)
    target_timestamp = models.DateTimeField()
    predicted_pm25 = models.DecimalField(max_digits=6, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    model_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'predictions'
        indexes = [
            models.Index(fields=['location_name', 'target_timestamp']),
        ]

class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField()
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'alerts'
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
        ]

class AlertConfig(models.Model):
    parameter = models.CharField(max_length=50)
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    severity = models.CharField(max_length=20)
    is_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'alert_configs'