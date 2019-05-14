from django.contrib import admin

from user_manager.models import App, Profile


class ProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ('apps',)


admin.site.register(App)
admin.site.register(Profile, ProfileAdmin)
