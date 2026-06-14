from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Role
from .serializers import RoleSerializer
from rest_framework import status

class RoleListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Lista los roles de la app (devuelve los registros de la base de datos)
        """
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Busca un rol por nombre y scope y lo retorna.
        """
        role_name = request.data.get('role_name', None)
        scope = request.data.get('scope', None)

        if role_name is None or scope is None:
            return Response({'detail': "Los campos 'role_name' y 'scope' son obligatorios."})
        
        role = Role.objects.filter(name=role_name, scope=scope).first()
        if not role:
            return Response({'detail': f"El rol '{role_name}' con scope '{scope}' no existe."})
        serializer = RoleSerializer(role)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoleDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """
        Retorna un rol.
        """
        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({'detail': 'No se encontró un rol con el id especificado.'}, status=404)
        serializer = RoleSerializer(role)
        return Response(serializer.data)
