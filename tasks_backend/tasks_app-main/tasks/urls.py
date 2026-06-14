from django.urls import path
from .views import (
    OrgProjectTaskListCreateView,
    OrgTaskDetailView,
    OrgTaskCompleteView,
    PersonalProjectTaskListCreateView,
    PersonalTaskDetailView,
    PersonalTaskCompleteView,
)

urlpatterns = [
    # Organizacionales
    path('organizations/<int:org_id>/projects/<int:project_id>/tasks/', OrgProjectTaskListCreateView.as_view(), name='org_task_list_create'),
    path('organizations/<int:org_id>/projects/<int:project_id>/tasks/<int:task_id>/', OrgTaskDetailView.as_view(), name='org_task_detail'),
    path('organizations/<int:org_id>/projects/<int:project_id>/tasks/<int:task_id>/complete/', OrgTaskCompleteView.as_view(), name='org_task_complete'),

    # Personales
    path('projects/<int:project_id>/tasks/', PersonalProjectTaskListCreateView.as_view(), name='personal_task_list_create'),
    path('projects/<int:project_id>/tasks/<int:task_id>/', PersonalTaskDetailView.as_view(), name='personal_task_detail'),
    path('projects/<int:project_id>/tasks/<int:task_id>/complete/', PersonalTaskCompleteView.as_view(), name='personal_task_complete'),
]
