from django.urls import path
from .views import RoleListView, RoleDetailView

urlpatterns = [
    path('roles/', RoleListView.as_view(), name='roles-list'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='roles-detail'),
]