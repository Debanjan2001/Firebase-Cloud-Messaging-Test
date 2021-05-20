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
        fields = ['url', 'id', 'username','email']


class FCMDeviceSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='notification:fcm-device-detail')
    user = HyperlinkedRelatedField(
        view_name='notification:user-detail',
        read_only=True,
    )
    
    class Meta:
        model = FCMDevice
        fields = '__all__'
        # lookup_field = 'pk'
        # lookup_url_kwarg = 'pk'
# 
    # def get_url(self,object):
    #     url = '{}{}'.format(self.context['request'].META['HTTP_HOST'],reverse('notification:fcm-device-detail',kwargs = {'pk' : object.pk}))
    #     return url.format(type = serializers.Field)


class MessageSerializer(serializers.Serializer):

    title = serializers.CharField()
    message = serializers.CharField()
    extra_data = serializers.JSONField(required = False)
    start_time = serializers.DateTimeField(required = False)
    end_time = serializers.DateTimeField(required = False)