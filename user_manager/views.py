import json

from django.shortcuts import render, redirect

# Create your views here.
from django.utils.safestring import mark_safe
from django.views import View

from user_manager.auth0utils import get_all_users, get_user_by_username
from user_manager.utils import get_apps_list


class Index(View):
    def get(self, request):
        users = get_all_users()
        return render(request, 'user_manager/01-index.html', {
            'users': mark_safe(users)
        })


class ViewUser(View):
    def get(self, request):
        username = request.GET.get('user_id', None)
        if username:
            data = get_user_by_username(username)
            return render(request, 'user_manager/02-user.html', {
                'data': mark_safe(data), 'apps': get_apps_list()
            })
        return redirect('user_manager:index')

    def post(self, request):
        print(request.POST.get('user_data'))
        return redirect(request.path)


class CreateUser(View):
    def get(self, request):
        user = {
            'username': '',
            'email': '',
            'email_verified': True,
            'app_metadata': {},
            'user_metadata': {}
        }
        data = json.dumps(user)

        return render(request, 'user_manager/02-user.html', {
            'data': mark_safe(data), 'apps': get_apps_list(), 'creating': True
        })

    def post(self, request):
        print(request.POST.get('user_data'))
        return redirect(request.path)
