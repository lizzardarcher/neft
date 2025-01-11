# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetDoneView, \
    PasswordResetCompleteView

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", register_user, name="register"),
    path('accounts/password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/',PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),name="password_change_done"),
    path('accounts/password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('accounts/password-reset-done/',PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),name='password_reset_done'),
    path('accounts/password-reset-complete/',PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),name='password_reset_complete'),
]
