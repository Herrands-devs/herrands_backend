from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from .views import (EmailTokenObtainPairView, AgentDetailsAPIView, CustomerDetailsAPIView, AgentListView, CustomerListView,
                     PreferencesDetailView, AgentDataView, UserDeletionView, RegisterView, LoginWithOTP, ValidateOTP,
                       UserDetailView, update_agent_data, AgentRegisterView, AgentUpdateView, ServicesListView, IdtypeListView,
                       PreferencesListView , AdminPermissionView , AdminRegisterView ,
                     AdminUpdateView, UserPermissionsView,UpdateUserView,UserPermissionsByUserIdView,AdminListView,RemoveUserPermissionsView,UpdateUserPermissionsView, AdminDeleteUserView,UserStatsView,ActionsOnUser, LoginWithContact )

urlpatterns = [
    path('register/', RegisterView.as_view(), name='token_obtain_pair'),
    path('register/agent/', AgentRegisterView.as_view(), name='agent_register'),
    path('update/agent/', AgentUpdateView.as_view(), name='agent_update'),
    path('update/data/', update_agent_data, name='update_agent_data'),
    path('token/obtain/', LoginWithContact.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
    path('validate-otp/', ValidateOTP.as_view(), name='validate-otp'),
    path('me/', UserDetailView.as_view(), name='me'),
    path('agent-details/', AgentDataView.as_view()),
    path('services/', ServicesListView.as_view(), name='services-list'),
    path('preferences/', PreferencesListView.as_view(), name='preferences-list'),
    path('idtypes/', IdtypeListView.as_view(), name='idtypes-list'),
    path('delete-user/', UserDeletionView.as_view(), name='delete-user'),
    path('delete-user/<str:user_id>/', AdminDeleteUserView.as_view(), name='delete-user'),
    path('preferences/<int:id>/', PreferencesDetailView.as_view(), name='preferences-detail'),
    path('agents/', AgentListView.as_view(), name='agent-list'),
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('agent/<uuid:user__id>/', AgentDetailsAPIView.as_view(), name='agent-details'),
    path('customer/<uuid:id>/', CustomerDetailsAPIView.as_view(), name='customer-details'),
    path('user-permissions/<uuid:user_id>/', UserPermissionsByUserIdView.as_view(), name='user-permissions-by-id'),
    path('register/admin/',AdminRegisterView.as_view(), name='register-admin'),
    path('update/admin/<uuid:user_id>/', AdminUpdateView.as_view(), name='update-admin'),
    path('manage-admin-permissions/', AdminPermissionView.as_view(), name='manage-admin-perm'),
    path('update-user/', UpdateUserView.as_view(), name='update_admin'),
    path('admin-list/', AdminListView.as_view(), name='admin_list'),
    path('user-monthly-state/', UserStatsView.as_view(), name='user-state'),
    path('action-on-user/<uuid:user_id>/', ActionsOnUser.as_view(), name='action_on_user'),
    path('user-permissions/', UserPermissionsView.as_view(), name='user-permissions'),
    path('update_permissions/<uuid:user_id>/', UpdateUserPermissionsView.as_view(), name='update_permissions'),
    path('remove_permissions/', RemoveUserPermissionsView.as_view(), name='remove_permissions'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)