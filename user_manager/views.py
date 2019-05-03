from django.db.models import Value, BooleanField
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.safestring import mark_safe
from django.views import View

from user_manager.auth0utils import get_all_users, get_user_by_username
from user_manager.models import App


class Index(View):
    def get(self, request):
        users = get_all_users()
        return render(request, 'user_manager/01-index.html', {
            'users': mark_safe(users)
        })


class ViewUser(View):
    def get(self, request):
        username = request.GET.get('username', None)
        if username:
            data = get_user_by_username(username)
            return render(request, 'user_manager/02-user.html', {
                'data': mark_safe(data),
                'apps': list(App.objects.annotate(selected=Value(False, output_field=BooleanField())).values())
            })
        return redirect('user_manager:index')
