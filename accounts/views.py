from django.contrib.auth import get_user_model
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.generics import DestroyAPIView, UpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from rest_framework import status, generics, permissions
from .utils import generate_otp, send_otp_email, send_otp_phone , send_account_creation_mail
from .models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import re
from django.db.models import Q 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, generics, viewsets, pagination
# ----------------------------------------------------------------------------------
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from api.models import ErrandTask, Wallet
from datetime import datetime, timedelta
import json
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .custom_permissions import DeleteUser, DeleteErrands, SuspendUser
# ------------------------------------------------------------------------------------

User = get_user_model()

class UserPermissionsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        specific_permissions = [
            "suspend_user",
            "delete_user",
            "delete_errands",
            "cancel_errands",
            "cancel_payout",
            "delete_payout",
            "manage_support",
            "add_new_admin",
        ]

        user_permissions = {str(perm).split('.')[-1].strip() for perm in user.user_permissions.all()}

        all_perm = [{'title': perm, 'status': perm in user_permissions} for perm in specific_permissions]

        return Response({'permissions': all_perm})

       

        
        return Response({'permissions': all_perm})


    
'''class UserPermissionsByUserIdView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        # Define a list of specific permission titles
        specific_permissions = [
            "suspend_user",
            "delete_user",
            "delete_errands",
            "cancel_errands",
            "cancel_payout",
            "delete_payout",
            "manage_support",
            "add_new_admin",
        ]

        # Fetch user's permissions
        user_permissions = user.user_permissions.values_list('codename', flat=True)

        # Create a list of dictionaries with title and status
        permissions = [
            {
                'title': title,
                'status': title in user_permissions
            }
            for title in specific_permissions
        ]

        return Response({'permissions': permissions})'''

class UserPermissionsByUserIdView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        specific_permissions = [
            "suspend_user",
            "delete_user",
            "delete_errands",
            "cancel_errands",
            "cancel_payout",
            "delete_payout",
            "manage_support",
            "add_new_admin",
        ]

        user_permissions = {str(perm).split('.')[-1].strip() for perm in user.user_permissions.all()}

        all_perm = [{'title': perm, 'status': perm in user_permissions} for perm in specific_permissions]

        return Response({'permissions': all_perm})
    
class UpdateUserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        permissions_to_update = [
            'delete_user', 'suspend_user', 'delete_errands',
            'cancel_errands', 'cancel_payout', 'delete_payout',
            'manage_support', 'add_new_admin',
        ]

        for permission_name in permissions_to_update:
            permission_codename = f'accounts.{permission_name}'
            value = serializer.validated_data.get(permission_name, False)

            try:
                permission = Permission.objects.get(codename=permission_codename)

                if value and permission not in user.user_permissions.all():
                    user.user_permissions.add(permission)
                elif not value and permission in user.user_permissions.all():
                    user.user_permissions.remove(permission)

            except Permission.DoesNotExist:
                # Handle the case where the permission doesn't exist if needed
                pass

        return Response(status=status.HTTP_200_OK)




class PermissionSerializer(serializers.Serializer):
    title = serializers.CharField()
    status = serializers.BooleanField()

