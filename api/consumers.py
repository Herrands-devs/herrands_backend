from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
import asyncio
from rest_framework import serializers
from .serializers import *
from accounts.serializers import AgentSerializer
from rest_framework.exceptions import ValidationError
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile
import base64
import json
from datetime import datetime
import random
from .models import ErrandTask, Conversation, Message
from django.core import serializers
from django.contrib.auth import get_user_model
from accounts.models import Agent

#from trips.serializers import NestedTripSerializer, TripSerializer, UserSerializer, UserFullSerializer

from math import radians, sin, cos, sqrt, atan2
import math

User = get_user_model()

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


class ErrandConsumer(AsyncJsonWebsocketConsumer):
    groups = ['test']

    @database_sync_to_async
    def _add_rejected_agent(self, errand, rejecting_agent):
        errand.rejected_agents.add(rejecting_agent)
        errand.save()

    @database_sync_to_async
    def _get_nearest_agent(self):
        agents = Agent.objects.all()
        
        if agents.exists():  # Check if any agents exist in the queryset
            random_agent = random.choice(agents)
            nearest_agent_data = AgentSerializer(random_agent).data
            print("Randomly selected agent:", nearest_agent_data)
            return nearest_agent_data
        else:
            print("No agents found.")
            return None

    @database_sync_to_async
    def _get_nearest_agents(self):
        #nearest_agents = []
        agents = Agent.objects.all()


        '''for agent in agents:
            nearest_agents.append(agent)
            print(agent)'''
        nearest_agents = AgentSerializer(agents, many=True).data

        print("Nearest driver after excluding rejected drivers:", nearest_agents)


        return nearest_agents
    


    '''@database_sync_to_async
    def _get_nearest_driver(self, pickup_lat, pickup_long):
        nearest_driver = None
        min_distance = float('inf')  # Initialize with positive infinity

        # Iterate through all users in the 'driver' group
        drivers = User.objects.filter(groups__name='driver')
        for driver in drivers:
            driver_lat = float(driver.current_lat)
            driver_long = float(driver.current_long)

            # Calculate the distance between the pickup location and the driver's location
            distance = calculate_distance(pickup_lat, pickup_long, driver_lat, driver_long)

            if distance < min_distance:
                # If this driver is closer than the current nearest driver, update the nearest driver and distance
                nearest_driver = driver
                min_distance = distance

        return nearest_driver

    @database_sync_to_async
    def _get_nearest_driver_exclude_rejected(self, pickup_lat, pickup_long, rejected_drivers):
        nearest_driver = None
        min_distance = float('inf')

        # Fetch all drivers excluding rejected ones
        drivers = User.objects.filter(groups__name='driver').exclude(id__in=rejected_drivers).only('current_lat', 'current_long')

        print("Drivers after excluding rejected drivers:", drivers)

        for driver in drivers:
            driver_lat = float(driver.current_lat)
            driver_long = float(driver.current_long)

            # Calculate the distance between the pickup location and the driver's location
            distance = calculate_distance(pickup_lat, pickup_long, driver_lat, driver_long)

            print(f"Driver {driver.id} - Distance: {distance}")

            if distance < min_distance:
                nearest_driver = driver
                min_distance = distance

        print("Nearest driver after excluding rejected drivers:", nearest_driver)

        return nearest_driver'''
    
    @database_sync_to_async
    def _update_location(self, data):
        user_id = data.get('id')
        print(user_id)
        user = User.objects.get(id=user_id)
        user.current_lat = data.get('current_lat')
        user.current_long = data.get('current_long')
        user.current_location = data.get('current_location')
        user.save()

    
    @database_sync_to_async
    def _create_errand(self, data):
        serializer = ErrandTaskSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.create(serializer.validated_data)

    @database_sync_to_async
    def _create_room(self, data):
        room = Conversation.objects.create(errand=data, customer=data.customer)
        return room
        

    @database_sync_to_async
    def _get_errand_data(self, errand):
        return NestedErrandSerializer(errand).data

    @database_sync_to_async
    def _get_errand_by_id(self, id):
        errand = ErrandTask.objects.get(id=id)
        return NestedErrandSerializer(errand).data

    @database_sync_to_async
    def _get_message_data(self, message):
        return NestedMessageSerializer(message).data

    '''@database_sync_to_async
    def _get_errand_ids(self, user):
        is_agent = user.user_type

        if is_agent == 'Agent':
            errandtask_ids = ErrandTask.objects.filter(
                agent=user,
                status__in=[ErrandTask.REQUESTED, ErrandTask.ACCEPTED, ErrandTask.ARRIVED, ErrandTask.STARTED, ErrandTask.IN_PROGRESS],
                user_cancelled=False
            ).values_list('id', flat=True)
        else:
            errandtask_ids = ErrandTask.objects.filter(
                customer=user,
                status__in=[ErrandTask.REQUESTED, ErrandTask.ACCEPTED, ErrandTask.ARRIVED, ErrandTask.STARTED, ErrandTask.IN_PROGRESS],
                user_cancelled=False
            ).values_list('id', flat=True)

        return map(str, errandtask_ids)'''
    @database_sync_to_async
    def _get_errand_ids(self, user):
        is_agent = user.user_type

        # Determine the field and value based on the user type
        '''field_name = "agent" if is_agent == 'Agent' else "customer"
        field_value = user

        # Perform a single query for errand task IDs
        errandtask_ids = ErrandTask.objects.filter(
            **{f"{field_name}": field_value},
            status__in=[ErrandTask.REQUESTED, ErrandTask.ACCEPTED, ErrandTask.ARRIVED, ErrandTask.STARTED, ErrandTask.IN_PROGRESS],
            user_cancelled=False
        ).values_list('id', flat=True)

        # Convert the IDs to strings and return
        return map(str, errandtask_ids)'''
        if is_agent == 'Agent':
            errandtask_ids = user.errands_as_agent.exclude(
                status=ErrandTask.COMPLETED
            ).only('id').values_list('id', flat=True)
        else:
            errandtask_ids = user.errands_as_customer.exclude(
                status=ErrandTask.COMPLETED
            ).only('id').values_list('id', flat=True)
        return map(str, errandtask_ids)




    @database_sync_to_async
    def _get_user_group(self, user):
        user_type = ''
        if user.is_agent == True:
            user_type = 'Agent'
        else:
            user_type = 'Customer'
        return user_type

    @database_sync_to_async
    def _update_errand(self, data):
        try:
            instance = ErrandTask.objects.get(id=data.get('id'))
            serializer = ErrandTaskSerializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return instance
        except ErrandTask.DoesNotExist:
            raise ValidationError("Errand with the provided ID does not exist")

    @database_sync_to_async
    def _update_room(self, data):
        try:
            instance = Conversation.objects.get(errand=data.get('id'))
            agent = User.objects.get(id=data.get('agent'))
            instance.agent = agent
            instance.save()
            return instance
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Errand with the provided ID does not exist")

    async def connect(self):
        try:
            user = self.scope['user']
            if user.is_anonymous:
                await self.close()
            else:
                user_group = await self._get_user_group(user)
                if user_group == 'Agent':
                    await self.channel_layer.group_add(
                        group=f'agent_{user.id}',
                        channel=self.channel_name
                    )
                    print('i am an agent')
                print(user.email)

                #errand_ids = await self._get_errand_ids(user)
                await self.accept()
                for errand_id in await self._get_errand_ids(user):
                    await self.channel_layer.group_add(
                            group=f'errand_{errand_id}',
                            channel=self.channel_name
                        )
                    print(f'Connection established: Customer for Errand {errand_id}')

               
            
            

        except Exception as e:
            print(f"Exception during connection: {e}")
            await self.close()

    ''' async def get_drivers(self, message):
        data = message.get('data')
        pickup_lat = data.get('pick_up_lat')
        pickup_long = data.get('pick_up_long')

        nearby_drivers = await self._get_nearby_drivers(pickup_lat, pickup_long)

        await self.send_json({
            'type': 'echo.message',
            'data': nearby_drivers
        })'''
    async def send_error_message(self, error_message):
        await self.send_json({
            'type': 'error.message',
            'data': {'error': error_message}
        })


    async def create_errand(self, message):
        data = message.get('data')
        errand = None
        '''pickup_lat = data.get('pick_up_lat')
        pickup_long = data.get('pick_up_long')'''
        ''' errand = await self._create_errand(data)
        errand_data = await self._get_errand_data(errand)'''
    
        # Code that might raise an exception
        errand = await self._create_errand(data)
        errand_data = await self._get_errand_data(errand)
        room = await self._create_room(errand)


        # Calculate nearby drivers
        '''nearby_driver = await self._get_nearest_driver(pickup_lat, pickup_long)

        if nearby_driver:
            distance = calculate_distance(pickup_lat, pickup_long, float(nearby_driver.current_lat), float(nearby_driver.current_long))
            max_distance = 5.0'''
        
        if errand:
            nearby_agents = await self._get_nearest_agents()
            print("check")
            print(nearby_agents)

            if nearby_agents:
                for nearby_agent in nearby_agents:
                    await self.channel_layer.group_send(
                    group=f'agent_{nearby_agent.id}',
                    message={
                        'type': 'errand.requested',
                        'data': errand_data
                    }
                    )
            #print(nearby_driver)
            # Add rider to trip group.
            await self.channel_layer.group_add(
                group=f'errand_{errand.id}',
                channel=self.channel_name
            )

            await self.send_json({
                'type': 'errand.created',
                'data': errand_data,
            })
    async def create_routine_errand(self, message):
        data = message.get('data')
        errand = None
        '''pickup_lat = data.get('pick_up_lat')
        pickup_long = data.get('pick_up_long')'''
        ''' errand = await self._create_errand(data)
        errand_data = await self._get_errand_data(errand)'''
    
        # Code that might raise an exception
        errand = await self._create_errand(data)
        errand_data = await self._get_errand_data(errand)
        room = await self._create_room(errand)


        # Calculate nearby drivers
        '''nearby_driver = await self._get_nearest_driver(pickup_lat, pickup_long)

        if nearby_driver:
            distance = calculate_distance(pickup_lat, pickup_long, float(nearby_driver.current_lat), float(nearby_driver.current_long))
            max_distance = 5.0'''
        
        if errand:
            '''nearby_agents = await self._get_nearest_agents()
            print("check")
            print(nearby_agents)

            if nearby_agents:
                for nearby_agent in nearby_agents:
                    await self.channel_layer.group_send(
                    group=f'agent_{nearby_agent.id}',
                    message={
                        'type': 'errand.requested',
                        'data': errand_data
                    }
                    )'''
            #print(nearby_driver)
            # Add rider to trip group.
            await self.channel_layer.group_add(
                group=f'errand_{errand.id}',
                channel=self.channel_name
            )

            await self.send_json({
                'type': 'errand.created',
                'data': errand_data,
            })
    async def create_virtual_errand(self, message):
        data = message.get('data')
        errand = None
        '''pickup_lat = data.get('pick_up_lat')
        pickup_long = data.get('pick_up_long')'''
        ''' errand = await self._create_errand(data)
        errand_data = await self._get_errand_data(errand)'''
    
        # Code that might raise an exception
        errand = await self._create_errand(data)
        errand_data = await self._get_errand_data(errand)
        room = await self._create_room(errand)
        
        if errand:
            await self.channel_layer.group_add(
                group=f'errand_{errand.id}',
                channel=self.channel_name
            )
            nearby_agents = await self._get_nearest_agents()

            await self.send_json({
                'type': 'errand.created',
                'data': errand_data,
                'agents': nearby_agents
            })
    
    
    async def get_agents(self, message):
        data = message.get('data')
        '''pickup_lat = data.get('pick_up_lat')
        pickup_long = data.get('pick_up_long')'''

        nearby_agents = await self._get_nearest_agents()

        await self.send_json({
            'type': 'echo.message',
            'data': nearby_agents
        })
    

    async def disconnect(self, code):
        print(f"WebSocket disconnected with code: {code}")
        await super().disconnect(code)

    async def echo_message(self, message):
        await self.send_json(message)
        
    async def errand_requested(self, event):
        # Handle the 'errand.requested' message type here
        # You can send a response back to the client or perform any necessary logic
        await self.send_json({
            'type': 'errand.requested',
            'data': event['data'],
        })
    async def errand_resent(self, event):
        # Handle the 'errand.requested' message type here
        # You can send a response back to the client or perform any necessary logic
        await self.send_json({
            'type': 'errand.resent',
            'data': event['data'],
            'new_agent': event['agent']
        })
    async def errand_accepted(self, event):
        # Handle the 'errand.requested' message type here
        # You can send a response back to the client or perform any necessary logic
        print(event['data']['status'])
        await self.send_json({
            'type': 'errand.' + event['data']['status'],
            'data': event['data'],
        })

    
    
    

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type == 'create.errand':
            await self.create_errand(content)
        elif message_type == 'create.routine_errand' or message_type == 'create.household_chores':
            await self.create_routine_errand(content)
        elif message_type == 'complete.routine_errand' or message_type == 'complete.household_chores':
            await self.complete_routine_errand(content)
        elif message_type == 'create.outdoor_errand':
            await self.create_routine_errand(content)
        elif message_type == 'create.virtual_errand':
            await self.create_virtual_errand(content)
        elif message_type == 'complete.outdoor_errand':
            await self.complete_routine_errand(content)
        elif message_type == 'errand.requested':
            await self.echo_message(content)
        elif message_type == 'echo.message':
            await self.echo_message(content)
        elif message_type == 'update.errand':
            await self.update_errand(content)
        elif message_type == 'check.agents':
            await self.get_drivers(content)
        elif message_type == 'user.location.update':
            await self.update_location(content)
        elif message_type == 'send.virtual_errand':
            await self.send_virtual_errand(content)

    async def update_location(self, message):
        data = message.get('data')
        update_loc = await self._update_location(data)
        await self.send_json({
            'type': 'location.updated',
            'data': 'location updated successfully'
        })

    async def update_errand(self, message):
        data = message.get('data')
        errand_data_id = data['id']
        if data['status'] == 'REJECTED':
            errand = await self._update_errand({'id':data['id'],'status':'REJECTED'})
        else:
            errand = await self._update_errand(data)
            room = await self._update_room(data)
        errand_id = f'errand_{errand.id}'
        errand_data = await self._get_errand_data(errand)

        if errand.status == 'REJECTED':
            rejecting_agent = self.scope['user']
            await self._add_rejected_agent(errand, rejecting_agent)

            # Remove the rejecting driver from the trip group
            await self.channel_layer.group_discard(
                group=errand_id,
                channel=self.channel_name
            )
            await self.channel_layer.group_send(
                    group=f'agent_{rejecting_agent.id}',
                    message={
                        'type': 'echo.message',
                        'data': "Errand rejected succesfully"
                    }
                )
            new_nearby_agent = await self._get_nearest_agent()
            agent_id = new_nearby_agent['user']['id']
            print(new_nearby_agent)
            print("check")
            print(new_nearby_agent)
            
            await self.channel_layer.group_send(
                    group=f'agent_{agent_id}',
                    message={
                        'type': 'errand.requested',
                        'data': errand_data
                    }
                )
            await self.channel_layer.group_send(
            group=errand_id,
            message={
                'type': 'errand.resent',
                'data': errand_data,
                'agent':new_nearby_agent
            }
            )

            return
            
        if errand.status == 'ACCEPTED':
            rejecting_agent = self.scope['user']
                # Add driver to the trip group.
            await self.channel_layer.group_add(
                group=errand_id,
                channel=self.channel_name
            )
            

            # Send update to rider.
        await self.channel_layer.group_send(
            group=errand_id,
            message={
                'type': 'errand.accepted',
                'data': errand_data,
            }
        )

        '''await self.send_json({
            'type': 'errand.' + errand_data.status,
            'data': errand_data
        })'''

    async def complete_routine_errand(self, message):
        data = message.get('data')
        errand = await self._update_errand(data)
        #room = await self._update_room(data)
        errand_id = f'errand_{errand.id}'
        errand_data = await self._get_errand_data(errand)

        '''nearby_driver = await self._get_nearest_driver(pickup_lat, pickup_long)

        if nearby_driver:
            distance = calculate_distance(pickup_lat, pickup_long, float(nearby_driver.current_lat), float(nearby_driver.current_long))
            max_distance = 5.0'''
        
        if errand:
            nearby_agents = await self._get_nearest_agents()
            print("check")
            print(nearby_agents)

            if nearby_agents:
                for nearby_agent in nearby_agents:
                    await self.channel_layer.group_send(
                    group=f'agent_{nearby_agent.id}',
                    message={
                        'type': 'errand.requested',
                        'data': errand_data
                    }
                    )
            #print(nearby_driver)
            # Add rider to trip group.
            await self.channel_layer.group_add(
                group=f'errand_{errand.id}',
                channel=self.channel_name
            )

            await self.send_json({
                'type': 'errand.created',
                'data': errand_data,
            })
    
    async def send_virtual_errand(self, message):
        data = message.get('data')
        print(data)
        agent = data['agent']
        print(agent)
        errand_id = data['id']
        print(errand_id)
        '''errand = await self._update_errand(data)
        #room = await self._update_room(data)
        errand_id = f'errand_{errand.id}'''
        errand_data = await self._get_errand_by_id(errand_id)


        await self.channel_layer.group_send(
            group=f'agent_{agent}',
            message={
                'type': 'errand.requested',
                'data': errand_data
            }
            )
            #print(nearby_driver)
            # Add rider to trip group.
        await self.channel_layer.group_add(
                group=f'errand_{errand_id}',
                channel=self.channel_name
            )

        await self.send_json({
                'type': 'errand.sent',
                'data': errand_data,
            })
            

