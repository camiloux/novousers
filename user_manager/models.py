from django.db import models


class App(models.Model):
    app_id = models.CharField(max_length=50, verbose_name='App unique ID', unique=True)
    app_name = models.CharField(max_length=100, verbose_name='App name', blank=True, default='')
    endpoint = models.URLField(verbose_name='Endpoint')

    def __str__(self):
        return self.app_id

    class Meta:
        verbose_name = 'App'
        verbose_name_plural = 'Apps'


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
