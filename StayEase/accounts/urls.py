from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import profile_view
from .views import logout_view

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/<uuid:token>/", views.reset_password, name="reset_password"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/pdf/", views.download_terms_pdf, name="download_terms_pdf"),
    path("privacy/pdf/", views.download_privacy_pdf, name="download_privacy_pdf"),
    path("logout/", views.logout_view, name="logout"),
    path('profile/', profile_view, name='profile'),
    path('settings/', views.edit_profile, name='settings'),
    path("notifications/read/", views.mark_notifications_read, name="mark_notifications_read"),
]
