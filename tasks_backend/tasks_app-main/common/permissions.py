from typing import Set, Any, Optional
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

from organizations.models import Organization, OrganizationMembership
from teams.models import Team, TeamMembership
from projects.models import Project, ProjectUserMembership, ProjectTeamMembership
from tasks.models import Task, TaskUserMembership, TaskTeamMembership

User = get_user_model()


# --------------------------
# RoleResolver
# --------------------------
class RoleResolver:
    """
    Resolve los nombres de roles (Role.name) que tiene `user` sobre una instancia
    de Organization | Team | Project | Task.
    """

    def get_roles_for_organization(self, user: User, organization: Organization) -> Set[str]:
        roles: Set[str] = set()
        org_mem = OrganizationMembership.objects.filter(user=user, organization=organization).first()
        if org_mem:
            roles.add(org_mem.role.name)
        return roles

    def get_roles_for_team(self, user: User, team: Team) -> Set[str]:
        roles: Set[str] = set()
        org_mem = OrganizationMembership.objects.filter(user=user, organization=team.organization).first()
        if not org_mem:
            return roles
        tm = TeamMembership.objects.filter(team=team, user=org_mem).select_related('role').first()
        if tm:
            roles.add(tm.role.name)
        # organization_admin implicit
        if org_mem.role.name == 'organization_admin':
            roles.add('organization_admin')
        return roles

    def get_roles_for_project(self, user: User, project: Project) -> Set[str]:
        roles: Set[str] = set()
        # personal project -> owner semantic
        if project.organization is None:
            if project.owner_id == getattr(user, "id", None):
                roles.add('owner')
            return roles

        org_mem = OrganizationMembership.objects.filter(user=user, organization=project.organization).first()
        if not org_mem:
            return roles

        # direct user membership
        pu = ProjectUserMembership.objects.filter(project=project, user=org_mem).select_related('role').first()
        if pu:
            roles.add(pu.role.name)

        # roles via teams
        team_ids = list(org_mem.team_memberships.values_list('team_id', flat=True))
        if team_ids:
            pts = ProjectTeamMembership.objects.filter(project=project, team_id__in=team_ids).select_related('role')
            for pt in pts:
                roles.add(pt.role.name)

        # organization_admin implicit
        if org_mem.role.name == 'organization_admin':
            roles.add('organization_admin')

        return roles

    def get_roles_for_task(self, user: User, task: Task) -> Set[str]:
        roles: Set[str] = set()
        project = task.project

        # personal project -> owner semantic
        if project.organization is None:
            if project.owner_id == getattr(user, "id", None):
                roles.add('owner')
            return roles

        org_mem = OrganizationMembership.objects.filter(user=user, organization=project.organization).first()
        if not org_mem:
            return roles

        # direct task user membership
        tum = TaskUserMembership.objects.filter(task=task, user=org_mem).select_related('role').first()
        if tum:
            roles.add(tum.role.name)

        # roles via teams
        team_ids = list(org_mem.team_memberships.values_list('team_id', flat=True))
        if team_ids:
            ttm_qs = TaskTeamMembership.objects.filter(task=task, team_id__in=team_ids).select_related('role')
            for ttm in ttm_qs:
                roles.add(ttm.role.name)

        # organization_admin implicit
        if org_mem.role.name == 'organization_admin':
            roles.add('organization_admin')

        # include project-level roles (useful in some checks)
        roles.update(self.get_roles_for_project(user, project))
        return roles

    def get_roles_for_object(self, user: User, obj: Any) -> Set[str]:
        if isinstance(obj, Organization):
            return self.get_roles_for_organization(user, obj)
        if isinstance(obj, Team):
            return self.get_roles_for_team(user, obj)
        if isinstance(obj, Project):
            return self.get_roles_for_project(user, obj)
        if isinstance(obj, Task):
            return self.get_roles_for_task(user, obj)
        return set()

    def has_any_role(self, user: User, obj: Any, required_roles: Set[str]) -> bool:
        if not required_roles:
            return True
        roles = self.get_roles_for_object(user, obj)
        return bool(set(required_roles) & roles)

    def has_role(self, user: User, obj: Any, role: str) -> bool:
        return self.has_any_role(user, obj, {role})


# --------------------------
# RoleRequiredPermission
# --------------------------
class RoleRequiredPermission(BasePermission):
    """
    Lee `view.roles_required` (dict: METHOD -> set(role_names)).
    Este permiso **solo** evalúa en has_object_permission usando la instancia que
    la view debe pasar a `check_object_permissions(request, obj)`.
    has_permission devuelve True para permitir que la view decida cuándo llamar
    a la comprobación por objeto.
    """

    def __init__(self):
        self.resolver = RoleResolver()

    def _required_for_method(self, view, method: str) -> Optional[Set[str]]:
        roles_map = getattr(view, 'roles_required', None) or {}
        return roles_map.get(method.upper())

    def has_permission(self, request, view):
        # Siempre permitir; la view debe llamar a check_object_permissions(request, obj)
        # cuando necesite validar roles sobre una instancia.
        return True

    def has_object_permission(self, request, view, obj):
        required = self._required_for_method(view, request.method)
        if required is None:
            return True
        if not required:
            return True
        return self.resolver.has_any_role(request.user, obj, required)