class LoginWithContact(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        password = request.data.get('password', '')

        try:
            #user = User.objects.get(Q(email=contact) | Q(phone_number=contact))
            user = User.objects.get(email=email)
            print(user.user_type)
        except User.DoesNotExist:
            return Response({'error': 'User with credentials does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        param = ['Admin', 'admin']
        if user.user_type not in param:
            return Response({'error':'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if user.check_password(password):
            #user.otp = None  # Reset the OTP field after successful validation
            #user.save()
            

            # Generate a new JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            #user_obj = Farmer.objects.get(email=user.email)
            user_seri = UserSerializer(user)
           
            return Response({'token': access_token, 'user': user_seri.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Password.'}, status=status.HTTP_400_BAD_REQUEST)

class ActionsOnUser(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request,user_id, *args, **kwargs):
        try:
            print(user_id)
            action = request.data.get('action')
            user_instance = User.objects.get(id=user_id)
            user_instance.status = action
            user_instance.save()
            return Response({'detail':f'{user_instance.email} {action} successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class PermissionUpdateSerializer(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.CharField())

class PermissionUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PermissionUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'user_id'  # Change to the actual lookup field you are using

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the list of permissions from the request data
        permissions_to_add = serializer.validated_data.get('permissions', [])

        # Add permissions to the user
        user_permissions = Permission.objects.filter(codename__in=permissions_to_add)
        instance.user_permissions.add(*user_permissions)

        return Response({'message': 'Permissions added successfully'}) 

class PermissionSerializer(serializers.Serializer):
    delete_user = serializers.BooleanField(required=False)
    suspend_user = serializers.BooleanField(required=False)
    delete_errands = serializers.BooleanField(required=False)
    cancel_errands = serializers.BooleanField(required=False)
    cancel_payout = serializers.BooleanField(required=False)
    delete_payout = serializers.BooleanField(required=False)
    manage_support = serializers.BooleanField(required=False)
    add_new_admin = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        # Loop through the validated_data and update the corresponding fields in the instance
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the instance to persist the changes
        instance.save()

        return instance


    
class UpdateUserPermissionsView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserPermissionsSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Update user permissions based on the provided data
        user = instance
        if serializer.validated_data.get('delete_user'):
            user.user_permissions.add(DeleteUser.get_permission())
        else:
            user.user_permissions.remove(DeleteUser.get_permission())

        if serializer.validated_data.get('suspend_user'):
            user.user_permissions.add(SuspendUser.get_permission())
        else:
            user.user_permissions.remove(SuspendUser.get_permission())

        if serializer.validated_data.get('delete_errands'):
            user.user_permissions.add(DeleteErrands.get_permission())
        else:
            user.user_permissions.remove(DeleteErrands.get_permission())

        user.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        try:
            current_month_agent_count = User.objects.filter(
                user_type='Agent',
                date_joined__year=current_month.year,
                date_joined__month=current_month.month
            ).count()
            last_month_agent_count = User.objects.filter(
                user_type='Agent',
                date_joined__year=last_month.year,
                date_joined__month=last_month.month
            ).count()
            current_month_customer_count = User.objects.filter(
                user_type='Customer',
                date_joined__year=current_month.year,
                date_joined__month=current_month.month
            ).count()
            last_month_customer_count = User.objects.filter(
                user_type='Customer',
                date_joined__year=last_month.year,
                date_joined__month=last_month.month
            ).count()
            print(current_month_agent_count,last_month_agent_count,current_month_customer_count,last_month_customer_count)
            agent_percentage_change = ((current_month_agent_count - last_month_agent_count) / last_month_agent_count) * 100
            customer_percentage_change = ((current_month_customer_count - last_month_customer_count) / last_month_customer_count) * 100

        except ZeroDivisionError:
            customer_percentage_change = 0
            agent_percentage_change = 0

        context = {
            'current_month_agent_count': current_month_agent_count,
            'agent_percentage_change': round(agent_percentage_change, 2),
            'current_month_customer_count': current_month_customer_count,
            'customer_percentage_change': round(customer_percentage_change, 2)
        }
        return Response(context, status=status.HTTP_200_OK)


class AdminRegisterView(APIView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
            mutable_data = request.data.copy()
            mutable_data['user_type'] = 'Admin'
            serializer = UserSerializer(data=mutable_data)
            if serializer.is_valid():
                user = get_user_model().objects.create_user(**serializer.validated_data)
                message = 'User created successfully.'
                serialized_user = UserSerializer(user)  # Serialize the user instance
                user_data = serialized_user.data
                send_account_creation_mail(user_data.get("id"), user_data.get("email"))
                return Response(status=HTTP_201_CREATED, data={'message': message, 'user': user_data})
            first_field = next(iter(serializer.errors))
            first_error = next(iter(serializer.errors.values()))[0]
            return Response(status=HTTP_400_BAD_REQUEST, data={first_field: first_error})
        except Exception as e:
            return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AdminUpdateView(APIView):
    http_method_names = ['put']

    def put(self, request, user_id, *args, **kwargs):
        try:
            user_instance = get_user_model().objects.get(pk=user_id, user_type='Admin')
            serializer = UserSerializer2(instance=user_instance, data=request.data, partial=True)
            #user_instance = self.get_object()
            if serializer.is_valid():
                user_password = make_password(serializer.validated_data['password'])
                serializer.save(password=user_password, account_completed=True)
                message = 'Admin user updated successfully.'
                serialized_user = UserSerializer(serializer.instance)  # Serialize the updated user instance
                return Response(data={'message': message, 'user': serialized_user.data})

            # Handle validation errors
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        except get_user_model().DoesNotExist:
            return Response({'detail': 'Admin user not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
'''class AgentUpdateView(viewsets.ModelViewSet):
    queryset =  User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['PATCH'])
    def update_farmer_number(self, request, pk=None):
        farmer_instance = self.get_object()
        serializer = FarmerUpdateSerializerOne(farmer_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Phone number added successfully", "data": serializer.data})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['PATCH'])
    def update_farmer_photo(self, request, pk=None):
        farmer_instance = self.get_object()
        serializer = FarmerUpdateSerializerTwo(farmer_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Photo added successfully", "data": serializer.data})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['PATCH'])
    def update_password(self, request, pk=None):
        farmer_instance = self.get_object()
        serializer = FarmerUpdateSerializerThree(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Set the new password
            farmer_instance.set_password(serializer.validated_data['password'])
            farmer_instance.save()
            return Response({"message": "Password updated successfully"})
        return Response(serializer.errors, status=400)'''

class UpdateUserView(UpdateAPIView):
    serializer_class = AgentUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class AdminPermissionView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Check if the user making the request is a superuser
            if not request.user.is_superuser:
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

            # Extract user_id and permissions from the request data
            user_id = request.data.get('user_id')
            print(user_id)
            permission_codenames = request.data.get('permissions')
            print(permission_codenames)
            try:
                user = get_user_model().objects.get(pk=user_id)
            except get_user_model().DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            # Set the user's permissions
            user.user_permissions.clear()
            for codename in list(permission_codenames):
                try:
                    model_name = self.get_model_name(codename)
                    content_type = ContentType.objects.get_for_model(model_name)
                    permission = Permission.objects.get(codename=codename , content_type=content_type)
                except Permission.DoesNotExist:
                    permission = Permission.objects.create(
                        codename=codename,
                        content_type=content_type,
                        name=codename,
                    )
                user.user_permissions.add(permission)

            return Response({'detail': 'Permissions updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_model_name(self,codename):
        if codename in ['suspend_user', 'delete_user', 'add_new_admin', 'manage_support']:
            return get_user_model()
        elif codename in ['delete_errands', 'cancel_errands']:
            return ErrandTask
        elif codename in ['cancel_payout', 'delete_payout']:    
            return Wallet
        else:
            return get_user_model()

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # Set the number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdminListView(generics.ListAPIView):
    queryset = User.objects.filter(user_type='Admin')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPageNumberPagination  

    def get(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AgentListView(generics.ListAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination  # Use your custom pagination class

    def get(self, request, *args, **kwargs):
        # Use the pagination class to get the paginated response
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CustomerListView(generics.ListAPIView):
    queryset = User.objects.filter(user_type='Customer')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPageNumberPagination  # Use your custom pagination class

    def get(self, request, *args, **kwargs):
        # Use the pagination class to get the paginated response
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserDeletionView(DestroyAPIView):
    serializer_class = UserDeletionSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.request.user
    
    def perform_destroy(self, instance):
        instance.delete()
        return Response({"detail": "Your account has been deleted."}, status=status.HTTP_204_NO_CONTENT)

class AdminDeleteUserView(DestroyAPIView):
    serializer_class = UserDeletionSerializer
    permission_classes = [IsAuthenticated | (IsAdminUser & DeleteUser)]

    def get_object(self):
        user_id = self.kwargs.get('user_id')  
        return User.objects.get(id=user_id)

    def perform_destroy(self, instance):
        instance.delete()
        return Response({"detail": "User has been deleted."}, status=status.HTTP_204_NO_CONTENT)

'''class ValidateOTP(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        otp = request.data.get('otp', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp:
            user.otp = None  # Reset the OTP field after successful validation
            user.save()

            # Authenticate the user and create or get an authentication token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)'''

class ValidateOTP(APIView):
    def post(self, request):
        contact = request.data.get('contact', '')
        otp = request.data.get('otp', '')
        print(contact,otp)
        try:
            user = User.objects.get(Q(email=contact) | Q(phone_number=contact))
        except User.DoesNotExist:
            return Response({'error': 'User with credentials does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if otp=='1234':
            user.otp = None  # Reset the OTP field after successful validation
            user.save()

            # Generate a new JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            user_seri = UserSerializer(user)

            return Response({'token': access_token, 'user': user_seri.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

class LoginWithOTP(APIView):
    def post(self, request):
        #email = request.data.get('email', '')
        contact = request.data.get('contact', '')
        print(contact)
        try:
            user = User.objects.get(Q(email=contact) | Q(phone_number=contact))
        except User.DoesNotExist:
            return Response({'error': 'User with this credential does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        '''try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)'''

        otp = generate_otp()
        print(otp)
        print(user)
        user.otp = otp
        user.save()
        print(user.otp)

        send_otp_email(contact, otp)
        print('sent')
        # send_otp_phone(phone_number, otp)
        '''if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', contact):
            # Send OTP via email
            send_otp_email(contact, otp)
        else:
            # Assuming you have a function send_otp_phone that sends OTP via SMS
            send_otp_phone(contact, otp)'''


        return Response({'message': 'OTP has been sent.'}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = get_user_model().objects.create_user(**serializer.validated_data)
            message = 'User created successfully.'
            serialized_user = UserSerializer(user)  # Serialize the user instance
            return Response(status=HTTP_201_CREATED, data={'message': message, 'user': serialized_user.data})
        first_field = next(iter(serializer.errors))
        first_error = next(iter(serializer.errors.values()))[0]
        return Response(status=HTTP_400_BAD_REQUEST, data={first_field: first_error})





class AgentRegisterView(generics.CreateAPIView):
    serializer_class = AgentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance.user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        response_data = serializer.data.copy()
        response_data['access_token'] = access_token
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


        
class AgentDataView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        if user.user_type=="Agent":
            try:
                agent = Agent.objects.get(user=user)
                serializer = AgentSerializer(agent, context={'request': request})
            except Agent.DoesNotExist:
                return Response({'error': 'Agent data not found.'}, status=status.HTTP_404_NOT_FOUND)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'User is not an agent.'}, status=status.HTTP_400_BAD_REQUEST)

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        # Use self.request.user to get the currently authenticated user
        return self.request.user
    
    def get_serializer_context(self):
        # Set the 'agent_representation' key in the context if user_type is 'Agent'
        context = super().get_serializer_context()
        if self.request.user.user_type == 'Agent':
            context['agent_representation'] = True
        return context

class ServicesListView(generics.ListAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer

class PreferencesListView(generics.ListAPIView):
    queryset = Preferences.objects.all()
    serializer_class = PreferencesSerializer

class PreferencesDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Preferences.objects.all()
    serializer_class = PreferencesSerializer
    lookup_field = 'id' 

class IdtypeListView(generics.ListAPIView):
    queryset = Idtype.objects.all()
    serializer_class = IdtypeSerializer

class AgentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_agent_data(request):
    # Retrieve the authenticated user
    user = request.user

    # Retrieve the agent instance associated with the user, if any
    #agent_instance = Agent.objects.get(user=user)
    agent_instance, created = Agent.objects.get_or_create(user=user)

    if agent_instance:
        # Initialize the serializer with the agent instance and request data
        serializer = AgentUpdateSerializer(instance=agent_instance, data=request.data, partial=True)

        # Validate and save the serializer data
        if serializer.is_valid():
            serializer.save()
            user.account_completed = True
            user.save()
            print(user.account_completed)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'User is not associated with an agent.'}, status=status.HTTP_404_NOT_FOUND)


class AgentDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user__id'

    def perform_destroy(self, instance):
        user = instance.user
        user.delete()

class CustomerDetailsAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
# ----------------------------------------------------------
    
class UpdateUserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        permissions_to_update = [
            'delete_user', 'suspend_user', 'delete_errands',
            'cancel_errands', 'cancel_payout', 'delete_payout',
            'manage_support', 'add_new_admin',
        ]

        for permission_name in permissions_to_update:
            permission_codename = f'accounts.{permission_name}'
            value = serializer.validated_data.get(permission_name, False)

            try:
                permission = Permission.objects.get(codename=permission_codename)

                if value and permission not in user.user_permissions.all():
                    user.user_permissions.add(permission)
                elif not value and permission in user.user_permissions.all():
                    user.user_permissions.remove(permission)

            except Permission.DoesNotExist:
                # Handle the case where the permission doesn't exist if needed
                pass

        return Response(status=status.HTTP_200_OK)
    
class RemoveUserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = RemoveUserPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        permissions_to_remove = serializer.validated_data['permissions_to_remove']

        for permission_codename in permissions_to_remove:
            try:
                permission = Permission.objects.get(codename=permission_codename)
                user.user_permissions.remove(permission)
            except Permission.DoesNotExist:
                # Handle the case where the permission doesn't exist if needed
                pass

        return Response(status=status.HTTP_200_OK)