from datetime import datetime, time, timedelta
import notification
from notification.models import Notification, NotificationStatus
from django.core.exceptions import ObjectDoesNotExist
from fcm_django.models import FCMDevice
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.views import APIView
from notification.serializers import FCMDeviceSerializer, LoginSerializer, MessageSerializer, NotificationSerializer, NotificationStatusSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from django.contrib.auth import authenticate,login, logout
import hashlib
from rest_framework import pagination

class CustomPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

def device_id_generator(token):
    encrypted_token = token.encode()
    token_hash = hashlib.sha256(encrypted_token)
    hex_device_id = token_hash.hexdigest()
    return hex_device_id 

# Create your views here.

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'login': reverse('notification:user-login', request=request, format=format),
        'logout': reverse('notification:user-logout', request=request, format=format),
        'users': reverse('notification:user-list', request=request, format=format),
        'fcm-devices': reverse('notification:fcm-device-list',request=request,format=format),
        'send-message': reverse('notification:send-message',request=request,format=format),
        'check-registration' : reverse('notification:check-registration',request=request,format=format),
        'notifications':reverse('notification:notification-list',request=request,format=format),
        'user-notifications': reverse('notification:user-notification-list',request=request,format=format),
        'mark-notification(s)-as-read': reverse('notification:mark-notification-as-read',request=request,format=format),
    })

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class FCMDeviceList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer

    def perform_create(self, serializer):
        device_name = self.request.META.get('HTTP_USER_AGENT','')
        device_id = device_id_generator(self.request.data.get('registration_id',''))
        serializer.save(name = device_name, device_id = device_id,user = self.request.user,active = True)

class FCMDeviceDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    # queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer

    def get_queryset(self):
        return FCMDevice.objects.filter(pk = self.kwargs['pk'])


