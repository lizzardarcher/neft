# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.middleware.csrf import get_token
from .forms import LoginForm, SignUpForm


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            email = form.cleaned_data.get("email")
            user = authenticate(username=username, password=raw_password)
            token = get_token(request)
            email_subject = 'Registration successful!'
            raw_message = render_to_string('accounts/mail_template.html', {'username': username, 'token': token})
            email_message = strip_tags(raw_message)
            try:
                send_mail(
                    subject=email_subject,
                    message=email_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email])
            except:
                msg = '<span class="badge badge-danger">Возникла проблема с регистрацией, попробуйте позже или обратитесь в поддержку</span>'
            msg = '<span class="badge badge-success">Пользователь успешно зарегистрирован</span>'
            success = True


            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
