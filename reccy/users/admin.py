from django.contrib import admin

from .models import UserConfirmation

from django.contrib.auth import get_user_model
User = get_user_model()


class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ('email', 'confirmation_code')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'password',
                    'last_name', 'is_staff', 'is_superuser')


admin.site.register(UserConfirmation, UserConfirmationAdmin)
admin.site.register(User, UserAdmin)
