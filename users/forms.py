import re

from django import forms
from django.contrib.auth import authenticate

from team_finder.service import form_clean_github_url
from users.models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError('Неверный email или пароль')
        return self.cleaned_data

    def get_user(self):
        return self.user


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'avatar': 'Аватар',
            'about': 'О себе',
            'phone': 'Телефон',
            'github_url': 'GitHub',
        }
        widgets = {
            'avatar': forms.FileInput(),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        phone = phone.strip()
        if re.match(r'^8\d{10}$', phone):
            phone = '+7' + phone[1:]
        elif re.match(r'^\+7\d{10}$', phone):
            pass
        else:
            raise forms.ValidationError(
                'Номер телефона должен быть в формате'
                '8XXXXXXXXXX или +7XXXXXXXXXX'
                )
        if User.objects.filter(phone=phone).exclude(pk=self.instance.pk
                                                    if self.instance
                                                    else None).exists():
            raise forms.ValidationError(
                'Пользователь с таким телефоном уже существует'
                )
        return phone

    def clean_github_url(self):
        return form_clean_github_url(self)


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput,
        label='Старый пароль'
        )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Новый пароль'
        )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label='Подтверждение пароля'
        )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old = self.cleaned_data.get('old_password')
        if not self.user.check_password(old):
            raise forms.ValidationError('Старый пароль введён неверно')
        return old

    def clean(self):
        new1 = self.cleaned_data.get('new_password1')
        new2 = self.cleaned_data.get('new_password2')
        if new1 and new2 and new1 != new2:
            raise forms.ValidationError('Новые пароли не совпадают')
        return self.cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
