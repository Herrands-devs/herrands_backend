from rest_framework import viewsets, pagination
from .models import Category, Wallet, Withdrawals, ErrandTask, Subtype, VehicleMetric, DistanceMetric, Conversation, Message 
from .serializers import *
from rest_framework import generics
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from django.db.models import Max
from rest_framework.decorators import api_view
from .serializers import ConversationListSerializer, ConversationSerializer, WithdrawSerializer
from django.db.models import Q
from django.shortcuts import redirect, reverse
from accounts.serializers import *
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from rest_framework.mixins import DestroyModelMixin
# --------------------------------------------------------------------------------------------
from django.http import JsonResponse
import uuid
import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment as Payments
from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime, timedelta



class CancelErrandsView(APIView):
    http_method_names = ['post']

    def post(self, request, errand_id,*args, **kwargs):
        try:
            errand_instance = ErrandTask.objects.get(id=errand_id)
        except Exception as e:
            return Response({"error": "Not Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        errand_instance.status = 'CANCELLED'
        errand_instance.save()
        return Response({"message": "Errand successfully cancelled" }, status=status.HTTP_200_OK)

class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            payment_data = list(Payments.objects.all().values())
            return Response({'payment_data':payment_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ErrandStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_month = datetime.now().replace(day=1)
        last_month = current_month - timedelta(days=1)
        try:
            current_month_errand_count = ErrandTask.objects.filter(
                created__year=current_month.year,
                created__month=current_month.month
            ).count()
            last_month_errand_count = ErrandTask.objects.filter(
                created__year=last_month.year,
                created__month=last_month.month
            ).count()
            print(current_month_errand_count,last_month_errand_count)
            errand_percentage_change = ((current_month_errand_count - last_month_errand_count) / last_month_errand_count) * 100
            print(errand_percentage_change)
        except ZeroDivisionError:
            errand_percentage_change = 0

        context = {
            'current_month_errand_count': current_month_errand_count,
            'errand_percentage_change': round(errand_percentage_change, 2)
        }
        return Response(context, status=status.HTTP_200_OK)

class SelectPaymentMethod(APIView):
    def post(self, request, id, *args, **kwargs):
        payment_mode = request.data.get('payment_method')

        try:
            errand_task = ErrandTask.objects.get(id=id)
            errand_task.payment_method = payment_method
            errand_task.save()

            serializer = ErrandTaskSerializer(errand_task)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ErrandTask.DoesNotExist:
            return Response({'error': 'Errand Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class MakePayment(APIView):
    def post(self, request, *args, **kwargs):
        try:
            errand_id = request.data.get('errand_id')
            user = self.request.user
            errand = ErrandTask.objects.get(id=errand_id)
            total_cost = errand.total_cost
            try:
                payment_instance = Payments.objects.create(errands = errand)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
            payment_id = payment_instance.payment_id
            payment_status = self.initiate_payment(total_cost, user.email,str(user.phone_number) , user.first_name, errand_id, payment_id)
            context = {
                'errnad_id':errand_id,
                'total_cost':total_cost,
                'user_email':user.email,
                'first_name':user.first_name,
                'last_name':user.last_name,
            }
            current_payment_status = payment_status.get('status')
            if current_payment_status == 'success':
                context['payment_status'] = payment_status
                return Response(context, status=status.HTTP_200_OK)
            else:
                return Response(payment_status, status=500)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def initiate_payment(self,amount, email, phone_number, name, errand_id, payment_id):
        url = "https://api.flutterwave.com/v3/payments"
        flw_sec_key = os.environ.get("FLW_SEC_KEY")
        headers = {
            "Authorization": f"Bearer {flw_secret_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "tx_ref": str(uuid.uuid4()),
            "amount": str(amount), 
            "currency": "NGN",
            "redirect_url": f"http:/127.0.0.1:8001/api/errand-initiate-payment/confirm_payment/?errand_id={errand_id}&payment_id={payment_id}",
            "meta": {
                "consumer_id": 23,
                "consumer_mac": "92a3-912ba-1192a"
            },
            "customer": {
                "email": email,
                "phonenumber": phone_number,
                "name": name
            },
            "customizations": {
                "title": "Herrands Payments",
                "logo": "http://www.piedpiper.com/app/themes/joystick-v27/images/logo.png" # this can be change
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code // 100 == 2:
            return response.json()
        else:
            return Response({"error":"Unable to make payment"}, status=response.status_code)
        
@csrf_exempt
def confirm_payment_view(request):
    if request.method == 'GET':
        try:
            # Access the parameters from the URL
            status = request.GET.get('status')
            errand_id = request.GET.get('errand_id')
            tx_ref = request.GET.get('tx_ref')
            transaction_id = request.GET.get('transaction_id')
            payment_id = request.GET.get('payment_id')

            payment_instance = Payments.objects.get(payment_id = payment_id)
            payment_instance.reference_id = tx_ref
            payment_instance.transaction_id = transaction_id
            if status == 'successful':
                payment_instance.payment_status = 'c'
            elif status == 'cancelled':
                payment_instance.payment_status = 'f'
            payment_instance.save()

            response_data = {
                "status": status,
                "tx_ref": tx_ref,
                "transaction_id": transaction_id,
                "message": "Received and processed the data successfully",
            }
            return JsonResponse(response_data)
        except Payments.DoesNotExist:
            return JsonResponse({"error": "Payment instance not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=400)

class WithdrawApi(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            #Handled only agent can withdraw
            if not request.user.is_agent:
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = WithdrawSerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                account_bank = validated_data.get('account_bank')
                account_number = validated_data.get('account_number')
                amount = validated_data.get('amount')
                agent_instance = self.request.user 

                #Calling of transfer method
                transfer_response = self.transfer(account_bank, account_number, amount, agent_instance.id)
                return transfer_response
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @csrf_exempt
    def transfer(self, account_bank, account_number, amount, agent_id):
        try:
            agent = get_user_model().objects.get(id=agent_id)
            wallet_data = Wallet.objects.get(user=agent)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        flutterwave_transfer_url = 'https://api.flutterwave.com/v3/transfers'
        # Check if the agent has sufficient balance
        if wallet_data.balance < amount:
            return JsonResponse({'success': False, 'message': 'Insufficient balance'})

        # Initiate transfer with Flutterwave
        flw_sec_key = "FLWSECK_TEST-fa9f76dea9dd1ae5f29784bc4bbfee46-X"
        headers = {'Authorization': f'Bearer {flw_sec_key}'}
        payload = {
            "account_bank":account_bank,
            "account_number":account_number,
            "amount": amount,
            "narration": "Payment for agent's withdraw",
            "currency": "NGN",
            # "reference": "akhlm-pstmnpyt-rfxx007_PMCKDU_1",
            # "callback_url": "https://www.flutterwave.com/ng/",
            "debit_currency": "NGN"
        }
        try:
            response = requests.post(flutterwave_transfer_url, json=payload, headers=headers)
            response_data = response.json()

            # Check if the transfer was successful
            if response.status_code == 200:
                
                self.create_withdraw_history(response_data.get('data'),wallet_data.user)
                # Update agent and admin balances
                wallet_data.balance -= amount
                wallet_data.save()
                #update withdraw history
                return JsonResponse({'success': True, 'message': 'Transfer successful','data':response_data }, status=200)
            
            return JsonResponse({'success': False,'error':response_data, 'message': 'Transfer failed'}, status=500)
        
        except Exception as e:
            return JsonResponse({'success': False,'error':str(e) ,'message': 'Internal server error'}, status=500)
    
    def create_withdraw_history(self,response_data,user):
        try:
            wallet_instance = Wallet.objects.get(user=user)
            bank_code = str(response_data.get('bank_code'))
            bank_account_number = int(response_data.get('account_number'))
            beneficiary_name = response_data.get('full_name')
            amount = response_data.get('amount')
            Withdrawals.objects.create(
                wallet=wallet_instance,
                bank_name=bank_code,
                bank_account_number=bank_account_number,
                beneficiary_name=beneficiary_name,
                amount=100
            )
        except Exception as e:
            print('failled _to_create_withdraw_history',str(e))

class WithdrawalHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated] 

    def get(self,request, *args, **kwargs):
        try:
            user = self.request.user
            wallet = Wallet.objects.get(user=user)
            withdraw_list = Withdrawals.objects.filter(wallet=wallet).values()
            return Response({"data": withdraw_list}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Internal server error'}, status=500)
        

# --------------------------------------------------------------------------------------------
"""class UserErrandTaskViewSet(viewsets.ModelViewSet):
    queryset = ErrandTask.objects.all()
    serializer_class = ErrandTaskSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust the permission as needed

    @action(detail=False, methods=['GET'])
    def agent_errands(self, request):
        # Get errands for the current authenticated agent
        agent_errands = ErrandTask.objects.filter(agent=request.user)
        serializer = self.get_serializer(agent_errands, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def customer_errands(self, request):
        # Get errands for the current authenticated customer
        customer_errands = ErrandTask.objects.filter(customer=request.user)
        serializer = self.get_serializer(customer_errands, many=True)
        return Response(serializer.data)"""

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10  # You can adjust this value to set the number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserErrandTaskViewSet(viewsets.ModelViewSet):
    queryset = ErrandTask.objects.all()
    serializer_class = NestedErrandSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust the permission as needed
    #pagination_class = StandardResultsSetPagination  # Enable pagination

    @action(detail=False, methods=['GET'])
    def agent_errands(self, request):
        # Get errands for the current authenticated agent
        agent_errands = ErrandTask.objects.filter(agent=request.user).exclude(status='COMPLETED').order_by('-created')[:8]
        page = self.paginate_queryset(agent_errands)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(agent_errands, many=True)
        return Response(serializer.data)

    '''@action(detail=False, methods=['GET'])
    def customer_errands(self, request):
        # Get errands for the current authenticated customer
        customer_errands = ErrandTask.objects.filter(customer=request.user)
        page = self.paginate_queryset(customer_errands)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(customer_errands, many=True)
        return Response(serializer.data)'''

class UserCompletedErrandTaskViewSet(viewsets.ModelViewSet):
    queryset = ErrandTask.objects.all()
    serializer_class = NestedErrandSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust the permission as needed
    pagination_class = StandardResultsSetPagination  # Enable pagination

    @action(detail=False, methods=['GET'])
    def agent_errands(self, request):
        # Get errands for the current authenticated agent
        agent_errands = ErrandTask.objects.filter(agent=request.user, status='COMPLETED').order_by('-created')[:8]
        page = self.paginate_queryset(agent_errands)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(agent_errands, many=True)
        return Response(serializer.data)



'''class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer'''

class VehicleMetricViewSet(viewsets.ModelViewSet):
    queryset = VehicleMetric.objects.all()
    serializer_class = VehicleMetricSerializer

    def get_permissions(self):
        if self.action == 'partial_update':
            # Add IsAuthenticated permission for the 'partial_update' (PATCH) action
            return [IsAuthenticated()]
        return super().get_permissions()

class DistanceMetricViewSet(viewsets.ModelViewSet):
    queryset = DistanceMetric.objects.all()
    serializer_class = DistanceMetricSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AllSubtypesViewSet(viewsets.ModelViewSet):
    queryset = Subtype.objects.all()
    serializer_class = SubtypeSerializer

class ErrandTaskViewSet(viewsets.ModelViewSet):
    queryset = ErrandTask.objects.all()
    serializer_class = ErrandTaskSerializer
    pagination_class = StandardResultsSetPagination

class AdminErrandTaskViewSet(viewsets.ModelViewSet):
    queryset = ErrandTask.objects.all()
    serializer_class = AdminErrandSerializer
    pagination_class = StandardResultsSetPagination

class AdminErrandTaskDeleteAPIView(generics.DestroyAPIView):
    queryset = ErrandTask.objects.all()
    serializer_class = AdminErrandSerializer
    #permission_classes = [IsAuthenticated]

class SubtypeViewSet(viewsets.ModelViewSet):
    queryset = Subtype.objects.all()
    serializer_class = SubtypeSerializer

    def list(self, request, *args, **kwargs):
        category_id = request.query_params.get('category_id')
        if category_id is not None:
            subtypes = self.queryset.filter(category__id=category_id)
            serializer = self.serializer_class(subtypes, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Category ID not provided"})

'''class CreateErrandView(APIView):
    def post(self, request, format=None):
        serializer = ErrandTaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Get the first error message
        field_name = next(iter(serializer.errors))
        first_error = next(iter(serializer.errors.values()))[0]

        return Response({field_name: first_error}, status=status.HTTP_400_BAD_REQUEST)'''

class CreateErrandView(CreateAPIView):
    serializer_class = ErrandTaskSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # import logging
        data = request.data
        # logger = logging.getLogger('accounts')
        # logger.info('inside post')
        # logger.info(data)
        serializer = self.get_serializer(data=data,context={'request':request})
        if serializer.is_valid():
            # logger.info('serializer is valid')
            prop = serializer.save()
            print(prop)
            return Response({
                'message': "Errand Created successfully",
                'data': serializer.data
            }, status=200, )
        error_keys = list(serializer.errors.keys())
        if error_keys:
            error_msg = serializer.errors[error_keys[0]]
            return Response({'message': error_msg[0]}, status=400)
        return Response(serializer.errors, status=400)

@api_view(['POST'])
def start_convo(request, ):
    data = request.data
    username = data.pop('username')
    try:
        participant = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'message': 'You cannot chat with a non existent user'})

    conversation = Conversation.objects.filter(Q(initiator=request.user, receiver=participant) |
                                               Q(initiator=participant, receiver=request.user))
    if conversation.exists():
        return redirect(reverse('get_conversation', args=(conversation[0].id,)))
    else:
        conversation = Conversation.objects.create(initiator=request.user, receiver=participant)
        return Response(ConversationSerializer(instance=conversation).data)


@api_view(['GET'])
def get_conversation(request, convo_id):
    conversation = Conversation.objects.filter(errand=convo_id)
    print('yes')
    if not conversation.exists():
        return Response({'message': 'Conversation does not exist'})
    else:
        serializer = ConversationSerializer(instance=conversation[0])
        return Response(serializer.data)


@api_view(['GET'])
def conversations(request):
    conversation_list = Conversation.objects.filter(Q(customer=request.user) |
                                                    Q(agent=request.user))
    serializer = ConversationListSerializer(instance=conversation_list, many=True)
    return Response(serializer.data)

class ConversationListAPIView(generics.ListAPIView):
    Permission = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        room_name = self.kwargs['room_name']

        # Get the conversations with the latest message timestamp
        queryset = Conversation.objects.filter(errand__id=room_name)
    
        return queryset

class AgentConversationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        conversations = Conversation.objects.filter(agent__id=user_id)
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomerConversationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        conversations = Conversation.objects.filter(customer__id=user_id).exclude(agent=None)
        serializer = ConversationListSerializer2(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
class WalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.get(user=self.request.user)
        except Wallet.DoesNotExist:
            # If the wallet doesn't exist, create a new one
            wallet = Wallet.objects.create(user=self.request.user)

        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

class EarningsListView(generics.ListAPIView):
    serializer_class = EarningsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Earnings.objects.filter(wallet__user=self.request.user)

        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(timestamp__year=year)

        # Filter by month
        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(timestamp__month=month)

        # Filter by year-only
        year_only = self.request.query_params.get('year_only')
        if year_only:
            queryset = queryset.filter(timestamp__year=year_only, timestamp__month=1)

        # Filter by day of month
        day = self.request.query_params.get('day')
        if day:
            queryset = queryset.filter(timestamp__day=day)

        return queryset

class WithdrawalView(APIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, request):
        serialize.save(wallet__user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get(self, request):
        withdrwals = Withdrawals.objects.filter(wallet__user=self.request.user)
        serializer = WithdrawalSerializer(withdrwals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminTopCustomersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        top_customers = get_user_model().objects.annotate(errands_count=Count('errands_as_customer')).order_by('-errands_count')[:5]
        serializer = User2Serializer(top_customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminTopAgentsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        top_agents = get_user_model().objects.annotate(errands_count=Count('errands_as_agent')).order_by('-errands_count')[:5]
        serializer = User2Serializer(top_agents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

'''class AdminErrandsComparisonView(APIView):
    def get(self, request):
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Calculate the start and end date for the current month
        current_month_start = timezone.datetime(current_year, current_month, 1)
        current_month_end = current_month_start + timedelta(days=32)

        # Calculate the start and end date for the previous month
        previous_month_start = current_month_start - timedelta(days=current_month_start.day)
        previous_month_end = current_month_start

        # Query the database to get the number of errands for the current and previous months
        current_month_errands = ErrandTask.objects.filter(created__gte=current_month_start, created__lt=current_month_end).count()
        previous_month_errands = ErrandTask.objects.filter(created__gte=previous_month_start, created__lt=previous_month_end).count()

        # Calculate the percentage change
        if previous_month_errands == 0:
            percentage_change = 100  # Handle division by zero
        else:
            percentage_change = ((current_month_errands - previous_month_errands) / previous_month_errands) * 100

        response_data = {
            "current_month_errands": current_month_errands,
            "previous_month_errands": previous_month_errands,
            "percentage_change": round(percentage_change, 2)
        }

        return Response(response_data, status=status.HTTP_200_OK)'''

class AdminErrandsComparisonView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Calculate the start and end date for the current month
        current_month_start = timezone.datetime(current_year, current_month, 1)
        current_month_end = current_month_start + timedelta(days=32)

        # Calculate the start and end date for the previous month
        previous_month_start = current_month_start - timedelta(days=current_month_start.day)
        previous_month_end = current_month_start

        # Query the database to get the number of errands for the current and previous months
        current_month_errands = ErrandTask.objects.filter(created__gte=current_month_start, created__lt=current_month_end).count()
        previous_month_errands = ErrandTask.objects.filter(created__gte=previous_month_start, created__lt=previous_month_end).count()

        # Calculate the percentage change for errands
        errands_percentage_change = self.calculate_percentage_change(previous_month_errands, current_month_errands)

        # Query the database to get the number of customers registered for the current and previous months
        current_month_customers = User.objects.filter(
            user_type='Customer',
            date_joined__gte=current_month_start,
            date_joined__lt=current_month_end
        ).count()

        previous_month_customers = User.objects.filter(
            user_type='Customer',
            date_joined__gte=previous_month_start,
            date_joined__lt=previous_month_end
        ).count()

        # Calculate the percentage change for customers
        customers_percentage_change = self.calculate_percentage_change(previous_month_customers, current_month_customers)

        # Query the database to get the number of agents registered for the current and previous months
        current_month_agents = User.objects.filter(
            user_type='Agent',
            date_joined__gte=current_month_start,
            date_joined__lt=current_month_end
        ).count()

        previous_month_agents = User.objects.filter(
            user_type='Agent',
            date_joined__gte=previous_month_start,
            date_joined__lt=previous_month_end
        ).count()

        # Calculate the percentage change for agents
        agents_percentage_change = self.calculate_percentage_change(previous_month_agents, current_month_agents)

        response_data = {
            "errands": {
                "current_month": current_month_errands,
                "previous_month": previous_month_errands,
                "percentage_change": errands_percentage_change,
            },
            "customers": {
                "current_month": current_month_customers,
                "previous_month": previous_month_customers,
                "percentage_change": customers_percentage_change,
            },
            "agents": {
                "current_month": current_month_agents,
                "previous_month": previous_month_agents,
                "percentage_change": agents_percentage_change,
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def calculate_percentage_change(self, previous_value, current_value):
        if previous_value ==0 and current_value ==0:
            return 0  # Handle division by zero
        elif previous_value ==0:
            return 100
        else:
            return round(((current_value - previous_value) / previous_value) * 100, 2)
        

class AgentRatingView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AgentRatingSerializer(data=request.data)
        if serializer.is_valid():
            errand_id = serializer.validated_data['errand_id']
            user_rating = serializer.validated_data['user_rating']

            # Update the agent_rating field in the corresponding ErrandTask instance
            errand_task = ErrandTask.objects.filter(id=errand_id, agent_rating__isnull=True).first()
            if errand_task:
                errand_task.agent_rating = user_rating
                errand_task.save()

                # Recalculate total and average ratings for the agent and update the Agent model
                agent = errand_task.agent
                all_ratings = ErrandTask.objects.filter(agent=agent, agent_rating__isnull=False).values_list('agent_rating', flat=True)
                total_ratings = sum(all_ratings)
                total_tasks_rated = len(all_ratings)
                average_rating = total_ratings / total_tasks_rated if total_tasks_rated > 0 else 0

                agent.average_rating = average_rating
                agent.total_ratings = total_ratings
                agent.total_tasks_rated = total_tasks_rated
                agent.save()

                return Response({'detail': 'Rating submitted successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Errand not found or already rated.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

