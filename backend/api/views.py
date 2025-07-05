from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
import requests
from .models import Measurement, Prediction, Alert, AlertConfig
from .serializers import (
    UserSerializer, MeasurementSerializer, 
    PredictionSerializer, AlertSerializer, AlertConfigSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

User = get_user_model()

class RegisterView(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            response.data['user'] = UserSerializer(user).data
        return response

class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['location_name', 'source']
    ordering_fields = ['timestamp', 'pm25', 'aqi']

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest measurements for each location"""
        locations = Measurement.objects.values_list('location_name', flat=True).distinct()
        latest_measurements = []
        
        for location in locations:
            latest = Measurement.objects.filter(
                location_name=location
            ).order_by('-timestamp').first()
            if latest:
                latest_measurements.append(latest)
        
        serializer = self.get_serializer(latest_measurements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get historical data with aggregations"""
        location = request.query_params.get('location', None)
        days = int(request.query_params.get('days', 7))
        
        start_date = timezone.now() - timedelta(days=days)
        queryset = Measurement.objects.filter(timestamp__gte=start_date)
        
        if location:
            queryset = queryset.filter(location_name=location)
        
        # Aggregate by day
        aggregated_data = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_data = queryset.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end
            ).aggregate(
                avg_pm25=Avg('pm25'),
                max_pm25=Max('pm25'),
                min_pm25=Min('pm25'),
                avg_temp=Avg('temperature'),
                avg_humidity=Avg('humidity')
            )
            
            if day_data['avg_pm25']:
                aggregated_data.append({
                    'date': day_start.date(),
                    **day_data
                })
        
        return Response(aggregated_data)

class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['location_name', 'model_name']

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def generate(self, request):
        """Generate new predictions using ML models"""
        location = request.data.get('location_name')
        hours_ahead = request.data.get('hours_ahead', 24)
        
        # Call ML service - try Docker service name first, then localhost
        ml_service_urls = [
            'http://ml_service:5000/predict',  # Docker service name
            'http://localhost:5001/predict'    # Localhost fallback
        ]
        
        response = None
        for url in ml_service_urls:
            try:
                response = requests.post(url, json={
                    'location': location,
                    'hours_ahead': hours_ahead
                }, timeout=30)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                continue
        
        if response and response.status_code == 200:
            prediction_data = response.json()
            
            # Save predictions
            predictions = []
            for pred in prediction_data['predictions']:
                prediction = Prediction.objects.create(
                    location_name=location,
                    target_timestamp=pred['timestamp'],
                    predicted_pm25=pred['pm25'],
                    confidence_score=pred['confidence'],
                    model_name=pred['model']
                )
                predictions.append(prediction)
            
            serializer = self.get_serializer(predictions, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'ML service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['severity', 'is_active', 'alert_type']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role != 'admin':
            # Regular users only see active alerts
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an alert as resolved"""
        alert = self.get_object()
        alert.is_active = False
        alert.resolved_at = timezone.now()
        alert.save()
        return Response({'status': 'resolved'})

class AlertConfigViewSet(viewsets.ModelViewSet):
    queryset = AlertConfig.objects.all()
    serializer_class = AlertConfigSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
