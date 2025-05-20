# -*- encoding: utf-8 -*-
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.middleware.csrf import get_token
from django.views.generic import TemplateView

from .forms import LoginForm, SignUpForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm


class LoginView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if username == '1':
                    return redirect('worker_document_list')
                else:
                    return redirect('dashboard')
            else:
                form.add_error(None, "Неправильный логин или пароль")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


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


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = UserPasswordChangeForm
