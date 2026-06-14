from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Team, TeamMembership
from .serializers import TeamSerializer, TeamMembershipSerializer
from common.permissions import RoleRequiredPermission, RoleResolver
from .permissions import TeamObjectPermission, TeamMembershipObjectPermission

from organizations.models import Organization, OrganizationMembership
from roles.models import Role, Roles, Scopes

resolver = RoleResolver()

# ---------------- Team list / create ----------------
class TeamListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'organization_project_creator', 'organization_team_creator', 'organization_member'},
        'POST': {'organization_admin', 'organization_team_creator'}
    }

    def get(self, request, org_id):
        """
        Si el usuario es 'organization_admin' retorna todos los equipos de la organizacion.
        Si no es 'organization_admin' retorna los equipos de los que es miembro.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)

        if resolver.has_role(request.user, org, Roles.ORGANIZATION_ADMIN):
            teams = Team.objects.filter(organization_id=org_id)
        else:
            # Membresía del usuario para buscar sus equipos
            org_mem = OrganizationMembership.objects.filter(user=request.user, organization=org).first()

            # ids de equipos del usuario
            team_ids = TeamMembership.objects.filter(user=org_mem).values_list('team_id', flat=True)

            # Equipos del usuario
            teams = Team.objects.filter(organization=org, id__in=team_ids)

        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    def post(self, request, org_id):
        """
        Crea un nuevo equipo en la organizacion del usuario.
        Luego de crear el equipo agrega al usuario al equipo con rol 'team_admin' por defecto.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)

        data = request.data.copy()
        data['organization'] = org_id

        serializer = TeamSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            team = serializer.save()

            org_mem = request.user.organization_membership
            role = Role.objects.filter(scope=Scopes.TEAM, name=Roles.TEAM_ADMIN).first()
            TeamMembership.objects.create(team=team, user=org_mem, role=role)

        return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)


# ---------------- Team detail / patch / delete ----------------
class TeamDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'team_admin', 'team_member'},
        'PATCH': {'organization_admin', 'team_admin'},
        'DELETE': {'organization_admin', 'team_admin'}
    }

    def get_object(self, org_id, team_id):
        return get_object_or_404(Team, id=team_id, organization_id=org_id)

    def get(self, request, org_id, team_id):
        """
        Retorna el equipo.
        """
        team = self.get_object(org_id, team_id)
        self.check_object_permissions(request, team)
        serializer = TeamSerializer(team)
        return Response(serializer.data)

    def patch(self, request, org_id, team_id):
        """
        Modifica el equipo.
        """
        team = self.get_object(org_id, team_id)
        self.check_object_permissions(request, team)
        data = request.data.copy()
        data['organization'] = org_id
        serializer = TeamSerializer(team, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        return Response(TeamSerializer(team).data)

    def delete(self, request, org_id, team_id):
        """
        Elimina el equipo.
        """
        team = self.get_object(org_id, team_id)
        self.check_object_permissions(request, team)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------- Team memberships list / create ----------------
class TeamMembershipListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'team_admin'},
        'POST': {'organization_admin', 'team_admin'}
    }

    def get_object(self, org_id, team_id):
        return get_object_or_404(Team, id=team_id, organization_id=org_id)

    def get(self, request, org_id, team_id):
        """
        Lista los usuarios miembros del equipo.
        """
        team = self.get_object(org_id, team_id)
        self.check_object_permissions(request, team)
        memberships = TeamMembership.objects.filter(team=team)
        serializer = TeamMembershipSerializer(memberships, many=True, context={'team': team})
        return Response(serializer.data)

    def post(self, request, org_id, team_id):
        """
        Agrega un usuario miembro de la org al proyecto organizacional.
        Le asigna el rol 'project_member' al usuario por defecto.
        """
        team = self.get_object(org_id, team_id)
        self.check_object_permissions(request, team)
        data = request.data.copy()
        data['team'] = team_id
        data['role'] = Role.objects.filter(scope=Scopes.TEAM, name=Roles.TEAM_MEMBER).first().id
        serializer = TeamMembershipSerializer(data=data, context={'team': team})
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        return Response(TeamMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)


# ---------------- Team membership detail / patch / delete ----------------
class TeamMembershipDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'team_admin'},
        'PATCH': {'organization_admin', 'team_admin'},
        'DELETE': {'organization_admin', 'team_admin'}
    }

    def get_object(self, org_id, team_id, user_org_membership_id):
        return get_object_or_404(TeamMembership, team_id=team_id, user_id=user_org_membership_id)

    def get(self, request, org_id, team_id, user_org_membership_id):
        """
        Retorna la membresía del usuario en el equipo con su rol.
        """
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(request, team)

        membership = self.get_object(org_id, team_id, user_org_membership_id)
        
        serializer = TeamMembershipSerializer(membership, context={'team': team})
        return Response(serializer.data)

    def patch(self, request, org_id, team_id, user_org_membership_id):
        """
        Modifica la membresía del usuario en el equipo (sirve para modificar el rol del usuario en el equipo).
        """
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(request, team)

        membership = self.get_object(org_id, team_id, user_org_membership_id)

        data = request.data.copy()
        data['team'] = team_id
        data['user'] = user_org_membership_id
        serializer = TeamMembershipSerializer(membership, data=data, partial=True, context={'team': team})
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        return Response(TeamMembershipSerializer(membership).data)

    def delete(self, request, org_id, team_id, user_org_membership_id):
        """
        Elimina al usuario del equipo.
        """
        team = get_object_or_404(Team, id=team_id)
        self.check_object_permissions(request, team)
        membership = self.get_object(org_id, team_id, user_org_membership_id)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
