from django.contrib.auth import get_user_model
from .models import Agent, Preferences, Services, Idtype
from rest_framework import serializers
import base64
from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializer

User = get_user_model()

class Base64ImageField(serializers.ImageField):
    ALLOWED_IMAGE_FORMATS = ['jpeg', 'jpg', 'png', 'gif']

    def to_internal_value(self, data):
        try:
            # Extract the file format and encoded data
            format, encoded_data = data.split(';base64,')
            # Get the file extension from the format
            file_extension = format.split("/")[-1]

            # Check if the file format is allowed
            if file_extension.lower() not in self.ALLOWED_IMAGE_FORMATS:
                raise serializers.ValidationError("Invalid image format")

            # Decode the base64 data
            decoded_data = base64.b64decode(encoded_data)
            # Create a ContentFile with the decoded data
            return ContentFile(decoded_data, name=f'image_file.{file_extension}')
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 image data: {e}")

        return super().to_internal_value(data)

class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        try:
            # Extract the file format and encoded data
            format, encoded_data = data.split(';base64,')
            # Decode the base64 data
            decoded_data = base64.b64decode(encoded_data)
            # Create a ContentFile with the decoded data
            return ContentFile(decoded_data, name=f'id_file.{format.split("/")[-1]}')
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 file data: {e}")
        return super().to_internal_value(data)

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = '__all__'

class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'


class IdtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idtype
        fields = '__all__'





class TokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    contact = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'account_completed')
        read_only_fields = ('id', 'account_completed')
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value

    def validate_first_name(self, value):
        if not value:
            raise serializers.ValidationError("First name is required.")
        return value

    def validate_last_name(self, value):
        if not value:
            raise serializers.ValidationError("Last name is required.")
        return value

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user_type = instance.user_type

        if 'agent_representation' in self.context and user_type == 'Agent':
            agent_data = AgentSerializer(instance.agent).data
            data['agent'] = agent_data

        return data
    
    

    

class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    preference = serializers.PrimaryKeyRelatedField(queryset=Preferences.objects.all())
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Services.objects.all())
    id_type = serializers.PrimaryKeyRelatedField(queryset=Idtype.objects.all())
    id_file  = Base64FileField()

    class Meta:
        model = Agent
        exclude = ['country']
        read_only_fields = ('photo',  'pay_per_hour', 'arrival_speed', 'delivery_speed', 'bank_name', 'account_number', 'beneficiary_name')
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        services = validated_data.pop('services', [])
        user = User.objects.create(**user_data)
        
        agent = Agent.objects.create(user=user, **validated_data)
        agent.services.set(services)

        return agent

    

class AgentUpdateSerializer(serializers.ModelSerializer):
    photo = Base64ImageField()
    class Meta:
        model = Agent
        fields = ['photo', 'pay_per_hour', 'arrival_speed', 'delivery_speed', 'bank_name', 'account_number', 'beneficiary_name']

'''class UserUpdateSerializer(serializers.ModelSerializer):
    agent_data = AgentUpdateSerializer()

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone_number', 'agent_data']


    def update(self, instance, validated_data):
        agent_data = validated_data.pop('agent_data', {})
        agent_instance = instance.agent if hasattr(instance, 'agent') else None

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if agent_data and agent_instance:
            # Ensure that 'agent' attribute exists on the 'User' instance
            if not hasattr(instance, 'agent'):
                Agent.objects.create(user=instance, **agent_data)
            else:
                for key, value in agent_data.items():
                    setattr(agent_instance, key, value)
                agent_instance.save()
                instance.account_completed = True
                instance.save()

        instance.save()
        return instance




'''
class UserUpdateSerializer(serializers.ModelSerializer):
    agent_data = AgentUpdateSerializer()

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone_number', 'agent_data']

    def update(self, instance, validated_data):
        agent_data = validated_data.pop('agent_data', {})
        agent_instance = instance.agent if hasattr(instance, 'agent') else None

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if agent_data:
            # Ensure that 'agent' attribute exists on the 'User' instance
            if not hasattr(instance, 'agent'):
                Agent.objects.create(user=instance, **agent_data)
            else:
                for key, value in agent_data.items():
                    setattr(agent_instance, key, value)
                agent_instance.save()
                user = User.objects.get(email=instance)
                print(user)
                user.account_completed = True
                user.save()
                instance.account_completed = True

        instance.save()
        return instance

class UserDeletionSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)