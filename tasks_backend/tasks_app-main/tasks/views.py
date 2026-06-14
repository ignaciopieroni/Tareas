from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Task
from .serializers import TaskSerializer
from .permissions import TaskObjectPermission, CanCompleteTask
from common.permissions import RoleRequiredPermission
from projects.models import Project

# ---------------- Org tasks ----------------
class OrgProjectTaskListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'project_admin', 'project_member'},
        'POST': {'organization_admin', 'project_admin'},
    }

    def get(self, request, org_id, project_id):
        """
        Lista las tareas del proyecto organizacional.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, org_id, project_id):
        """
        Crea una tarea en el proyecto organizacional.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        data = request.data.copy()
        data['project'] = project_id
        serializer = TaskSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class OrgTaskDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'organization_admin', 'project_admin', 'project_member'},
        'PATCH': {'organization_admin', 'project_admin'},
        'DELETE': {'organization_admin', 'project_admin'},
    }

    def get_object(self, task_id):
        return get_object_or_404(Task, id=task_id)

    def get(self, request, org_id, project_id, task_id):
        """
        Retorna la tarea del proyecto organizacional.
        """
        project = get_object_or_404(Project, project_id=project_id)
        self.check_object_permissions(request, project)
        task = self.get_object(task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def patch(self, request, org_id, project_id, task_id):
        """
        Modifica la tarea del proyecto organizacional.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)

        task = self.get_object(task_id)
        data = request.data.copy()
        data['project'] = project_id
        serializer = TaskSerializer(task, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskSerializer(task).data)

    def delete(self, request, org_id, project_id, task_id):
        """
        Elimina la tarea del proyecto organizacional.
        """
        project = get_object_or_404(Project, project_id=project_id)
        self.check_object_permissions(request, project)

        task = self.get_object(task_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrgTaskCompleteView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'POST': {'organization_admin', 'project_admin', 'task_assigned'},
    }

    def post(self, request, org_id, project_id, task_id):
        """
        Completa la tarea del proyecto organizacional.
        """
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(request, task)
        incomplete = task.predecessor_links.exclude(predecessor_task__completed=True)
        if incomplete.exists():
            return Response({
                'detail': 'No es posible completar la tarea porque algunas de sus predecesoras aún están incompletas.',
                'pending': [p.predecessor_task.id for p in incomplete]
            }, status=status.HTTP_400_BAD_REQUEST)

        task.completed = True
        task.save()
        return Response(TaskSerializer(task).data)


# ---------------- Personal tasks ----------------
class PersonalProjectTaskListCreateView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'owner'}, 
        'POST': {'owner'}
    }

    def get(self, request, project_id):
        """
        Lista las tareas del proyecto personal.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        """
        Crea una tarea en el proyecto personal.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        data = request.data.copy()
        data['project'] = project_id
        serializer = TaskSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class PersonalTaskDetailView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission]
    roles_required = {
        'GET': {'owner'}, 
        'PATCH': {'owner'}, 
        'DELETE': {'owner'}
    }

    def get_object(self, task_id):
        return get_object_or_404(Task, id=task_id)

    def get(self, request, project_id, task_id):
        """
        Retorna la tarea del proyecto personal.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        task = self.get_object(task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def patch(self, request, project_id, task_id):
        """
        Modifica la tarea del proyecto personal.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        task = self.get_object(task_id)
        data = request.data.copy()
        data['project'] = project_id
        serializer = TaskSerializer(task, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskSerializer(task).data)

    def delete(self, request, project_id, task_id):
        """
        Elimina la tarea del proyecto personal.
        """
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        task = self.get_object(task_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PersonalTaskCompleteView(APIView):
    permission_classes = [IsAuthenticated, RoleRequiredPermission] 
    roles_required = {
        'POST': {'owner'},
    }

    def post(self, request, project_id, task_id):
        """
        Completa la tarea del proyecto personal.
        """
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(request, task)
        incomplete = task.predecessor_links.exclude(predecessor_task__completed=True)
        if incomplete.exists():
            return Response({
                'detail': 'No es posible completar la tarea porque algunas de sus predecesoras aún están incompletas.',
                'pending': [p.predecessor_task.id for p in incomplete]
            }, status=status.HTTP_400_BAD_REQUEST)

        task.completed = True
        task.save()
        return Response(TaskSerializer(task).data)