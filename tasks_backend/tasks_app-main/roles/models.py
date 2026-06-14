from django.db import models

class Scopes(models.TextChoices):
    ORGANIZATION = "organization", "organization"
    TEAM = "team", "team"
    PROJECT = "project", "project"
    TASK = "task", "task"

class Roles(models.TextChoices):
    ORGANIZATION_ADMIN = "organization_admin", "organization_admin"
    ORGANIZATION_PROJECT_CREATOR = "organization_project_creator", "organization_project_creator"
    ORGANIZATION_TEAM_CREATOR = "organization_team_creator", "organization_team_creator"
    ORGANIZATION_MEMBER = "organization_member", "organization_member"
    TEAM_ADMIN = "team_admin", "team_admin"
    TEAM_MEMBER = "team_member", "team_member"
    PROJECT_ADMIN = "project_admin", "project_admin"
    PROJECT_MEMBER = "project_member", "project_member"
    TASK_ASSIGNED = "task_assigned", "task_assigned"

class Role(models.Model):
    """
    Catalogo de roles. name y scope están normalizados por TextChoices.
    """
    name = models.CharField(max_length=64, choices=Roles.choices)
    scope = models.CharField(max_length=32, choices=Scopes.choices)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('name', 'scope')
        ordering = ('scope', 'name')

    def __str__(self):
        return f"{self.scope}:{self.name}"
