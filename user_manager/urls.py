from django.urls import path

from user_manager import views

app_name = 'user_manager'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('view-user', views.ViewUser.as_view(), name='view-user'),
    path('create-user', views.CreateUser.as_view(), name='create-user'),
    path('delete-user', views.DeleteUser.as_view(), name='delete-user'),
    path('reset-password', views.ResetPassword.as_view(), name='reset-password'),

    path('reportes', views.ReportsView.as_view(), name='reports'),
    path('login-log', views.LoginLogView.as_view(), name='login-log'),
    path('descargar-reporte-login-logs', views.DownloadLoginLogReportView.as_view(), name='download-login-logs-report')
]
