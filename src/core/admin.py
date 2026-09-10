from django.contrib import admin

from core.models import BarkModel, DogUserModel


@admin.register(DogUserModel)
class DogUserAdmin(admin.ModelAdmin):
    pass


@admin.register(BarkModel)
class BarkAdmin(admin.ModelAdmin):
    pass
