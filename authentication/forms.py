# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Логин",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Пароль",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Логин",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Пароль",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Введите пароль еще раз",
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Новый пароль'
    }), label="Новый пароль")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Подтвердить новый пароль'
    }), label="Подтвердить новый пароль")


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Старый пароль'
    }), label='Старый пароль')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Новый пароль'
    }), label="Новый пароль")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Подтвердить новый пароль'
    }), label="Подтвердить новый пароль")