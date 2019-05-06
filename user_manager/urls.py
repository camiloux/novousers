from django.urls import path

from user_manager import views

app_name = 'user_manager'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('view-user', views.ViewUser.as_view(), name='view-user'),
    path('create-user', views.CreateUser.as_view(), name='create-user'),
    path('delete-user', views.DeleteUser.as_view(), name='delete-user'),
]
