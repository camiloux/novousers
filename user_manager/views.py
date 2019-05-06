import json
from uuid import uuid4

from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import View

from user_manager.auth0utils import get_all_users, get_user_by_username, DEFAULT_DB_CONNECTION, create_user, patch_user
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
        try:
            json_data = json.loads(request.POST.get('user_data'))
            user_id = json_data['user_id']
            del json_data['username']
            del json_data['user_id']
            del json_data['email']
            del json_data['email_verified']
        except json.decoder.JSONDecodeError:
            return redirect(request.path)

        result = patch_user(json.dumps(json_data), user_id)
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
        try:
            json_data = json.loads(request.POST.get('user_data'))
            json_data['connection'] = DEFAULT_DB_CONNECTION
            json_data['email_verified'] = False
            json_data['password'] = str(uuid4())
        except json.decoder.JSONDecodeError:
            return redirect(request.path)
        result_json = create_user(json.dumps(json_data))
        result = json.loads(result_json)
        return redirect(f"{reverse('user_manager:view-user')}?user_id={result['user_id']}")
