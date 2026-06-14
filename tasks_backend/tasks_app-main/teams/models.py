from django.db import models
from organizations.models import Organization, OrganizationMembership
from roles.models import Role, Scopes

class Team(models.Model):
    """
    Tabla de equipos.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class TeamMembership(models.Model):
    """
    Tabla de membresias de usuarios a los equipos.
    Un usuario tendra un unico rol en un equipo.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, limit_choices_to={'scope': Scopes.TEAM})
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.user.username} in {self.team.name} as {self.role.name}"