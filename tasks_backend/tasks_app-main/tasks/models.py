# tasks/models.py
from django.db import models
from django.utils import timezone
from projects.models import Project
from teams.models import Team
from organizations.models import OrganizationMembership
from roles.models import Role, Scopes

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_datetime = models.DateTimeField(null=True, blank=True)  # timezone-aware datetime
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ('expiration_datetime', 'created_at')

    def __str__(self):
        return f"{self.name} ({'closed' if self.completed else 'open'})"

class TaskDependency(models.Model):
    """
    Representa que predecessor_task debe completarse antes que successor_task.
    La integridad (mismo proyecto, sin ciclos) se validará en la lógica/serializers.
    """
    predecessor_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='successor_links')
    successor_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='predecessor_links')

    class Meta:
        unique_together = ('predecessor_task', 'successor_task')
        ordering = ('predecessor_task',)

    def __str__(self):
        return f"{self.predecessor_task_id} -> {self.successor_task_id}"

class TaskUserMembership(models.Model):
    """
    Asignación de tarea a un usuario. `user` referencia a OrganizationMembership
    para asegurar que el usuario pertenezca a la organización del proyecto.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='user_memberships')
    user = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE, related_name='task_user_memberships')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, limit_choices_to={'scope': Scopes.TASK})
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'user')

    def __str__(self):
        return f"{self.user.user.username} -> {self.task.name} ({self.role.name})"

class TaskTeamMembership(models.Model):
    """
    Asignación de tarea a un equipo.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='task_team_memberships')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, limit_choices_to={'scope': Scopes.TASK})
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'team')

    def __str__(self):
        return f"{self.team.name} -> {self.task.name} ({self.role.name})"
