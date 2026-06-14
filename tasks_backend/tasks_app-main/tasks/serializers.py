from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from django.db import transaction, IntegrityError

from .models import Task, TaskDependency, TaskUserMembership, TaskTeamMembership
from teams.models import Team, TeamMembership
from organizations.models import OrganizationMembership
from projects.models import ProjectUserMembership, ProjectTeamMembership
from django.contrib.auth import get_user_model
from roles.models import Role, Roles

from tasks.utils import check_cycle_in_db

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    predecessors = serializers.SerializerMethodField(read_only=True)
    assigned_users = serializers.SerializerMethodField(read_only=True)  # devuelve OrganizationMembership.id + username
    assigned_teams = serializers.SerializerMethodField(read_only=True)

    predecessors_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    users_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)  # OrganizationMembership ids
    teams_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Task
        fields = (
            'id', 'project', 'name', 'description', 'created_at',
            'expiration_datetime', 'completed',
            'predecessors', 'predecessors_ids',
            'assigned_users', 'users_ids',
            'assigned_teams', 'teams_ids'
        )
        read_only_fields = ('id', 'created_at', 'completed', 'predecessors', 'assigned_users', 'assigned_teams')

    def get_predecessors(self, obj):
        return [{'id': d.predecessor_task.id, 'name': d.predecessor_task.name}
                for d in obj.predecessor_links.select_related('predecessor_task').all()]

    def get_assigned_users(self, obj):
        users_map = {}
        for um in TaskUserMembership.objects.filter(task=obj, role__name=Roles.TASK_ASSIGNED).select_related('user__user'):
            org_mem = um.user
            users_map[org_mem.id] = org_mem.user.username
        for tm in TaskTeamMembership.objects.filter(task=obj, role__name=Roles.TASK_ASSIGNED).select_related('team'):
            team = tm.team
            for team_mem in team.memberships.select_related('user__user').all():
                org_mem = team_mem.user
                users_map[org_mem.id] = org_mem.user.username
        return [{'id': mid, 'username': mname} for mid, mname in sorted(users_map.items())]

    def get_assigned_teams(self, obj):
        return [{'id': tm.team.id, 'name': tm.team.name}
                for tm in TaskTeamMembership.objects.filter(task=obj, role__name=Roles.TASK_ASSIGNED).select_related('team')]

    def validate_expiration_datetime(self, value):
        if not isinstance(value, datetime):
            raise serializers.ValidationError({'detail': "Valor de fecha/hora inválido."})
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = timezone.make_aware(value, timezone.get_default_timezone())
        if value < timezone.now():
            raise serializers.ValidationError({'detail': "expiration_datetime no puede estar en el pasado (hora de Argentina)."})
        return value

    def _validate_predecessors_list(self, project, predecessors_ids, instance_task_id=None):
        if not predecessors_ids:
            return []
        qs_map = {t.id: t for t in Task.objects.filter(id__in=predecessors_ids)}
        preds = []
        for pid in predecessors_ids:
            if pid not in qs_map:
                raise serializers.ValidationError({'detail': f"Tarea id {pid} no encontrada."})
            t = qs_map[pid]
            if t.project_id != project.id:
                raise serializers.ValidationError({'detail': f"La tarea id {pid} no pertenece al mismo proyecto."})
            if instance_task_id and pid == instance_task_id:
                raise serializers.ValidationError({'detail': "Una tarea no puede ser predecesora de sí misma."})
            preds.append(t)
        return preds

    def _validate_users_list(self, project, users_ids):
        if not users_ids:
            return []

        if project.organization is None:
            raise serializers.ValidationError({'detail': "No se pueden asignar usuarios a tareas de proyectos personales."})

        org_mems_qs = OrganizationMembership.objects.filter(id__in=users_ids)
        org_map = {om.id: om for om in org_mems_qs}
        missing = [mid for mid in users_ids if mid not in org_map]
        if missing:
            raise serializers.ValidationError({'detail': f"OrganizationMembership ids {missing} no encontradas."})

        wrong_org = [om.id for om in org_mems_qs if om.organization_id != project.organization_id]
        if wrong_org:
            raise serializers.ValidationError({'detail': f"Los OrganizationMembership ids {wrong_org} no pertenecen a la organización del proyecto."})

        ordered_org_mems = [org_map[mid] for mid in users_ids]
        om_ids = [om.id for om in ordered_org_mems]

        pu_qs = ProjectUserMembership.objects.filter(project=project, user_id__in=om_ids).values_list('user_id', flat=True)
        pu_set = set(pu_qs)

        tm_qs = TeamMembership.objects.filter(user_id__in=om_ids).values_list('user_id', 'team_id')
        om_to_team_ids = {}
        for user_id, team_id in tm_qs:
            om_to_team_ids.setdefault(user_id, set()).add(team_id)
        all_team_ids = {tid for s in om_to_team_ids.values() for tid in s} if om_to_team_ids else set()

        if all_team_ids:
            pt_qs = ProjectTeamMembership.objects.filter(project=project, team_id__in=all_team_ids).values_list('team_id', flat=True)
            project_team_set = set(pt_qs)
        else:
            project_team_set = set()

        not_in_project = []
        for om in ordered_org_mems:
            if om.id in pu_set:
                continue
            teams_of_om = om_to_team_ids.get(om.id, set())
            if teams_of_om and (teams_of_om & project_team_set):
                continue
            not_in_project.append(om.id)

        if not_in_project:
            raise serializers.ValidationError({'detail': f"OrganizationMembership ids {not_in_project} no son miembros del proyecto."})

        return ordered_org_mems

    def _validate_teams_list(self, project, teams_ids):
        if not teams_ids:
            return []
        if project.organization is None:
            raise serializers.ValidationError({'detail': "No se pueden asignar equipos a tareas de proyectos personales."})

        teams_qs = Team.objects.filter(id__in=teams_ids)
        teams_map = {t.id: t for t in teams_qs}
        missing = [tid for tid in teams_ids if tid not in teams_map]
        if missing:
            raise serializers.ValidationError({'detail': f"Teams ids {missing} no encontrados."})

        wrong_org = [t.id for t in teams_qs if t.organization_id != project.organization_id]
        if wrong_org:
            raise serializers.ValidationError({'detail': f"Los equipos {wrong_org} no pertenecen a la organización del proyecto."})
        return [teams_map[tid] for tid in teams_ids]

    def _apply_predecessors(self, task, preds):
        current = set(TaskDependency.objects.filter(successor_task=task).values_list('predecessor_task_id', flat=True))
        new = set(t.id for t in preds)
        to_create = new - current
        to_delete = current - new
        with transaction.atomic():
            if to_delete:
                TaskDependency.objects.filter(predecessor_task_id__in=to_delete, successor_task=task).delete()
            for pid in to_create:
                TaskDependency.objects.create(predecessor_task_id=pid, successor_task=task)

    def _apply_user_memberships(self, task, org_members_list):
        current_ids = set(TaskUserMembership.objects.filter(task=task).values_list('user_id', flat=True))
        new_ids = set([om.id for om in org_members_list])

        to_create = new_ids - current_ids
        to_delete = current_ids - new_ids

        with transaction.atomic():
            if to_delete:
                TaskUserMembership.objects.filter(task=task, user_id__in=list(to_delete)).delete()
            role_obj = Role.objects.filter(name=Roles.TASK_ASSIGNED).first()
            for om in org_members_list:
                if om.id in to_create:
                    TaskUserMembership.objects.create(task=task, user=om, role=role_obj)

    def _apply_team_memberships(self, task, teams):
        current_ids = set(TaskTeamMembership.objects.filter(task=task).values_list('team_id', flat=True))
        new_ids = set([t.id for t in teams])
        to_create = new_ids - current_ids
        to_delete = current_ids - new_ids

        with transaction.atomic():
            if to_delete:
                TaskTeamMembership.objects.filter(task=task, team_id__in=list(to_delete)).delete()
            role_obj = Role.objects.filter(name=Roles.TASK_ASSIGNED).first()
            for t in teams:
                if t.id in to_create:
                    TaskTeamMembership.objects.create(task=task, team=t, role=role_obj)

    def create(self, validated_data):
        preds_ids = validated_data.pop('predecessors_ids', None)
        users_ids = validated_data.pop('users_ids', None)
        teams_ids = validated_data.pop('teams_ids', None)

        project = validated_data.get('project')
        if project is None:
            raise serializers.ValidationError({'detail': "Falta el proyecto para la tarea."})

        preds = self._validate_predecessors_list(project, preds_ids, instance_task_id=None) if preds_ids else []
        org_members = self._validate_users_list(project, users_ids) if users_ids else []
        teams = self._validate_teams_list(project, teams_ids) if teams_ids else []

        # Para creación no es necesario check_cycle_in_db (la tarea no existe aún y no tiene sucesoras).
        try:
            with transaction.atomic():
                task = Task.objects.create(**validated_data)
                if preds:
                    self._apply_predecessors(task, preds)
                if org_members:
                    self._apply_user_memberships(task, org_members)
                if teams:
                    self._apply_team_memberships(task, teams)
        except IntegrityError as e:
            raise serializers.ValidationError({'detail': str(e)})

        return task

    def update(self, instance, validated_data):
        preds_ids = validated_data.pop('predecessors_ids', None)
        users_ids = validated_data.pop('users_ids', None)
        teams_ids = validated_data.pop('teams_ids', None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        project = instance.project

        if preds_ids is not None:
            preds = self._validate_predecessors_list(project, preds_ids, instance_task_id=instance.id)
            # ciclo check: obtener conjunto completa de predecesoras que resultaría (existentes + nuevas)
            existing_pred_ids = list(TaskDependency.objects.filter(successor_task=instance).values_list('predecessor_task_id', flat=True))
            combined = list(dict.fromkeys(existing_pred_ids + [p.id for p in preds]))
            ok, offending = check_cycle_in_db(instance.id, combined)
            if not ok:
                raise serializers.ValidationError({'detail': f"Asignar estas predecesoras causaría un ciclo. Tareas conflictivas: {offending}"})
            self._apply_predecessors(instance, preds)

        if users_ids is not None:
            org_members = self._validate_users_list(project, users_ids)
            self._apply_user_memberships(instance, org_members)

        if teams_ids is not None:
            teams = self._validate_teams_list(project, teams_ids)
            self._apply_team_memberships(instance, teams)

        return instance
