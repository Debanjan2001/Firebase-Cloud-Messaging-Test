from django.contrib.auth.models import User
from rest_framework import renderers
from django.urls import reverse,reverse_lazy
from django.shortcuts import redirect
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.response import Response
from rest_framework import serializers
from fcm_django.models import FCMDevice

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