from uuid import UUID
from django.core.serializers.json import DjangoJSONEncoder

class UUIDEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

class ChatConsumer(WebsocketConsumer):
    @database_sync_to_async
    def _get_message_data(self, message):
        return NestedMessageSerializer(message).data

    def connect(self):
        print("here")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        # parse the json data into dictionary object
        text_data_json = json.loads(text_data)

        # Send message to room group
        chat_type = {"type": "chat_message"}
        return_dict = {**chat_type, **text_data_json}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            return_dict,
        )

    # Receive message from room group
    def chat_message(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")
        message, attachment = (
            text_data_json["message"],
            text_data_json.get("attachment"),
        )

        conversation = Conversation.objects.get(errand=(self.room_name))
        sender = self.scope['user']
        _message = None

        # Attachment
        if attachment:
            file_str, file_ext = attachment["data"], attachment["format"]

            file_data = ContentFile(
                base64.b64decode(file_str), name=f"{secrets.token_hex(8)}.{file_ext}"
            )
            _message = Message.objects.create(
                sender=sender,
                attachment=file_data,
                text=message,
                conversation_id=conversation,
            )
        else:
            _message = Message.objects.create(
                sender=sender,
                text=message,
                conversation_id=conversation,
            )
        serializer = NestedMessageSerializer(instance=_message)
        message_data = self._get_message_data(_message)
        
        # Send message to WebSocket with custom JSON encoder
        serialized_data = json.dumps(serializer.data, cls=UUIDEncoder)
        self.send(text_data=serialized_data)

