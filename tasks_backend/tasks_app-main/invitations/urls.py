from django.urls import path
from .views import InvitationListView, InvitationDetailView

urlpatterns = [
    # Listar todas las invitaciones del usuario
    path('invitations/', InvitationListView.as_view(), name='user-invitations-list'),

    # Detalle de una invitación y aceptar/rechazar
    path('invitations/<int:invitation_id>/', InvitationDetailView.as_view(), name='user-invitation-detail'),
]
