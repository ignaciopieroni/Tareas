from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from common.permissions import RoleRequiredPermission

from organizations.models import OrganizationInvitation
from organizations.serializers import OrganizationInvitationSerializer


class InvitationListView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {'GET': set()}

    def get(self, request):
        """
        Retorna las invitaciones PENDIENTES (no aceptadas ni rechazadas) del usuario
        logueado (filtradas por email). Si el usuario ya pertenece a una organización,
        devuelve 403.
        """
        if hasattr(request.user, 'organization_membership'):
            return Response(
                {'detail': 'El usuario ya pertenece a una organización.'},
                status=status.HTTP_403_FORBIDDEN
            )

        invites = OrganizationInvitation.objects.filter(
            email__iexact=request.user.email,
            accepted=False,
            rejected=False
        ).order_by('-created_at')
        serializer = OrganizationInvitationSerializer(invites, many=True)
        return Response(serializer.data)


class InvitationDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': set(),
        'PATCH': set()
    }

    def get_object(self, invitation_id, user):
        """
        Obtiene la invitación pendiente por id y email del usuario.
        """
        return get_object_or_404(OrganizationInvitation, id=invitation_id, email__iexact=user.email, accepted=False, rejected=False)

    def get(self, request, invitation_id):
        """
        Devuelve la invitacion si:
        - contiene el mail del usuario
        - aun esta pendiente
        """
        invite = self.get_object(invitation_id, request.user)
        serializer = OrganizationInvitationSerializer(invite)
        return Response(serializer.data)

    def patch(self, request, invitation_id):
        """
        Acepta o rechaza la invitacion a través de metodos del modelo OrganizationInvitation.
        Si se acepta la invitacion, el metodo agrega al usuario a la organizacion con el rol 'organization_member' por defecto.
        La aceptacion / rechazo de la invitacion se realiza con el parametro -> action = 'accept' | 'reject'
        """
        invite = self.get_object(invitation_id, request.user)
        action = (request.data.get('action') or '').lower()

        if action not in ('accept', 'reject'):
            return Response({'detail': 'Acción inválida. Use "accept" o "reject".'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if action == 'accept':
                invite.accept(request.user)
            else:
                invite.reject(request.user)
        except IntegrityError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrganizationInvitationSerializer(invite).data)
