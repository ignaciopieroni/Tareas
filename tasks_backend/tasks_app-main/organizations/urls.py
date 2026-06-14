from django.urls import path
from .views import (
    OrganizationListCreateView,
    OrganizationDetailView,
    OrganizationMembershipListView,
    OrganizationMembershipDetailView,
    OrganizationInvitationListCreateView
)

urlpatterns = [
    # Organizations
    path('organizations/', OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('organizations/<int:org_id>/', OrganizationDetailView.as_view(), name='organization-detail'),

    # Organization Memberships
    path('organizations/<int:org_id>/members/', OrganizationMembershipListView.as_view(), name='organization-members-list'),
    path('organizations/<int:org_id>/members/<int:user_id>/', OrganizationMembershipDetailView.as_view(), name='organization-member-detail'),

    # Organization Invitations (GET/POST dentro de la org)
    path('organizations/<int:org_id>/invitations/', OrganizationInvitationListCreateView.as_view(), name='organization-invitation-list-create'),
]
