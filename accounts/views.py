from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import ClienteRegistrationSerializer, ProfissionalRegistrationSerializer

class ClienteRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClienteRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail": "Cliente criado com sucesso", "id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfissionalRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProfissionalRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail": "Profissional criado com sucesso", "id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

