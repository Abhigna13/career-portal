from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('skills/', views.skills_page, name='skills'),
    path('jobs/', views.job_recommendations_page, name='jobs'),

    path('logout/', views.logout_view, name='logout'),
]