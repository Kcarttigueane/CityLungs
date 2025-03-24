from django.db import models
from django.conf import settings


class EnvironmentalMeasurement(models.Model):
    """Model for storing environmental measurements from various sources."""
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Pollutant measurements
    pm25 = models.FloatField(verbose_name="PM2.5", help_text="Particulate matter 2.5 (μg/m³)", null=True, blank=True)
    pm10 = models.FloatField(verbose_name="PM10", help_text="Particulate matter 10 (μg/m³)", null=True, blank=True)
    o3 = models.FloatField(verbose_name="O3", help_text="Ozone (ppb)", null=True, blank=True)
    no2 = models.FloatField(verbose_name="NO2", help_text="Nitrogen dioxide (ppb)", null=True, blank=True)
    so2 = models.FloatField(verbose_name="SO2", help_text="Sulfur dioxide (ppb)", null=True, blank=True)
    co = models.FloatField(verbose_name="CO", help_text="Carbon monoxide (ppm)", null=True, blank=True)
    
    # Weather data
    temperature = models.FloatField(help_text="Temperature (°C)", null=True, blank=True)
    humidity = models.FloatField(help_text="Relative humidity (%)", null=True, blank=True)
    wind_speed = models.FloatField(help_text="Wind speed (m/s)", null=True, blank=True)
    wind_direction = models.FloatField(help_text="Wind direction (degrees)", null=True, blank=True)
    pressure = models.FloatField(help_text="Atmospheric pressure (hPa)", null=True, blank=True)
    precipitation = models.FloatField(help_text="Precipitation (mm)", null=True, blank=True)
    
    # Traffic data
    traffic_volume = models.IntegerField(help_text="Number of vehicles", null=True, blank=True)
    traffic_speed = models.FloatField(help_text="Average traffic speed (km/h)", null=True, blank=True)
    
    # Source information
    data_source = models.CharField(max_length=100, help_text="Source of the data (API name, sensor ID, etc.)")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.location} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Prediction(models.Model):
    """Model for storing AI predictions."""
    timestamp = models.DateTimeField(auto_now_add=True)
    target_time = models.DateTimeField(help_text="Time for which the prediction is made")
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Predicted values
    predicted_pm25 = models.FloatField(verbose_name="Predicted PM2.5", null=True, blank=True)
    predicted_pm10 = models.FloatField(verbose_name="Predicted PM10", null=True, blank=True)
    predicted_o3 = models.FloatField(verbose_name="Predicted O3", null=True, blank=True)
    predicted_no2 = models.FloatField(verbose_name="Predicted NO2", null=True, blank=True)
    predicted_traffic = models.IntegerField(verbose_name="Predicted traffic volume", null=True, blank=True)
    
    # Model information
    model_name = models.CharField(max_length=100, help_text="Name of the prediction model used")
    model_version = models.CharField(max_length=50, help_text="Version of the prediction model")
    confidence = models.FloatField(help_text="Prediction confidence (0-1)", null=True, blank=True)
    
    class Meta:
        ordering = ['-target_time']
        indexes = [
            models.Index(fields=['target_time']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"Prediction for {self.location} at {self.target_time.strftime('%Y-%m-%d %H:%M')}"


class Alert(models.Model):
    """Model for storing environmental alerts."""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ALERT_TYPES = [
        ('pollution', 'Pollution'),
        ('weather', 'Weather'),
        ('traffic', 'Traffic'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Optional reference to measurement that triggered the alert
    measurement = models.ForeignKey(
        EnvironmentalMeasurement, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='alerts'
    )
    
    # Optional reference to prediction that triggered the alert
    prediction = models.ForeignKey(
        Prediction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='alerts'
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.severity.capitalize()} {self.alert_type} alert: {self.title}"


class UserAlert(models.Model):
    """Model for storing user-specific alert preferences and history."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='user_alerts')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'alert')
        ordering = ['-alert__timestamp']
    
    def __str__(self):
        return f"Alert for {self.user.email}: {self.alert.title}"