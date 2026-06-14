from rest_framework import serializers
from .models import Team, TeamMembership
from organizations.models import OrganizationMembership


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'organization', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        if not value.strip():
            serializers.ValidationError("El nombre del equipo no puede estar en blanco.")
        return value


class TeamMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembership
        fields = ['id', 'team', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']

    def validate_user(self, value):
        team = self.context['team']
        if value.organization != team.organization:
            raise serializers.ValidationError("El usuario debe pertenecer a la misma organizacion que el equipo.")
        return value
