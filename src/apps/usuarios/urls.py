from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/cambiar-password/', auth_views.PasswordChangeView.as_view(
        template_name='usuarios/cambiar_password.html',
        success_url=reverse_lazy('usuarios:perfil'),
    ), name='cambiar_password'),
]
