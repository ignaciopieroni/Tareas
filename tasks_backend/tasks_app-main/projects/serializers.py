from rest_framework import serializers
from .models import Project, ProjectUserMembership, ProjectTeamMembership
from organizations.models import OrganizationMembership

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'organization', 'owner', 'name', 'description', 'is_closed', 'closed_at', 'created_at')
        read_only_fields = ('id', 'is_closed', 'closed_at', 'created_at')

    def validate(self, attrs):
        # Proyectos personales: debe crearse con owner y sin organization
        # Proyecto organizacionales: debe crearse sin owner y con organization
        if attrs.get('owner') is not None and attrs.get('organization') is not None:
            serializers.ValidationError("No puede crearse un proyecto con owner y organization al mismo tiempo.")
        return attrs

    def create(self, validated_data):
        return Project.objects.create(**validated_data)


class ProjectUserMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectUserMembership
        fields = ('id', 'project', 'user', 'role', 'joined_at')
        read_only_fields = ('id', 'joined_at',)

    def validate_user(self, value):
        project = self.context.get('project')
        if project.organization and value.organization != project.organization:
            raise serializers.ValidationError("El usuario debe pertenecer a la misma organización que el proyecto.")
        return value


class ProjectTeamMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTeamMembership
        fields = ('id', 'project', 'team', 'role', 'joined_at')
        read_only_fields = ('id', 'joined_at',)

    def validate_team(self, value):
        project = self.context.get('project')
        if project.organization and value.organization != project.organization:
            raise serializers.ValidationError("El equipo debe pertenecer a la misma organización que el proyecto.")
        return value
