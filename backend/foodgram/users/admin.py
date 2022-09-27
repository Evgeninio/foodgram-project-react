from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email'
    )
    search_fields = ('username', 'email', )
    list_filter = ('username', )
    empy_value_display = '-пусто-'


admin.site.register(CustomUser, CustomUserAdmin)
