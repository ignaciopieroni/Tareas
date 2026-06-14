from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import serializers as drf_serializers

from .models import Organization, OrganizationMembership, OrganizationInvitation
from .serializers import (
    OrganizationSerializer,
    OrganizationMembershipSerializer,
    OrganizationInvitationSerializer
)
from roles.models import Role, Roles, Scopes
from common.permissions import RoleRequiredPermission


# ---------------- Organizations ----------------

class OrganizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    roles_required = {
        'GET': set(),
        'POST': set()
    }

    def get(self, request):
        """
        Lista todas las organizaciones a las que pertenece el usuario.
        """
        memberships = OrganizationMembership.objects.filter(user=request.user).select_related('organization')
        orgs = [m.organization for m in memberships]
        serializer = OrganizationSerializer(orgs, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Valida que el usuario NO pertenezca a ninguna organización, y crea una.
        """
        if OrganizationMembership.objects.filter(user=request.user).exists():
            return Response(
                {'detail': 'User already belongs to an organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = serializer.save()

        role = Role.objects.filter(scope=Scopes.ORGANIZATION , name=Roles.ORGANIZATION_ADMIN).first()

        # Asignar ORGANIZATION_ADMIN al creador
        OrganizationMembership.objects.create(
            user=request.user,
            organization=org,
            role=role
        )
        return Response(OrganizationSerializer(org).data, status=status.HTTP_201_CREATED)


class OrganizationDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'organization_project_creator', 'organization_team_creator', 'organization_member'},
        'PATCH': {'organization_admin'},
        'DELETE': {'organization_admin'}
    }

    def get_object(self, org_id):
        return get_object_or_404(Organization, id=org_id)

    def get(self, request, org_id):
        """
        Retorna detalle de la organizacion.
        """
        org = self.get_object(org_id)
        self.check_object_permissions(request, org)
        serializer = OrganizationSerializer(org)
        return Response(serializer.data)

    def patch(self, request, org_id):
        """
        Actualiza la organizacion.
        """
        org = self.get_object(org_id)
        self.check_object_permissions(request, org)
        serializer = OrganizationSerializer(org, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, org_id):
        """
        Elimina la organizacion.
        """
        org = self.get_object(org_id)
        self.check_object_permissions(request, org)
        org.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------- Organization Memberships ----------------

class OrganizationMembershipListView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'organization_project_creator', 'organization_team_creator', 'organization_member'}
    }

    def get(self, request, org_id):
        """
        Lista los miembros de la organizacion.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)
        memberships = OrganizationMembership.objects.filter(organization_id=org_id)
        serializer = OrganizationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class OrganizationMembershipDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'PATCH': {'organization_admin'},
        'DELETE': {'organization_admin'}
    }

    def get_object(self, org_id, user_id):
        return get_object_or_404(OrganizationMembership, organization_id=org_id, user_id=user_id)

    def patch(self, request, org_id, user_id):
        """
        Actualiza un miembro de la organizacion.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)
        if request.user.id == user_id:
            return Response(
                {'detail': 'Un usuario no puede editarse a si mismo.'},
                status=status.HTTP_403_FORBIDDEN
            )
        membership = self.get_object(org_id, user_id)
        serializer = OrganizationMembershipSerializer(membership, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, org_id, user_id):
        """
        Elimina un miembro de la organizacion.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)
        membership = self.get_object(org_id, user_id)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------- Organization Invitations ----------------

class OrganizationInvitationListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin'},
        'POST': {'organization_admin'}
    }

    def get(self, request, org_id):
        """
        Lista las invitaciones a la organizacion.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)
        invites = OrganizationInvitation.objects.filter(organization_id=org_id)
        serializer = OrganizationInvitationSerializer(invites, many=True)
        return Response(serializer.data)

    def post(self, request, org_id):
        """
        Crea una nueva invitacion a la organizacion.
        """
        org = get_object_or_404(Organization, id=org_id)
        self.check_object_permissions(request, org)

        inviter_mem = getattr(request.user, 'organization_membership', None)

        payload = request.data or {}
        emails = payload.get('emails')

        if not isinstance(emails, list):
            return Response({'detail': "El campo 'emails' debe ser una lista de emails."}, status=status.HTTP_400_BAD_REQUEST)

        # normalizar y validar cada email
        normalizer = []
        seen = set()
        email_field = drf_serializers.EmailField()
        for idx, raw in enumerate(emails):
            if not isinstance(raw, str):
                return Response({'emails': f'El email con indice {idx} debe ser un string.'}, status=status.HTTP_400_BAD_REQUEST)
            normalized = raw.strip().lower()
            if not normalized:
                return Response({'emails': f'El email con indice {idx} está vacío.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # validar formato
            try:
                email_field.run_validation(normalized)
            except drf_serializers.ValidationError as e:
                return Response({'detail': f"Error email {idx}: {e.detail}"}, status=status.HTTP_400_BAD_REQUEST)
            if normalized in seen:
                return Response({'emails': f'El email {normalized} está duplicado'}, status=status.HTTP_400_BAD_REQUEST)
            seen.add(normalized)
            normalizer.append(normalized)

        if len(normalizer) == 0:
            return Response({'emails': "El campo 'emails' no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # checkear conflictos por duplicacion de invitaciones pendientes
        pending_qs = OrganizationInvitation.objects.filter(
            organization=org,
            email__in=normalizer,
            accepted=False,
            rejected=False
        ).values_list('email', flat=True)
        pending_conflicts = [e for e in normalizer if e in set(pending_qs)]
        if pending_conflicts:
            return Response(
                {'detail': 'Ya existen invitaciones pendientes para algunos emails.',
                'conflicts': pending_conflicts},
                status=status.HTTP_400_BAD_REQUEST
            )

        # create invites in transaction
        created = []
        with transaction.atomic():
            for e in normalizer:
                inv = OrganizationInvitation.objects.create(
                    inviter=inviter_mem,
                    organization=org,
                    email=e
                )
                created.append(inv)

        serializer = OrganizationInvitationSerializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)