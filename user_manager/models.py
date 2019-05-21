from django.db import models


class App(models.Model):
    endpoint = models.URLField(verbose_name='Endpoint')
    app_id = models.CharField(max_length=50, verbose_name='App unique ID', unique=True, editable=False)
    app_name = models.CharField(max_length=100, verbose_name='App name', blank=True, editable=False, default='')
    roles = models.TextField(editable=False, verbose_name='Roles (Texto plano)', blank=True, default='')

    def __str__(self):
        return self.app_id

    class Meta:
        verbose_name = 'App'
        verbose_name_plural = 'Apps'

    def save(self, *args, **kwargs):
        from user_manager.auth0utils import get_app_data
        get_app_data(self)
        return super().save(*args, **kwargs)


class Profile(models.Model):
    name = models.CharField(max_length=300, verbose_name='Nombre')
    apps = models.ManyToManyField(App, verbose_name='Apps que pertenecen a este perfil')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'


class AppRole(models.Model):
    app = models.ForeignKey(App, models.PROTECT, verbose_name='App')
    name = models.CharField(max_length=150, verbose_name='Nombre')

    def __str__(self):
        return f'{self.app} {self.name}'

    class Meta:
        verbose_name = 'Rol en la app'
        verbose_name_plural = 'Roles en la app'
