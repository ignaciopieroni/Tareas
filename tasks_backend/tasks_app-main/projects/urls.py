from django.urls import path
from .views import (
    PersonalProjectListCreateView,
    PersonalProjectDetailView,
    OrgProjectListCreateView,
    OrgProjectDetailView,
    ProjectUserMembershipListCreateView,
    ProjectUserMembershipDetailView,
    ProjectTeamMembershipListCreateView,
    ProjectTeamMembershipDetailView,
)

urlpatterns = [
    # Proyectos personales 
    path('projects/', PersonalProjectListCreateView.as_view(), name='personal-projects'),
    path('projects/<int:project_id>/', PersonalProjectDetailView.as_view(), name='personal-project-detail'),

    # Proyectos organizacionales 
    path('organizations/<int:org_id>/projects/', OrgProjectListCreateView.as_view(), name='org-projects'),
    path('organizations/<int:org_id>/projects/<int:project_id>/', OrgProjectDetailView.as_view(), name='org-project-detail'),

    # Miembros de proyectos organizacionales 
    path('organizations/<int:org_id>/projects/<int:project_id>/members/', ProjectUserMembershipListCreateView.as_view(),name='project-user-members'),
    path('organizations/<int:org_id>/projects/<int:project_id>/members/<int:user_org_membership_id>', ProjectUserMembershipDetailView.as_view(),name='project-user-members'),
    path('organizations/<int:org_id>/projects/<int:project_id>/teams/', ProjectTeamMembershipListCreateView.as_view(), name='project-team-members'),
    path('organizations/<int:org_id>/projects/<int:project_id>/teams/<int:team_id>', ProjectTeamMembershipDetailView.as_view(), name='project-team-members'),
]
