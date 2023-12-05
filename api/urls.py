from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ErrandTaskViewSet, UserErrandTaskViewSet, UserCompletedErrandTaskViewSet, CreateErrandView, SubtypeViewSet, VehicleMetricViewSet, DistanceMetricViewSet
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subtypes', SubtypeViewSet, basename='subtype')
router.register(r'errand-tasks', ErrandTaskViewSet)
router.register(r'vehicle-metric', VehicleMetricViewSet)
router.register(r'distance-metric', DistanceMetricViewSet)
router.register(r'errands', UserErrandTaskViewSet, basename='errands')



urlpatterns = [
    path('', include(router.urls)),
    path('create-errand/', CreateErrandView.as_view(), name='create_errand'),
    path('user_errand_tasks/agent_errands/', UserErrandTaskViewSet.as_view({'get': 'agent_errands'}), name='agent_errands'),
    path('user_completed_tasks/agent_errands/', UserCompletedErrandTaskViewSet.as_view({'get': 'agent_errands'}), name='agent_errands'),
    path('user_errand_tasks/customer_errands/', UserErrandTaskViewSet.as_view({'get': 'customer_errands'}), name='customer_errands'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

