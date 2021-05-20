from datetime import datetime, time, timedelta
from django.shortcuts import render
from fcm_django.models import FCMDevice
import rest_framework
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.views import APIView
from notification.serializers import FCMDeviceSerializer, MessageSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.renderers import JSONRenderer
import io
from rest_framework.parsers import JSONParser

# Create your views here.

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('notification:user-list', request=request, format=format),
        'fcm-devices': reverse('notification:fcm-device-list',request=request,format=format),
        'send-message': reverse('notification:send-message',request=request,format=format),
    })

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class FCMDeviceList(generics.ListCreateAPIView):
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer

class FCMDeviceDetail(generics.RetrieveUpdateDestroyAPIView):
    # queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'


    def get_queryset(self):
        return FCMDevice.objects.filter(pk = self.kwargs['pk'])

        # for i in q:
        #     print(i.registration_id)
        #     if i.registration_id == self.kwargs['registration_id']:
        #         print(True)
        #         return i
        #     else:
        #         print(False)
        #     print(i)

        return q

class PostMessage(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        sample = {
                "title": "sample_title (This is Required)", 
                "message": "sample_msg (This is Required)",
                "start_time" : str(datetime.now()) + " (Optional.You may not provide it)",
                "end_time" : str(datetime.now()+timedelta(1)) + " (Optional.You may not provide it)",
                "extra_data": { 
                    "data_field1": "data1 (Optional.You may not provide it)",
                    "data_field2": "data2 (Optional.You may not provide it)",
                }
        }
        serializer = MessageSerializer(sample)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            json = JSONRenderer().render(serializer.data)
            stream = io.BytesIO(json)
            data = JSONParser().parse(stream)
            # print(data)
            push_notify(data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def push_notify(data):
    title = data.get('title','')
    message = data.get('message','')
    start_time = data.get('start_time',None)
    end_time = data.get('end_time',None)
    extra_data = data.get('extra_data',None)

    time_to_live = 28*3600*24

    # work in progress
    # if end_time is not None:
    #     # time_to_live = datetime.parse(end_time) - start_time
    #     print(time_to_live)
    # print(title)
    
    devices = FCMDevice.objects.filter(active = True)

    devices.send_message(title = title,message = message)
        