class PostMessage(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        sample = {
                "title": "sample_title (This is Required)", 
                "message": "sample_msg (If not given, Empty msg will be taken)",
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
            data = serializer.data
            # print(serializer.data)
            send_notification(data,request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_notification(data,sender):
    title = data.get('title','')
    message = data.get('message','')
    start_time = data.get('start_time',None)
    end_time = data.get('end_time',None)
    extra_data = data.get('extra_data',None)

    time_to_live = 1800

    if start_time is not None:
        start_time = datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%S%z")
        start_time = datetime.strftime(start_time,"%c")
        # print(end_time)
        message = message + f". Your class starts at {start_time}"
    
    if end_time is not None:
        end_time = datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%S%z")
        end_time = datetime.strftime(end_time,"%c")
        # print(end_time)
        message = message + f". Your class ends at {end_time}"
        time_to_live = end_time - start_time

    # work in progress
    # if end_time is not None:
    #     time_to_live = datetime.parse(end_time) - start_time
    #     # print(time_to_live)
    
    devices = FCMDevice.objects.filter(active = True).exclude(id = sender.id)
    # print(devices)

    receivers = User.objects.all().exclude(id = sender.id)
    # print(len(receivers))
    notification = Notification.objects.create(
        title = title,
        content = message,
        sender = sender,
    )
    notification.receivers.set(receivers)
    notification.save()

    # print(notification)

    notification_status_objects = [
        NotificationStatus(
            notification = notification,
            recipient = receiver
        )
        for receiver in receivers
    ]

    NotificationStatus.objects.bulk_create(notification_status_objects)

    devices.send_message(
        title = title,
        body = message,
        icon = 'https://play-lh.googleusercontent.com/vJhJczbXkqCYkEVPSe6It2k-KqhlD0dDNAZ5txf7ZXhwdtAjcU3BAzbXF3BWwnKpeKg=s200',
        click_action = 'api/user_notifications',
        time_to_live = time_to_live
    )


class CheckRegistration(APIView):

    def get(self, request, format=None):

        reg_id = request.query_params.get('reg_id',None)
        hh = hash(reg_id)
        print(hh)
        if reg_id is None:
            sample = {"SAMPLE GET CALL": "root/api/check_registration?reg_id=abcdef"}
            return Response(sample,status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

        is_registered = False
        try:
            FCMDevice.objects.get(registration_id = reg_id,active = True)
            print("found")
            # assert(myId == reg_id)
            is_registered = True
        except ObjectDoesNotExist:
            pass

        return Response({"is_registered": is_registered},status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    
    serializer_class = LoginSerializer
    def post(self, request, format=None):
        serializer = LoginSerializer(data = request.data)
        if serializer.is_valid():
            username = serializer.data.get('username')
            password = serializer.data.get('password')
            user = authenticate(username = username, password = password)

            if user is not None:
                login(request,user)
                return Response(data={'status':'Successfully Logged in!'}, status= status.HTTP_202_ACCEPTED)
            else:
                return Response(data={'status':'Username or password is wrong'}, status= status.HTTP_401_UNAUTHORIZED)

        return Response(data = serializer.errors, status= status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):

    def get(self, request, format=None):
        if request.user.is_authenticated:
            print(request.user)
            logout(request)
            response_data = {"status" : "Successfully Logged out!"}
            return Response(data=response_data, status= status.HTTP_200_OK)

        return Response(data={"status": "User is not logged in!"}, status=status.HTTP_400_BAD_REQUEST)
    

class NotificationList(generics.ListCreateAPIView):
    pagination_class = CustomPagination
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class NotificationDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    # queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(pk = self.kwargs['pk'])


class UserNotificationPagination(pagination.PageNumberPagination):

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10

    def get_paginated_response(self, data,unread_messages):
        return Response({
            'unread_messages': unread_messages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })

class UserNotificationList(APIView):

    permission_classes = [IsAuthenticated]
    
    # def get_queryset(self):
    #     return self.request.user.notification_status.all().order_by('is_read','-notification__created_on')

    def get(self, request, *args, **kwargs):

        user = request.user

        if user.is_authenticated is False:
            return Response(data = {"detail":"Username/password not provided"},status=status.HTTP_401_UNAUTHORIZED)

        paginator = UserNotificationPagination()
        notification_status_objects = self.request.user.notification_status.all().order_by('is_read','-notification__created_on')

        paginated_notifications = paginator.paginate_queryset(notification_status_objects,request)
        context = { "request": request }
        print(paginated_notifications)
        notification_status_serializer = NotificationStatusSerializer( paginated_notifications,many=True,context = context)
        
        unread_messages = notification_status_objects.filter(is_read = False).count()
        response = paginator.get_paginated_response(notification_status_serializer.data,unread_messages)
        
        return response

class UserNotificationDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationStatusSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return NotificationStatus.objects.filter(pk = self.kwargs['pk'])


class MarkNotificationAsRead(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request,*args, **kwargs):
        return Response(
            data = {
                "Info": "Sample POST DATA",
                "id": 2,
                "mark_all" : True,
                "Extra info": "Use only one of the two method above",
            },  
            status = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
        )

    def post(self,request,*args, **kwargs):
        user = request.user

        id = request.data.get('id',None)
        mark_all = request.data.get('mark_all',False)

        if id is None and mark_all is False:
            return Response( data = {"details":"Invalid Operation: 'mark_all'/'id' is not given"}, status= status.HTTP_400_BAD_REQUEST )
        
        def set_read_status(obj):
            obj.is_read = True
            return obj

        if mark_all is True:
            notification_status_objects = [
                set_read_status(obj)
                for obj in user.notification_status.all()
            ]
            NotificationStatus.objects.bulk_update(notification_status_objects,['is_read'])
            return Response(data = {"details":"Successful"}, status= status.HTTP_200_OK)

        try:
            notification_status = user.notification_status.get(id = id)
            notification_status.is_read = True
            notification_status.save()
            return Response(data = {"details":"Successful"}, status= status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(data = {"details":"Invalid ID/Notification does not exist"}, status= status.HTTP_200_OK)

        
