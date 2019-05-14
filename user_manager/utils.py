from django.db.models import Value, BooleanField

from user_manager.models import App, Profile


def get_apps_list():
    return list(App.objects.annotate(selected=Value(False, output_field=BooleanField())).values())


def get_profiles():
    qs = Profile.objects.prefetch_related('apps').all()
    profiles_list = []
    for profile in qs:
        profile_dict = {
            'id': profile.id,
            'name': profile.name,
            'apps': list(profile.apps.values('app_id', 'app_name'))
        }
        profiles_list.append(profile_dict)
    return profiles_list
