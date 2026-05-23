from rest_framework import permissions

class IsAdminEstabelecimento(permissions.BasePermission):
    """
    Role baseada no profissional_profile possuir cargo ADMIN no estabelecimento.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'profissional_profile'))

    def has_object_permission(self, request, view, obj):
        # Obj pode ser o Estabelecimento ou alguma entidade que tem estabelecimento
        profile = request.user.profissional_profile
        if hasattr(obj, 'estabelecimento'):
            return profile.estabelecimento == obj.estabelecimento and profile.cargo == 'ADMIN'
        return profile.estabelecimento == obj and profile.cargo == 'ADMIN'

class IsFuncionario(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'profissional_profile'))

    def has_object_permission(self, request, view, obj):
        profile = request.user.profissional_profile
        if hasattr(obj, 'estabelecimento'):
            return profile.estabelecimento == obj.estabelecimento
        return profile.estabelecimento == obj

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Is the user the direct owner?
        if hasattr(obj, 'cliente') and obj.cliente == request.user:
            return True
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
            
        # Or is the user the professional attending?
        if hasattr(obj, 'profissional') and obj.profissional == request.user.profissional_profile:
            return True

        return False
