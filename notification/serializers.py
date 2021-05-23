from django.contrib.auth.models import User
from rest_framework import serializers
from fcm_django.models import FCMDevice
from notification.models import Notification, NotificationStatus

class UserSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='notification:user-detail')

    class Meta:
        model = User
        fields = ['url', 'id', 'username','password']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class FCMDeviceSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='notification:fcm-device-detail')
    
    class Meta:
        model = FCMDevice
        fields = '__all__'       

class MessageSerializer(serializers.Serializer):

    title = serializers.CharField(max_length = 500)
    message = serializers.CharField(required = False)
    extra_data = serializers.JSONField(required = False)
    start_time = serializers.DateTimeField(required = False)
    end_time = serializers.DateTimeField(required = False)

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True)
    

class NotificationSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='notification:notification-detail')
    sender_name = serializers.SerializerMethodField('get_sender_name')
    # recipients
    class Meta:
        model = Notification
        fields = '__all__'

    def get_sender_name(self,obj):
        return obj.sender.username

class NotificationStatusSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name = 'notification:user-notification-detail')
    notification = NotificationSerializer(read_only = True)
    
    class Meta:
        model = NotificationStatus
        fields = '__all__'

    def to_representation(self, obj):
        data = super().to_representation(obj)
        # data is your serialized instance
        data.get('notification').pop('receivers')
        print(data["notification"]["sender"]) 
        return data

    