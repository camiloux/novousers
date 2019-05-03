from django.urls import path

from user_manager import views

app_name = 'user_manager'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('view-user', views.ViewUser.as_view(), name='view-user'),
]
