# projects/permissions.py
from typing import Optional
from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404

from common.permissions import RoleResolver
from .models import Project, ProjectUserMembership, ProjectTeamMembership

resolver = RoleResolver()


def _get_project_from_view_kwargs(view) -> Optional[Project]:
    kw = getattr(view, "kwargs", {}) or {}
    project_id = kw.get("project_id") or kw.get("pk")
    if project_id:
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None
    return None


class ProjectObjectPermission(BasePermission):
    """
    Object-level permission for Project actions.
    - Personal project: owner has full access.
    - Org project: organization_admin OR project_admin have full access.
    This class is intended for PATCH/DELETE and other object-level checks.
    """

    def has_object_permission(self, request, view, obj):
        # resolve object if needed
        project = obj if isinstance(obj, Project) else _get_project_from_view_kwargs(view)
        if project is None:
            return False

        # personal project -> owner only
        if project.organization is None:
            return getattr(project, 'owner_id', None) == getattr(request.user, 'id', None)

        # org project -> org_admin OR project_admin
        return resolver.has_any_role(request.user, project, {'organization_admin', 'project_admin'})


class ProjectMembershipObjectPermission(BasePermission):
    """
    Object-level permission for managing project memberships (users / teams).
    Allows organization_admin or project_admin on the project.
    """

    def has_object_permission(self, request, view, obj):
        # obj could be ProjectUserMembership/ProjectTeamMembership or Project
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = _get_project_from_view_kwargs(view)
            if project is None:
                return False

        return resolver.has_any_role(request.user, project, {'organization_admin', 'project_admin'})
