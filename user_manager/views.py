import json
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from novousers.settings import login_logs_collection
from user_manager.auth0utils import get_all_users, get_user_by_user_id, DEFAULT_DB_CONNECTION, create_user, \
    patch_user, delete_user, request_password_reset, update_user_apps, get_all_users_cached, clear_cache, \
    update_cached_user
from user_manager.utils import get_apps_list, get_profiles, get_documents, insert_document, MongoJSONEncoder


class Login(View):
    def get(self, request):
        return render(request, 'user_manager/modules/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            username=username, password=password
        )
        if user:
            login(request, user)
            return redirect('user_manager:index')
        else:
            messages.add_message(request, messages.ERROR, 'Credenciales invalidas', extra_tags='alert-danger')
            return redirect('user_manager:login')


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('user_manager:login')


class AuthView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('user_manager:login')


class Index(AuthView):
    def get(self, request):
        users = get_all_users_cached()
        if not users:
            users = get_all_users()
        return render(request, 'user_manager/modules/admin/01-user-list.html', {
            'users': mark_safe(json.dumps(users)), 'profiles': get_profiles(), 'apps': get_apps_list()
        })


class ViewUser(AuthView):
    def get(self, request):
        username = request.GET.get('user_id', None)
        if username:
            data, code = get_user_by_user_id(username)
            profiles = get_profiles()
            return render(request, 'user_manager/modules/admin/02-user.html', {
                'data': mark_safe(data), 'apps': get_apps_list(), 'profiles': profiles
            })
        return redirect('user_manager:index')

    def post(self, request):
        try:
            user_json = json.loads(request.POST.get('user_data'))
            data, code = get_user_by_user_id(user_json['user_id'])
            original_user = json.loads(data)

            user_id = user_json['user_id']

            if original_user == user_json:
                messages.add_message(request, messages.WARNING, 'No se ha realizado ningín cambio',
                                     extra_tags='alert-warning')
            else:
                to_update_data = {
                    'app_metadata': user_json['app_metadata'], 'user_metadata': user_json['user_metadata']
                }
                response, status = patch_user(to_update_data, user_id)
                update_cached_user(user_id, user_json['app_metadata'], user_json['user_metadata'])

                if status == 200:
                    update_user_apps(user_json, original_user)
                    messages.add_message(request, messages.SUCCESS, 'Usuario actualizado', extra_tags='alert-success')
                else:
                    messages.add_message(request, messages.ERROR, f'Ocurrió un error: {response}',
                                         extra_tags='alert-danger')

        except json.decoder.JSONDecodeError:
            messages.add_message(request, messages.ERROR, 'Error en la solicitud', extra_tags='alert-success')
            return redirect(request.path)

        return redirect(f'{request.path}?user_id={user_id}')


class DeleteUser(AuthView):
    def post(self, request):
        user_id = request.POST.get('user_id')
        response, status = delete_user(user_id)
        clear_cache()
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
        profiles = get_profiles()
        clear_cache()

        return render(request, 'user_manager/modules/admin/02-user.html', {
            'data': mark_safe(data), 'apps': get_apps_list(), 'creating': True, 'profiles': profiles
        })

    def post(self, request):
        try:
            json_data = json.loads(request.POST.get('user_data'))
            json_data['connection'] = DEFAULT_DB_CONNECTION
            json_data['email_verified'] = True
            json_data['password'] = str(uuid4())
        except json.decoder.JSONDecodeError:
            messages.add_message(request, messages.ERROR,
                                 'Se han recibido datos inválidos. Por favor intente de nuevo.',
                                 extra_tags='alert-danger')
            return redirect(request.path)
        response, status = create_user(json_data)
        result = json.loads(response)
        if status == 201:
            messages.add_message(request, messages.SUCCESS, f"Usuario \"{json_data['username']}\" creado",
                                 extra_tags='alert-success')
            request_password_reset(json_data['username'], json_data['email'])
            return redirect('user_manager:create-user')
            # return redirect(f"{reverse('user_manager:view-user')}?user_id={result['user_id']}")
        else:
            messages.add_message(request, messages.ERROR, f'Ocurrió un error: {response}', extra_tags='alert-danger')
            return redirect('user_manager:create-user')


class ResetPassword(AuthView):
    def post(self, request):
        user_id = request.POST.get('user_id')
        if request.POST.get('email') and request.POST.get('username'):
            response, status = request_password_reset(request.POST['username'], request.POST['email'])
            if status == 200:
                messages.add_message(request, messages.SUCCESS,
                                     'Se ha enviado un correo para reestablecer la contraseña',
                                     extra_tags='alert-success')
            else:
                messages.add_message(request, messages.ERROR,
                                     response, extra_tags='alert-danger')
        if user_id:
            return redirect(reverse('user_manager:view-user') + '?user_id=' + user_id)
        return redirect('user_manager:login')


class ReportsView(AuthView):
    def get(self, request):
        return render(request, 'user_manager/modules/admin/03-reports.html', {
            'apps': get_apps_list(),
            'login_logs': mark_safe(json.dumps(get_documents(login_logs_collection, {}), cls=MongoJSONEncoder))
        })


@method_decorator(csrf_exempt, name='dispatch')
class LoginLogView(View):
    def get(self, request):
        return JsonResponse(
            get_documents(login_logs_collection, {}),
            safe=False,
            encoder=MongoJSONEncoder
        )

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        username = body.get('username', '')
        application = body.get('application', '')
        if username and application:
            insert_document(login_logs_collection, {
                'username': username,
                'application': application,
                'date_time': now(),
            })

        return JsonResponse({'status': 'ok'})
