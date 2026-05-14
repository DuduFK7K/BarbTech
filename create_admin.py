import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbtech_core.settings')
django.setup()

from accounts.models import User

# Cria um super usuário se não existir
if not User.objects.filter(email='admin@barbtech.com').exists():
    User.objects.create_superuser(
        username='admin', 
        email='admin@barbtech.com', 
        password='admin', 
        nome='Administrador'
    )
    print("Superusuário 'admin@barbtech.com' (senha: 'admin') criado com sucesso!")
else:
    print("O superusuário 'admin@barbtech.com' já existe.")
