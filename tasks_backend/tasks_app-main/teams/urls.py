from django.urls import path
from .views import (
    TeamListCreateView,
    TeamDetailView,
    TeamMembershipListCreateView,
    TeamMembershipDetailView,
)

urlpatterns = [
    # Teams de una organización
    path('organizations/<int:org_id>/teams/', TeamListCreateView.as_view(), name='team-list-create'),
    path('organizations/<int:org_id>/teams/<int:team_id>/', TeamDetailView.as_view(), name='team-detail'),

    # Team Memberships
    path('organizations/<int:org_id>/teams/<int:team_id>/memberships/', TeamMembershipListCreateView.as_view(), name='team-membership-list-create'),
    path('organizations/<int:org_id>/teams/<int:team_id>/memberships/<int:user_org_membership_id>/', TeamMembershipDetailView.as_view(), name='team-membership-detail'),
]
