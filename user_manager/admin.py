from django.contrib import admin

from user_manager.models import App, Profile


class AppAdmin(admin.ModelAdmin):
    readonly_fields = ('app_id', 'app_name', 'roles')

    list_display = ('app_id', 'app_name', 'endpoint')
    list_display_links = ('app_id', 'app_name')


class ProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ('apps',)


admin.site.register(App, AppAdmin)
admin.site.register(Profile, ProfileAdmin)
