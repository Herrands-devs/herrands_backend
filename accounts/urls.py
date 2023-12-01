from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static


from .views import EmailTokenObtainPairView, PreferencesDetailView, AgentDataView, UserDeletionView, RegisterView, LoginWithOTP, ValidateOTP, UserDetailView, update_agent_data, AgentRegisterView, AgentUpdateView, ServicesListView, IdtypeListView,PreferencesListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='token_obtain_pair'),
    path('register/agent/', AgentRegisterView.as_view(), name='agent_register'),
    path('update/agent/', AgentUpdateView.as_view(), name='agent_update'),
    path('update/data/', update_agent_data, name='update_agent_data'),
    path('token/obtain/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
    path('validate-otp/', ValidateOTP.as_view(), name='validate-otp'),
    path('me/', UserDetailView.as_view(), name='me'),
    path('agent-details/', AgentDataView.as_view()),
    path('services/', ServicesListView.as_view(), name='services-list'),
    path('preferences/', PreferencesListView.as_view(), name='preferences-list'),
    path('idtypes/', IdtypeListView.as_view(), name='idtypes-list'),
    path('delete-user/', UserDeletionView.as_view(), name='delete-user'),
    path('preferences/<int:id>/', PreferencesDetailView.as_view(), name='preferences-detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)