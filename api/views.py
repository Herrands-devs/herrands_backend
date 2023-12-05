from rest_framework import viewsets, pagination
from .models import Category, ErrandTask, Subtype, VehicleMetric, DistanceMetric
from .serializers import *
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action

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
    pagination_class = StandardResultsSetPagination  # Enable pagination

    @action(detail=False, methods=['GET'])
    def agent_errands(self, request):
        # Get errands for the current authenticated agent
        agent_errands = ErrandTask.objects.filter(agent=request.user)
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
        agent_errands = ErrandTask.objects.filter(agent=request.user, status="COMPLETED")
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

class DistanceMetricViewSet(viewsets.ModelViewSet):
    queryset = DistanceMetric.objects.all()
    serializer_class = DistanceMetricSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ErrandTaskViewSet(viewsets.ModelViewSet):
    queryset = ErrandTask.objects.all()
    serializer_class = ErrandTaskSerializer

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


