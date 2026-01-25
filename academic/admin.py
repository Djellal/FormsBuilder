from django.contrib import admin
from .models import Etablissement, Faculte, Domaine


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'adresse']
    search_fields = ['nom']


@admin.register(Faculte)
class FaculteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'etablissement']
    list_filter = ['etablissement']
    search_fields = ['nom']


@admin.register(Domaine)
class DomaineAdmin(admin.ModelAdmin):
    list_display = ['nom', 'faculte']
    list_filter = ['faculte']
    search_fields = ['nom']
