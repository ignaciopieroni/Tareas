from rest_framework.permissions import BasePermission
from projects.models import Project
from common.permissions import RoleResolver

resolver = RoleResolver()


def _get_project_from_view_kwargs(view):
    kw = getattr(view, "kwargs", {}) or {}
    return Project.objects.filter(id=kw.get("project_id")).first()


class TaskObjectPermission(BasePermission):
    """
    Object-level permissions for editing/deleting a task.
    Personal project: owner only.
    Org project: org_admin or project_admin.
    """

    def has_object_permission(self, request, view, obj):
        project = obj.project if hasattr(obj, 'project') else _get_project_from_view_kwargs(view)
        if project is None:
            return False

        # Personal project -> only owner
        if project.organization is None:
            return project.owner_id == request.user.id

        # Organizational project -> org_admin or project_admin
        return resolver.has_any_role(request.user, project, {'organization_admin', 'project_admin'})


class CanCompleteTask(BasePermission):
    """
    Permissions to mark a task as completed.
    Allowed roles: task_assigned, project_admin, organization_admin
    """

    def has_object_permission(self, request, view, obj):
        project = obj.project if hasattr(obj, 'project') else _get_project_from_view_kwargs(view)
        if project is None:
            return False

        allowed_roles = {'task_assigned', 'project_admin', 'organization_admin'}
        return resolver.has_any_role(request.user, obj, allowed_roles)
