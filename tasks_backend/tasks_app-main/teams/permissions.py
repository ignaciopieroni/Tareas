# teams/permissions.py
from rest_framework.permissions import BasePermission
from typing import Optional
from django.shortcuts import get_object_or_404

from common.permissions import RoleResolver
from .models import Team, TeamMembership

resolver = RoleResolver()


def _get_team_from_view_kwargs(view) -> Optional[Team]:
    kw = getattr(view, "kwargs", {}) or {}
    team_id = kw.get("team_id")
    if team_id:
        try:
            return Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return None
    return None


class TeamObjectPermission(BasePermission):
    """
    Object-level permission for actions on a Team instance.
    Permite si el usuario tiene role 'organization_admin' sobre la org del team
    o 'team_admin' sobre el team.
    (has_permission delega a RoleRequiredPermission para checks por método.)
    """

    def has_object_permission(self, request, view, obj):
        # obj expected to be a Team instance
        if not isinstance(obj, Team):
            obj = _get_team_from_view_kwargs(view)
            if obj is None:
                return False
        return resolver.has_any_role(request.user, obj, {'organization_admin', 'team_admin'})


class TeamMembershipObjectPermission(BasePermission):
    """
    Object-level permission for actions on a TeamMembership instance.
    Permite si el usuario es organization_admin sobre el team OR team_admin del team.
    """

    def has_object_permission(self, request, view, obj):
        # obj can be TeamMembership or Team
        if isinstance(obj, TeamMembership):
            team = obj.team
        else:
            team = _get_team_from_view_kwargs(view)
            if team is None:
                return False
        return resolver.has_any_role(request.user, team, {'organization_admin', 'team_admin'})
