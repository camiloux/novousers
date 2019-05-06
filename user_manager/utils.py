from django.db.models import Value, BooleanField

from user_manager.models import App


def get_apps_list():
    return list(App.objects.annotate(selected=Value(False, output_field=BooleanField())).values())
