from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import(CancelErrandsView, PaymentListView,ErrandStatsView, AgentRatingView,SelectPaymentMethod,WithdrawApi,confirm_payment_view,MakePayment, CategoryViewSet,AdminTopAgentsView,
                    WithdrawalView, AdminErrandsComparisonView, AdminTopCustomersView, AdminErrandTaskViewSet,
                    CustomerConversationsView, AgentConversationsView, EarningsListView, WalletView,
                    ConversationListAPIView, ErrandTaskViewSet, UserErrandTaskViewSet, UserCompletedErrandTaskViewSet,
                    CreateErrandView, SubtypeViewSet, VehicleMetricViewSet, DistanceMetricViewSet,
                    WithdrawalHistoryView , AdminErrandTaskDeleteAPIView, AllSubtypesViewSet)
from django.conf import settings
from django.conf.urls.static import static
from . import views


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subtypes', SubtypeViewSet, basename='subtype')
router.register(r'all-subtypes', AllSubtypesViewSet, basename='all-subtypes')
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
    path('rate-agent/', AgentRatingView.as_view(), name='rate-agent'),
    # -----------------
    path('select-payment-method/<uuid:id>/', SelectPaymentMethod.as_view(), name='select_payment_method'),
    path('errand-initiate-payment/', MakePayment.as_view(), name='errand-pay'),
    path('errand-initiate-payment/confirm_payment/', confirm_payment_view, name='confirm_payment'),
    path('withdraw/', WithdrawApi.as_view(), name='withdraw'),
    path('withdraw-history-list/', WithdrawalHistoryView.as_view(), name='withdraw_history'),
    path('errand-monthly-state/', ErrandStatsView.as_view(), name='errand_state'),
    path('payment-list/', PaymentListView.as_view(), name='payment_list'),
    path('cancel-errand/<uuid:errand_id>/', CancelErrandsView.as_view(), name='cancel_errand'),
    path('delete-errand-task/<str:pk>/', AdminErrandTaskDeleteAPIView.as_view(), name='delete-errand-task'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)