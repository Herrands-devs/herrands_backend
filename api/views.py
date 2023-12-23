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
from .serializers import ConversationListSerializer, ConversationSerializer
from django.db.models import Q
from django.shortcuts import redirect, reverse
from accounts.serializers import *
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta




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

class ErrandTaskViewSet(viewsets.ModelViewSet):
    queryset = ErrandTask.objects.all()
    serializer_class = ErrandTaskSerializer
    pagination_class = StandardResultsSetPagination

class AdminErrandTaskViewSet(viewsets.ModelViewSet):
    queryset = ErrandTask.objects.all()
    serializer_class = AdminErrandSerializer
    pagination_class = StandardResultsSetPagination

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
        conversations = Conversation.objects.filter(customer__id=user_id)
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

