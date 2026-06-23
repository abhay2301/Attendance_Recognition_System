from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
# # app_name='users'w
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    # path('upload-face/', views.upload_face, name='upload_face'),
    
    # Authentication URLs
    path('login/', views.LoginView, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    
]