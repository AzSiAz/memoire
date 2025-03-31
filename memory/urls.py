from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.memory_list, name='memory_list'),
    path('memory/<uuid:memory_id>/', views.memory_detail, name='memory_detail'),
    path('memory/create/', views.create_memory, name='create_memory'),
    path('memory/search/', views.search_memories, name='search_memories'),
    path('memory/add/', views.memory_add, name='memory_add'),
    # New user profile endpoints
    path('users/', views.user_profile_list, name='user_profile_list'),
    path('users/<str:username>/', views.profile_view, name='profile'),
    path('api/users/', views.user_profile_list_api, name='user_profile_list_api'),
    path('api/users/<str:username>/', views.user_profile_api, name='user_profile_api'),
]
