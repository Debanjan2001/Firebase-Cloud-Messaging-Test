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

    # url = serializers.HyperlinkedIdentityField(view_name='notification:fcm-device-detail')
    # notification = serializers.HyperlinkedRelatedField(view_name='notification:fcm-device-detail')
    
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

    class Meta:
        model = Notification
        fields = '__all__'

class NotificationStatusSerializer(serializers.ModelSerializer):

    # notification = serializers.HyperlinkedIdentityField(to = view_name='notification:notification-detail')

    title = serializers.SerializerMethodField('get_title')
    content = serializers.SerializerMethodField('get_content')

    class Meta:
        model = NotificationStatus
        fields = '__all__'

    def get_title(self,obj):
        return obj.notification.title

    def get_content(self,obj):
        return obj.notification.content