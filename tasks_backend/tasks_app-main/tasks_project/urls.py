from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps
    path('api/v1/', include('roles.urls')),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('organizations.urls')),
    path('api/v1/', include('invitations.urls')),
    path('api/v1/', include('teams.urls')),
    path('api/v1/', include('projects.urls')),
    path('api/v1/', include('tasks.urls')),
]
