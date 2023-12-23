from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet,AdminTopAgentsView, WithdrawalView, AdminErrandsComparisonView, AdminTopCustomersView, AdminErrandTaskViewSet, CustomerConversationsView, AgentConversationsView, EarningsListView, WalletView, ConversationListAPIView, ErrandTaskViewSet, UserErrandTaskViewSet, UserCompletedErrandTaskViewSet, CreateErrandView, SubtypeViewSet, VehicleMetricViewSet, DistanceMetricViewSet
from django.conf import settings
from django.conf.urls.static import static
from . import views


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subtypes', SubtypeViewSet, basename='subtype')
router.register(r'errand-tasks', ErrandTaskViewSet)
router.register(r'admin-errand-tasks', AdminErrandTaskViewSet)
router.register(r'vehicle-metric', VehicleMetricViewSet)
router.register(r'distance-metric', DistanceMetricViewSet)
router.register(r'errands', UserErrandTaskViewSet, basename='errands')



urlpatterns = [
    path('', include(router.urls)),
    path('conversations/<str:room_name>/', ConversationListAPIView.as_view(), name='conversation-list'),
    path('create-errand/', CreateErrandView.as_view(), name='create_errand'),
    path('user_errand_tasks/agent_errands/', UserErrandTaskViewSet.as_view({'get': 'agent_errands'}), name='agent_errands'),
    path('user_completed_tasks/agent_errands/', UserCompletedErrandTaskViewSet.as_view({'get': 'agent_errands'}), name='agent_errands'),
    path('user_errand_tasks/customer_errands/', UserErrandTaskViewSet.as_view({'get': 'customer_errands'}), name='customer_errands'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('earnings/', EarningsListView.as_view(), name='earnings-list'),
    path('withdrawals/', WithdrawalView.as_view(), name='withdrawals-list'),
    path('<int:convo_id>/', views.get_conversation, name='get_conversation'),
    path('agent-conversations', AgentConversationsView.as_view(), name='agent-conversations'),
    path('customer-conversations', CustomerConversationsView.as_view(), name='customer-conversations'),
    path('top-customers/', AdminTopCustomersView.as_view(), name='top-customers'),
    path('top-agents/', AdminTopAgentsView.as_view(), name='top-agents'),
    path('errands-dashboard/', AdminErrandsComparisonView.as_view(), name='errands-comparison'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)