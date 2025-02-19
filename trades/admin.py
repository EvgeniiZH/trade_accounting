from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Item, Calculation, CalculationItem, CustomUser

# Регистрация стандартных моделей
admin.site.register(Item)
admin.site.register(Calculation)


# Кастомный админ для CalculationItem с использованием raw_id_fields и list_display
class CalculationItemAdmin(admin.ModelAdmin):
    raw_id_fields = ('calculation', 'item')
    list_display = ('calculation', 'item', 'quantity')


# Сначала отписываем старую регистрацию CalculationItem, если она была
try:
    admin.site.unregister(CalculationItem)
except admin.sites.NotRegistered:
    pass

admin.site.register(CalculationItem, CalculationItemAdmin)


# Кастомный админ для CustomUser, наследуемся от UserAdmin и добавляем дополнительные поля
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_admin')
    list_filter = ('is_staff', 'is_active', 'is_admin', 'groups')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_admin', 'groups',
                       'user_permissions'),
        }),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)


# Перерегистрируем CustomUser с нашим классом админки
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

admin.site.register(CustomUser, CustomUserAdmin)
