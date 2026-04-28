# users/admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.utils.html import format_html

from users.models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput
        )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput
        )

    class Meta:
        model = User
        fields = (
            'email',
            'name',
            'surname',
            'phone',
            'github_url',
            'about'
            )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label='Пароль',
        help_text='Пароли хранятся в хэшированном виде, поэтому вы не можете '
                  'увидеть пароль этого пользователя, но можете изменить его '
                  'с помощью <a href="../password/">этой формы</a>.'
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'surname', 'avatar',
                  'phone', 'github_url', 'about', 'is_active', 'is_staff',
                  'is_superuser', 'groups', 'user_permissions')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'avatar_preview',
        'email',
        'name',
        'surname',
        'phone',
        'is_staff',
        'is_active'
        )
    list_filter = (
        'is_staff',
        'is_active',
        'skills'
        )
    search_fields = (
        'email',
        'name',
        'surname'
        )
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': (
            'name',
            'surname',
            'avatar',
            'phone',
            'github_url',
            'about'
            )}),
        ('Навыки', {'fields': ('skills',)}),
        ('Разрешения', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions'
            )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'name',
                'surname',
                'phone',
                'github_url',
                'about',
                'password1',
                'password2'
                ),
        }),
    )
    filter_horizontal = (
        'skills',
        'groups',
        'user_permissions'
        )

    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40"'
                'height="40"'
                'style="border-radius: 50%;" />',
                obj.avatar.url
                )
        return "—"


admin.site.unregister(Group)
