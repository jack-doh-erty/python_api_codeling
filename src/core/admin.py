from django.contrib import admin
from core.models import BarkModel, DogUserModel
from core.models import AuthTokenModel


@admin.register(DogUserModel)
class DogUserAdmin(admin.ModelAdmin):
    pass


@admin.register(BarkModel)
class BarkAdmin(admin.ModelAdmin):
    pass

@admin.register(AuthTokenModel)
class AuthTokenAdmin(admin.ModelAdmin):
    readonly_fields = ("key", "created_at")
