from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Category, Earnings, Wallet, Subtype, File, ErrandTask, VehicleMetric, DistanceMetric, Conversation, Message
import base64
from django.core.files.base import ContentFile
from rest_framework.exceptions import APIException
from django.conf import settings

from math import radians, sin, cos, sqrt, atan2
from decimal import Decimal
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c

    return distance



class APIException400(APIException):
    status_code = 400


class VehicleMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMetric
        fields = '__all__'

class DistanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistanceMetric
        fields = '__all__'


class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        # If the input data is a base64-encoded string, decode it
        #if isinstance(data, str) and data.startswith('data:audio'):
        try:
            # Extract the file format and encoded data
            format, encoded_data = data.split(';base64,')
            # Decode the base64 data
            decoded_data = base64.b64decode(encoded_data)
            # Create a ContentFile with the decoded data
            return ContentFile(decoded_data, name=f'file.{format.split("/")[-1]}')
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 file data: {e}")
        return super().to_internal_value(data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtype
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    file = Base64FileField()
    class Meta:
        model = File
        fields = '__all__'

class AdminErrandSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    agent = UserSerializer()
    class Meta:
        model= ErrandTask
        fields = ['id', 'customer', 'agent', 'describe_errand', 'total_cost', 'pick_up_address', 'drop_off_address', 'created', 'updated', 'status']
        depth = 1

class ErrandTaskSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, required=False)

    class Meta:
        model = ErrandTask
        fields = '__all__'

    '''def validate(self, attrs):
        category = attrs['category']
        files = attrs['files']

        if not files:
            raise APIException400({"message": "property must have flats"})

        if category:
            category_id = category

            # Check the category ID and enforce field requirements
            if category_id == 3:  # Replace 1 with the actual ID of the "Work" category
                # If "Work" category is selected, make certain fields required
                if not files:
                    raise APIException400({"message": "property must have flats"})
                    
                return attrs

        return attrs'''

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        subtype_data = validated_data.pop('subtype')
        # Handle the case where 'files' is not provided or is an empty list
        total_cost = 0
        distance_in_km = 0
        if subtype_data == 2:
            validated_data_copy = validated_data.copy()
            lat_1 = validated_data_copy.pop('pick_up_lat')
            long_1 = validated_data_copy.pop('pick_up_long')
            lat_2 = validated_data_copy.pop('drop_off_lat')
            long_2 = validated_data_copy.pop('drop_off_long')
            distance_in_km = calculate_distance(lat_1, long_1, lat_2, long_2)
            print(distance_in_km)
            vehicle_type = validated_data_copy.pop('vehicle_type')
            vehicle_instance = VehicleMetric.objects.get(id=vehicle_type.id)
            total_cost = Decimal(str(vehicle_instance.cost)) * Decimal(str(distance_in_km))
            print(total_cost)

        

        
        if not validated_data.get('files'):
            files = []
        else:
            files_data = validated_data.pop('files')
            files = [File.objects.create(**file_data) for file_data in files_data]

        errand_task = ErrandTask.objects.create(category=category_data, subtype=subtype_data, distance_in_km = distance_in_km, total_cost=total_cost, **validated_data)
        if files:
            errand_task.files.set(files)
        

        return errand_task

 

class NestedErrandSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    agent = UserSerializer()

    class Meta:
        model = ErrandTask
        fields = '__all__'
        depth = 1

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        ordering = ['-h']
        

class NestedMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    class Meta:
        model = Message
        exclude = ('conversation_id',)


class ConversationListSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    #agent = UserSerializer()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'customer', 'last_message', 'errand']

    '''def get_last_message(self, instance):
        message = instance.message_set.first()
        return MessageSerializer(instance=message)'''
    def get_last_message(self, instance):
        message = instance.message_set.last()
        return MessageSerializer(instance=message).data


class ConversationSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    agent = UserSerializer()
    message_set = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ['customer', 'agent', 'message_set']
    
    def get_message_set(self, instance):
        ordered_messages = instance.ordered_messages.all(id=1)
        return MessageSerializer(instance=ordered_messages, many=True).data

class EarningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earnings
        fields = ['amount', 'timestamp']

class WalletSerializer(serializers.ModelSerializer):
    #earnings = EarningsSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ['balance', 'timestamp']

