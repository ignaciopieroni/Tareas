from django.conf import settings
from django.db import models
from django.utils import timezone
from organizations.models import Organization
from organizations.models import OrganizationMembership
from teams.models import Team
from roles.models import Role, Scopes

User = settings.AUTH_USER_MODEL

class Project(models.Model):
    """
    Tabla de Proyectos Organizacionales y Proyectos Personales.
    organization == None  => proyecto personal (owner NOT NULL)
    organization != None  => proyecto organizacional (owner NULL)
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True, related_name='projects')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='personal_projects')
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def close(self):
        self.is_closed = True
        self.closed_at = timezone.now()
        self.save()

    def __str__(self):
        kind = 'personal' if self.organization is None else self.organization.name
        return f"{self.name} ({kind})"

    class Meta:
        ordering = ('-created_at',)


class ProjectUserMembership(models.Model):
    """
    Tabla de membresias de usuarios a proyectos.
    Cada usuario tendra un unico rol sobre un proyecto.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_memberships')
    user = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE, related_name='project_user_memberships')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, limit_choices_to={'scope': Scopes.PROJECT})
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.user.username} @ {self.project.name} as {self.role.name}"


class ProjectTeamMembership(models.Model):
    """
    Tabla de membresias de equipos a proyectos.
    Cada equipo tendra un unico rol sobre un proyecto.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='project_team_memberships')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, limit_choices_to={'scope': Scopes.PROJECT})
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'team')

    def __str__(self):
        return f"{self.team.name} @ {self.project.name} as {self.role.name}"