from rest_framework import serializers
from .models import EnvironmentalMeasurement, Prediction, Alert, UserAlert


class EnvironmentalMeasurementSerializer(serializers.ModelSerializer):
    """Serializer for environmental measurements."""
    
    class Meta:
        model = EnvironmentalMeasurement
        fields = '__all__'


class PredictionSerializer(serializers.ModelSerializer):
    """Serializer for AI predictions."""
    
    class Meta:
        model = Prediction
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for environmental alerts."""
    
    class Meta:
        model = Alert
        fields = '__all__'


class UserAlertSerializer(serializers.ModelSerializer):
    """Serializer for user-specific alerts."""
    alert = AlertSerializer(read_only=True)
    
    class Meta:
        model = UserAlert
        fields = ['id', 'user', 'alert', 'is_read', 'read_at']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        """Create a user alert with the current user."""
        # Get the user from the context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DashboardSerializer(serializers.Serializer):
    """
    Serializer for the dashboard data, which combines measurements, predictions, and alerts
    into a single API response.
    """
    latest_measurements = EnvironmentalMeasurementSerializer(many=True)
    predictions = PredictionSerializer(many=True)
    active_alerts = AlertSerializer(many=True)
    user_alerts = UserAlertSerializer(many=True)