from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, TokenObtainPairSerializer
from rest_framework import status
from .utils import generate_otp, send_otp_email, send_otp_phone
from .models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import re
from django.db.models import Q 
from rest_framework_simplejwt.tokens import RefreshToken

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

        if user.otp == otp:
            user.otp = None  # Reset the OTP field after successful validation
            user.save()

            # Generate a new JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({'token': access_token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

class LoginWithOTP(APIView):
    def post(self, request):
        #email = request.data.get('email', '')
        contact = request.data.get('contact', '')
        try:
            user = User.objects.get(Q(email=contact) | Q(phone_number=contact))
        except User.DoesNotExist:
            return Response({'error': 'User with this credentials does not exist.'}, status=status.HTTP_404_NOT_FOUND)
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
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', contact):
            # Send OTP via email
            send_otp_email(contact, otp)
        else:
            # Assuming you have a function send_otp_phone that sends OTP via SMS
            send_otp_phone(contact, otp)


        return Response({'message': 'OTP has been sent.'}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    http_method_names = ['post']

    def post(self, *args, **kwargs):
        serializer = UserSerializer(data=self.request.data)
        if serializer.is_valid():
            user = get_user_model().objects.create_user(**serializer.validated_data)
            message = 'User created successfully.'
            return Response(status=HTTP_201_CREATED, data={'message': message, 'user_id': user.id})
        return Response(status=HTTP_400_BAD_REQUEST, data={'errors': serializer.errors})


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer