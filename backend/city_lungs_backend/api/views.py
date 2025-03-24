from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import EnvironmentalMeasurement, Prediction, Alert, UserAlert
from .serializers import (
    EnvironmentalMeasurementSerializer, PredictionSerializer,
    AlertSerializer, UserAlertSerializer, DashboardSerializer
)
from user_auth.permission import IsAdmin, IsAdminOrReadOnly


class EnvironmentalMeasurementViewSet(viewsets.ModelViewSet):
    """
    API endpoints for environmental measurements.
    
    list:
    Return a list of all environmental measurements, optionally filtered by location, date range, or data source.
    
    create:
    Create a new environmental measurement (admin only).
    
    retrieve:
    Return the specified environmental measurement.
    
    update:
    Update the specified environmental measurement (admin only).
    
    partial_update:
    Partially update the specified environmental measurement (admin only).
    
    destroy:
    Delete the specified environmental measurement (admin only).
    """
    queryset = EnvironmentalMeasurement.objects.all()
    serializer_class = EnvironmentalMeasurementSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('location', openapi.IN_QUERY, description="Filter by location name", type=openapi.TYPE_STRING),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('source', openapi.IN_QUERY, description="Filter by data source", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Return a list of all measurements with optional filtering."""
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        Optionally filter by location, date range, or data source.
        """
        queryset = super().get_queryset()

        # Filter by location if provided
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        if source := self.request.query_params.get('source', None):
            queryset = queryset.filter(data_source__icontains=source)

        return queryset


class PredictionViewSet(viewsets.ModelViewSet):
    """
    API endpoints for AI predictions.
    
    list:
    Return a list of all predictions, optionally filtered by location, target date range, or model.
    
    create:
    Create a new prediction (admin only).
    
    retrieve:
    Return the specified prediction.
    
    update:
    Update the specified prediction (admin only).
    
    partial_update:
    Partially update the specified prediction (admin only).
    
    destroy:
    Delete the specified prediction (admin only).
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('location', openapi.IN_QUERY, description="Filter by location name", type=openapi.TYPE_STRING),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Filter by target start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Filter by target end date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('model', openapi.IN_QUERY, description="Filter by model name", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Return a list of all predictions with optional filtering."""
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        Optionally filter by location, target date range, or model.
        """
        queryset = super().get_queryset()

        if location := self.request.query_params.get('location', None):
            queryset = queryset.filter(location__icontains=location)

        # Filter by target date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            queryset = queryset.filter(target_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(target_time__lte=end_date)

        if model := self.request.query_params.get('model', None):
            queryset = queryset.filter(model_name__icontains=model)

        return queryset


class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoints for environmental alerts.
    
    list:
    Return a list of all alerts, optionally filtered by location, type, severity, or active status.
    
    create:
    Create a new alert (admin only).
    
    retrieve:
    Return the specified alert.
    
    update:
    Update the specified alert (admin only).
    
    partial_update:
    Partially update the specified alert (admin only).
    
    destroy:
    Delete the specified alert (admin only).
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('location', openapi.IN_QUERY, description="Filter by location name", type=openapi.TYPE_STRING),
            openapi.Parameter('type', openapi.IN_QUERY, description="Filter by alert type (pollution, weather, traffic)", type=openapi.TYPE_STRING),
            openapi.Parameter('severity', openapi.IN_QUERY, description="Filter by severity (low, medium, high, critical)", type=openapi.TYPE_STRING),
            openapi.Parameter('active', openapi.IN_QUERY, description="Filter by active status (true/false)", type=openapi.TYPE_BOOLEAN),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Return a list of all alerts with optional filtering."""
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        Optionally filter by location, type, severity, or active status.
        """
        queryset = super().get_queryset()

        if location := self.request.query_params.get('location', None):
            queryset = queryset.filter(location__icontains=location)

        if alert_type := self.request.query_params.get('type', None):
            queryset = queryset.filter(alert_type=alert_type)

        if severity := self.request.query_params.get('severity', None):
            queryset = queryset.filter(severity=severity)

        # Filter by active status if provided
        active = self.request.query_params.get('active', None)
        if active is not None:
            is_active = active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)

        return queryset


class UserAlertViewSet(viewsets.ModelViewSet):
    """
    API endpoints for user-specific alerts.
    
    list:
    Return a list of the authenticated user's alerts.
    
    create:
    Create a new user alert for the authenticated user.
    
    retrieve:
    Return the specified user alert.
    
    update:
    Update the specified user alert.
    
    partial_update:
    Partially update the specified user alert.
    
    destroy:
    Delete the specified user alert.
    
    mark_as_read:
    Mark a specific user alert as read.
    
    mark_all_as_read:
    Mark all user alerts as read.
    """
    serializer_class = UserAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only the user's own alerts.
        """
        return UserAlert.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Mark a specific user alert as read",
        responses={
            200: UserAlertSerializer,
            404: "Alert not found"
        }
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a user alert as read.
        """
        user_alert = self.get_object()
        user_alert.is_read = True
        user_alert.read_at = timezone.now()
        user_alert.save()
        
        serializer = self.get_serializer(user_alert)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Mark all user alerts as read",
        responses={
            200: openapi.Response(
                description="All alerts marked as read",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all user alerts as read.
        """
        queryset = self.get_queryset().filter(is_read=False)
        now = timezone.now()
        
        # Update all unread alerts
        queryset.update(is_read=True, read_at=now)
        
        return Response({'status': 'All alerts marked as read'})


class DashboardView(APIView):
    """
    API endpoint for the dashboard, which combines data from multiple sources.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get combined dashboard data including measurements, predictions, and alerts",
        manual_parameters=[
            openapi.Parameter('location', openapi.IN_QUERY, description="Filter by location name", type=openapi.TYPE_STRING),
        ],
        responses={
            200: DashboardSerializer,
            401: "Authentication credentials were not provided"
        }
    )
    def get(self, request):
        """
        Return a combination of latest measurements, predictions, and alerts.
        """
        # Get location filter if provided
        location = request.query_params.get('location', None)
        location_filter = Q(location__icontains=location) if location else Q()
        
        # Get latest measurements
        measurements = EnvironmentalMeasurement.objects.filter(
            location_filter
        ).order_by('-timestamp')[:10]
        
        # Get upcoming predictions
        predictions = Prediction.objects.filter(
            location_filter,
            target_time__gte=timezone.now()
        ).order_by('target_time')[:10]
        
        # Get active alerts
        active_alerts = Alert.objects.filter(
            location_filter,
            is_active=True
        ).order_by('-severity', '-timestamp')[:10]
        
        # Get user alerts
        user_alerts = UserAlert.objects.filter(
            user=request.user
        ).order_by('-alert__timestamp')[:10]
        
        # Combine the data
        dashboard_data = {
            'latest_measurements': EnvironmentalMeasurementSerializer(measurements, many=True).data,
            'predictions': PredictionSerializer(predictions, many=True).data,
            'active_alerts': AlertSerializer(active_alerts, many=True).data,
            'user_alerts': UserAlertSerializer(user_alerts, many=True).data,
        }
        
        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data)