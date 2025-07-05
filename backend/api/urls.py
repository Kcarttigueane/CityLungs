from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, CustomTokenObtainPairView,
    MeasurementViewSet, PredictionViewSet,
    AlertViewSet, AlertConfigViewSet
)

router = DefaultRouter()
router.register('measurements', MeasurementViewSet)
router.register('predictions', PredictionViewSet)
router.register('alerts', AlertViewSet)
router.register('alert-configs', AlertConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view({'post': 'register'})),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]