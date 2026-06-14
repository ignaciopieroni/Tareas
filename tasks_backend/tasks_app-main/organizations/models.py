from django.conf import settings
from django.db import models, IntegrityError
from django.utils import timezone
from roles.models import Role, Roles, Scopes

User = settings.AUTH_USER_MODEL

class Organization(models.Model):
    """
    Tabla de organizaciones.
    """
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class OrganizationMembership(models.Model):
    """
    Tabla de membresias a organizaciones.
    Cada usuario solo puede tener una organizacion (OneToOneField).
    El usuario tendrá un unico rol en la organización.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organization_membership')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, limit_choices_to={'scope': 'organization'}, related_name='organization_members')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} @ {self.organization} ({self.role.name})"

    class Meta:
        ordering = ('organization', 'joined_at')

class OrganizationInvitation(models.Model):
    """
    Tabla de invitaciones a organizaciones.
    Cada invitacion tiene un email (el cual puede o no pertenecer a un usuario registrado en la app).
    Si la invitacion se acepta, se agrega al usuario invitado a la organizacion con el rol 'organization_member' por defecto.
    """
    inviter = models.ForeignKey('OrganizationMembership', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invitations')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def accept(self, user):
        """
        Marca la invitacion como aceptada y crea OrganizationMembership para 'user.
        Por defecto, se le asigna el rol 'organization_member' al 'user' agregado a la org.
        """

        if self.accepted or self.rejected:
            raise IntegrityError("Esta invitación ya fue aceptada o rechazada.")

        if user.email.lower() != (self.email or "").lower():
            raise IntegrityError("Solo el usuario invitado puede aceptar esta invitación.")

        if hasattr(user, 'organization_membership'):
            raise IntegrityError("El usuario ya pertenece a otra organización.")

        # marcar invitación como aceptada
        self.accepted = True
        self.rejected = False
        self.accepted_at = timezone.now()
        self.save()

        # crear OrganizationMembership con rol por defecto 'organization_member'
        OrganizationMembership.objects.create(
            user=user,
            organization=self.organization,
            role=Role.objects.get(name=Roles.ORGANIZATION_MEMBER, scope=Scopes.ORGANIZATION)
        )

    def reject(self, user):
        """
        Marca la invitacion como rechazada.
        """
        if self.accepted or self.rejected:
            raise IntegrityError("Esta invitación ya fue aceptada o rechazada.")

        if user.email.lower() != (self.email or "").lower():
            raise IntegrityError("Solo el usuario invitado puede rechazar esta invitación.")

        self.rejected = True
        self.accepted = False
        self.accepted_at = None
        self.save()
