from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.generics import DestroyAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from rest_framework import status, generics
from .utils import generate_otp, send_otp_email, send_otp_phone
from .models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import re
from django.db.models import Q 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

class UserDeletionView(DestroyAPIView):
    serializer_class = UserDeletionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def perform_destroy(self, instance):
        instance.delete()
        return Response({"detail": "Your account has been deleted."}, status=status.HTTP_204_NO_CONTENT)

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

        try:
            user = User.objects.get(Q(email=contact) | Q(phone_number=contact))
        except User.DoesNotExist:
            return Response({'error': 'User with credentials does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if otp=="1234":
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

        #send_otp_email(email, otp)
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



