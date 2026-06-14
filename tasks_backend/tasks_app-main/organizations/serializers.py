from rest_framework import serializers
from .models import Organization, OrganizationMembership, OrganizationInvitation
from django.contrib.auth import get_user_model

User = get_user_model()

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ('id', 'user', 'user_username', 'user_email', 'role', 'role_name', 'joined_at')
        read_only_fields = ('id', 'user', 'user_username', 'user_email', 'role_name', 'joined_at')


class OrganizationInvitationSerializer(serializers.ModelSerializer):
    inviter_username = serializers.CharField(source='inviter.user.username', read_only=True)
    inviter_email = serializers.EmailField(source='inviter.user.email', read_only=True)

    class Meta:
        model = OrganizationInvitation
        fields = ('id', 'inviter', 'inviter_username', 'inviter_email',
                  'organization', 'email', 'created_at', 'accepted', 'rejected', 'accepted_at')
        read_only_fields = ('id', 'created_at', 'accepted', 'rejected', 'accepted_at')