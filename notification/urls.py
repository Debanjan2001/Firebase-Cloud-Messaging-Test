from django.contrib import admin
from django.urls import path,include
from notification import views

app_name = 'notification'

urlpatterns = [
    path('', views.api_root),
    path('users/', views.UserList.as_view(),name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(),name='user-detail'),
    path('fcm_devices/',views.FCMDeviceList.as_view(),name = 'fcm-device-list'),
    path('fcm_devices/<int:pk>',views.FCMDeviceDetail.as_view(),name = 'fcm-device-detail'),
    path('send_message/',views.PostMessage.as_view(),name = 'send-message'),
]
