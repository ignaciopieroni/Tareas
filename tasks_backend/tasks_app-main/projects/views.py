# projects/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Project, ProjectUserMembership, ProjectTeamMembership
from .serializers import ProjectSerializer, ProjectUserMembershipSerializer, ProjectTeamMembershipSerializer
from common.permissions import RoleRequiredPermission, RoleResolver
from .permissions import ProjectObjectPermission, ProjectMembershipObjectPermission
from organizations.models import Organization, OrganizationMembership
from roles.models import Role, Roles, Scopes

resolver = RoleResolver()

# ----------------- Personal Projects -----------------
class PersonalProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': set(),
        'POST': set(),
    }

    def get(self, request):
        """
        Lista los proyectos personales del usuario.
        """
        projects = Project.objects.filter(owner=request.user, is_closed=False)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Crea un nuevo proyecto personal del usuario.
        """
        data = request.data.copy()
        data['owner'] = request.user.id
        serializer = ProjectSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)


class PersonalProjectDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'owner'},
        'PATCH': {'owner'},
        'DELETE': {'owner'},
    }

    def get_object(self, project_id):
        return get_object_or_404(Project, id=project_id)

    def get(self, request, project_id):
        """
        Retorna el proyecto personal del usuario.
        """
        project = self.get_object(project_id)
        self.check_object_permissions(request, project)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, project_id):
        """
        Modifica el proyecto personal del usuario.
        """
        project = self.get_object(project_id)
        self.check_object_permissions(request, project)
        data = request.data.copy()
        data['owner'] = request.user.id
        serializer = ProjectSerializer(project, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(ProjectSerializer(project).data)

    def delete(self, request, project_id):
        """
        Elimina el proyecto personal del usuario.
        """
        project = self.get_object(project_id)
        self.check_object_permissions(request, project)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------- Organizational Projects -----------------
class OrgProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'organization_project_creator', 'organization_team_creator', 'organization_member'},
        'POST': {'organization_admin', 'organization_project_creator'},
    }

    def get(self, request, org_id):
        """
        Si el usuario es 'organization_admin' retorna todos los proyectos de la organizacion.
        Si no es 'organization_admin' retorna los proyectos de los que es miembro.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)

        if resolver.has_role(request.user, org, Roles.ORGANIZATION_ADMIN):
            projects = Project.objects.filter(organization=org, is_closed=False)
        else:
            # Membresía del usuario en org para buscar sus equipos y proyectos
            org_mem = OrganizationMembership.objects.filter(organization=org, user=request.user).first()

            # Proyectos del usuario (con membresia directa)
            direct_project_ids = list(ProjectUserMembership.objects.filter(user=org_mem).values_list('project_id', flat=True))

            # Equipos del usuario
            team_ids = list(org_mem.team_memberships.values_list('team_id', flat=True))

            # Proyectos de equipos del usuario
            team_project_ids = list(ProjectTeamMembership.objects.filter(team_id__in=team_ids).values_list('project_id', flat=True)) if team_ids else []

            # Todos los proyectos del usuario
            project_ids = set(direct_project_ids) | set(team_project_ids)
            if project_ids:
                projects = Project.objects.filter(organization=org, id__in=project_ids, is_closed=False) # org asegura que sean organizacionales
            else:
                projects = Project.objects.none()

        serializer = ProjectSerializer(projects.distinct(), many=True)
        return Response(serializer.data)

    def post(self, request, org_id):
        """
        Crea un nuevo proyecto organizacional del usuario.
        Luego de crear el proyecto agrega al usuario al proyecto con rol 'project_admin' por defecto.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)

        data = request.data.copy()
        data['organization'] = org_id

        serializer = ProjectSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            project = serializer.save()

            org_mem = request.user.organization_membership
            role = Role.objects.filter(scope=Scopes.PROJECT, name=Roles.PROJECT_ADMIN).first()
            ProjectUserMembership.objects.create(project=project, user=org_mem, role=role)

        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)


class OrgProjectDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'project_admin', 'project_member'},
        'PATCH': {'organization_admin', 'project_admin'},
        'DELETE': {'organization_admin', 'project_admin'},
    }

    def get_object(self, org_id, project_id):
        return get_object_or_404(Project, id=project_id, organization_id=org_id)

    def get(self, request, org_id, project_id):
        """
        Retorna el proyecto organizacional.
        """
        project = self.get_object(project_id)
        self.check_object_permissions(request, project)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, org_id, project_id):
        """
        Modifica el proyecto organizacional.
        """
        project = self.get_object(org_id, project_id)
        self.check_object_permissions(request, project)
        data = request.data.copy()
        data['organization'] = org_id
        serializer = ProjectSerializer(project, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(ProjectSerializer(project).data)

    def delete(self, request, org_id, project_id):
        """
        Elimina el proyecto organizacional.
        """
        project = self.get_object(org_id, project_id)
        self.check_object_permissions(request, project)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------- Project Memberships (users / teams) -----------------
class ProjectUserMembershipListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'project_admin'},
        'POST': {'organization_admin', 'project_admin'},
    }

    def get_object(self, org_id, project_id):
        return get_object_or_404(Project, id=project_id, organization_id=org_id)

    def get(self, request, org_id, project_id):
        """
        Lista los usuarios miembros del proyecto organizacional.
        """
        project = self.get_object(org_id, project_id)
        self.check_object_permissions(request, project)
        serializer = ProjectUserMembershipSerializer(project.user_memberships.all(), many=True)
        return Response(serializer.data)

    def post(self, request, org_id, project_id):
        """
        Agrega un usuario miembro de la org al proyecto organizacional.
        Le asigna el rol 'project_member' al usuario por defecto.
        """
        project = self.get_object(org_id, project_id)
        self.check_object_permissions(request, project)
        data = request.data.copy()
        data['project'] = project_id
        data['role'] = Role.objects.filter(scope=Scopes.PROJECT, name=Roles.PROJECT_MEMBER).first().id       
        serializer = ProjectUserMembershipSerializer(data=data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        return Response(ProjectUserMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)
    
class ProjectUserMembershipDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'project_admin'},
        'PATCH': {'organization_admin', 'project_admin'},
        'DELETE': {'organization_admin', 'project_admin'},
    }

    def get_object(self, org_id, project_id, user_org_membership_id):
        return get_object_or_404(ProjectUserMembership, project_id=project_id, user_id=user_org_membership_id)
    
    def get(self, request, org_id, project_id, user_org_membership_id):
        """
        Retorna la membresía del usuario en el proyecto con su rol.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)

        membership = self.get_object(org_id, project_id, user_org_membership_id)

        serializer = ProjectUserMembershipSerializer(membership, context={'project': project})
        return Response(serializer.data)
    
    def patch(self, request, org_id, project_id, user_org_membership_id):
        """
        Modifica la membresía del usuario en el proyecto (sirve para modificar el rol del usuario en el proyecto).
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)

        membership = self.get_object(org_id, project_id, user_org_membership_id)

        data = request.data.copy()
        data['project'] = project_id
        data['user'] = user_org_membership_id
        serializer = ProjectUserMembershipSerializer(membership, data=data, partial=True, context={'project': project})
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        return Response(ProjectUserMembershipSerializer(membership).data)
    
    def delete(self, request, org_id, project_id, user_org_membership_id):
        """
        Elimina al usuario del proyecto.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        membership = self.get_object(org_id, project_id, user_org_membership_id)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProjectTeamMembershipListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'project_admin'},
        'POST': {'organization_admin', 'project_admin'},
    }

    def get_object(self, org_id, project_id):
        return get_object_or_404(Project, id=project_id, organization_id=org_id)

    def get(self, request, org_id, project_id):
        """
        Lista los equipos miembros del proyecto organizacional.
        """
        project = self.get_object(org_id, project_id)
        self.check_object_permissions(request, project)
        serializer = ProjectTeamMembershipSerializer(project.team_memberships.all(), many=True)
        return Response(serializer.data)

    def post(self, request, org_id, project_id):
        """
        Agrega un equipo miembro de la org al proyecto organizacional.
        Le asigna el rol 'project_member' al equipo por defecto.
        """
        project = self.get_object(org_id, project_id)
        self.check_object_permissions(request, project)
        data = request.data.copy()
        data['project'] = project_id
        data['role'] = Role.objects.filter(scope=Scopes.PROJECT, name=Roles.PROJECT_MEMBER).first().id
        serializer = ProjectTeamMembershipSerializer(data=data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        return Response(ProjectTeamMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)

class ProjectTeamMembershipDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'project_admin'},
        'PATCH': {'organization_admin', 'project_admin'},
        'DELETE': {'organization_admin', 'project_admin'},
    }

    def get_object(self, org_id, project_id, team_id):
        return get_object_or_404(ProjectTeamMembership, project_id=project_id, team_id=team_id)
    
    def get(self, request, org_id, project_id, team_id):
        """
        Retorna la membresía del equipo en el proyecto con su rol.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)

        membership = self.get_object(org_id, project_id, team_id)

        serializer = ProjectUserMembershipSerializer(membership, context={'project': project})
        return Response(serializer.data)
    
    def patch(self, request, org_id, project_id, team_id):
        """
        Modifica la membresía del equipo en el proyecto (sirve para modificar el rol del equipo en el proyecto).
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)

        membership = self.get_object(org_id, project_id, team_id)

        data = request.data.copy()
        data['project'] = project_id
        data['team'] = team_id
        serializer = ProjectUserMembershipSerializer(membership, data=data, partial=True, context={'project': project})
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        return Response(ProjectUserMembershipSerializer(membership).data)
    
    def delete(self, request, org_id, project_id, team_id):
        """
        Elimina al equipo del proyecto.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        membership = self.get_object(org_id, project_id, team_id)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
