from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import asyncio
from rest_framework import serializers
from .serializers import *
from rest_framework.exceptions import ValidationError

from .models import ErrandTask
from django.core import serializers
from django.contrib.auth import get_user_model

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
    def _get_nearest_agents(self):
        nearest_agents = []
        agents = User.objects.filter(is_agent=True)

        for agent in agents:
            nearest_agents.append(agent)
            print(agent)

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
    def _create_errand(self, data):
        serializer = ErrandTaskSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.create(serializer.validated_data)
        

    @database_sync_to_async
    def _get_errand_data(self, errand):
        return NestedErrandSerializer(errand).data

    @database_sync_to_async
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

            errand_ids = await self._get_errand_ids(user)
            for errand_id in errand_ids:
                await self.channel_layer.group_add(
                        group=f'errand_{errand_id}',
                        channel=self.channel_name
                    )
                print(f'Connection established: Customer for Errand {errand_id}')

            # Convert the map object to a list
            errand_ids_list = list(errand_ids)

            # Connection established for all errands
            print(f'Connection established: Customer for Errands {errand_ids_list}')

            # Accept the connection
            await self.accept()
            
            

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
    async def errand_accepted(self, event):
        # Handle the 'errand.requested' message type here
        # You can send a response back to the client or perform any necessary logic
        await self.send_json({
            'type': 'errand.accepted',
            'data': event['data'],
        })

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type == 'create.errand':
            await self.create_errand(content)
        elif message_type == 'errand.requested':
            await self.echo_message(content)
        elif message_type == 'echo.message':
            await self.echo_message(content)
        elif message_type == 'update.errand':
            await self.update_errand(content)
        elif message_type == 'check.agents':
            await self.get_drivers(content)

    async def update_errand(self, message):
        data = message.get('data')
        errand = await self._update_errand(data)
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

            '''pickup_lat = trip.pick_up_lat
            pickup_long = trip.pick_up_long
            new_nearby_driver = await self._get_nearest_driver_exclude_rejected(pickup_lat, pickup_long, trip.rejected_drivers.all())

            if new_nearby_driver:
                distance = calculate_distance(pickup_lat, pickup_long, float(new_nearby_driver.current_lat), float(new_nearby_driver.current_long))
                max_distance = 5.0

                if distance <= max_distance:
                    # Send a ride request to the new nearest driver
                    await self.channel_layer.group_send(
                        group=f'driver_{new_nearby_driver.id}',
                        message={
                            'type': 'echo.message',
                            'data': trip_data
                        }
                    )


                    # Notify the rider about the new driver
                    await self.send_json({
                        'type': 'echo.message',
                        'data': trip_data
                    })

                    return'''
            new_nearby_agents = await self._get_nearest_agents()
            print("check")
            print(new_nearby_agents)
            for new_nearby_agent in new_nearby_agents:
                await self.channel_layer.group_send(
                        group=f'agent_{new_nearby_agent.id}',
                        message={
                            'type': 'echo.message',
                            'data': errand_data
                        }
                    )


                # Notify the rider about the new driver
                await self.send_json({
                    'type': 'echo.message',
                    'data': errand_data
                })

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

            await self.send_json({
                'type': 'errand.accepted',
                'data': errand_data
            })
