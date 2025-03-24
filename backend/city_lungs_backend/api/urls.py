# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EnvironmentalMeasurementViewSet, PredictionViewSet,
    AlertViewSet, UserAlertViewSet, DashboardView
)

app_name = 'api'  # Add namespace to avoid URL name conflicts

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'measurements', EnvironmentalMeasurementViewSet, basename='measurement')
router.register(r'predictions', PredictionViewSet, basename='prediction')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'user-alerts', UserAlertViewSet, basename='user-alert')

urlpatterns = [
    # Include router-generated URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]