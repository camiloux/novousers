import json
from uuid import uuid4

from django.contrib import messages
from django.shortcuts import render, redirect

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import View

from user_manager.auth0utils import get_all_users, get_user_by_username, DEFAULT_DB_CONNECTION, create_user, \
    patch_user, delete_user
from user_manager.utils import get_apps_list, get_profiles


class Login(View):
    def get(self, request):
        return redirect('/')


class Index(View):
    def get(self, request):
        users, code = get_all_users()
        return render(request, 'user_manager/modules/admin/01-user-list.html', {
            'users': mark_safe(users), 'profiles': get_profiles(), 'apps': get_apps_list()
        })


class ViewUser(View):
    def get(self, request):
        username = request.GET.get('user_id', None)
        if username:
            data, code = get_user_by_username(username)
            profiles = get_profiles()
            return render(request, 'user_manager/modules/admin/02-user.html', {
                'data': mark_safe(data), 'apps': get_apps_list(), 'profiles': profiles
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
            return redirect(f'{request.path}?user_id={user_id}')

        response, status = patch_user(json.dumps(json_data), user_id)
        if status == 200:
            messages.add_message(request, messages.SUCCESS, 'Usuario actualizado', extra_tags='alert-success')
        else:
            messages.add_message(request, messages.ERROR, f'Ocurrió un error: {response}', extra_tags='alert-danger')

        return redirect(f'{request.path}?user_id={user_id}')


class DeleteUser(View):
    def post(self, request):
        user_id = request.POST.get('user_id')
        response, status = delete_user(user_id)
        if status == 204:
            messages.add_message(request, messages.SUCCESS, 'Usuario eliminado', extra_tags='alert-success')
        else:
            messages.add_message(request, messages.ERROR, f'Ocurrió un error: {response}', extra_tags='alert-danger')
        return redirect('user_manager:index')


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
        response, status = create_user(json.dumps(json_data))
        result = json.loads(response)
        if status == 201:
            messages.add_message(request, messages.SUCCESS, 'Usuario creado', extra_tags='alert-success')
        else:
            messages.add_message(request, messages.ERROR, f'Ocurrió un error: {response}', extra_tags='alert-danger')
        return redirect(f"{reverse('user_manager:view-user')}?user_id={result['user_id']}")
