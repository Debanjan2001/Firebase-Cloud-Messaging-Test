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
    path('check_registration/',views.CheckRegistration.as_view(),name = 'check-registration'),
    path('login/',views.LoginAPIView().as_view(),name = 'user-login'),
    path('logout/',views.LogoutAPIView.as_view(), name = 'user-logout'),
    path('notifications/', views.NotificationList.as_view(),name='notification-list'),
    path('notifications/<int:pk>/', views.NotificationDetail.as_view(),name='notification-detail'),
    path('user_notifications/', views.UserNotificationList.as_view(),name ='user-notification-list'),

]
