import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Conecta no banco padrão do postgres para poder rodar o CREATE DATABASE
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='password', host='localhost', port='5432')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Verifica se o banco já existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'barbtech'")
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute('CREATE DATABASE barbtech;')
        print("Database 'barbtech' created successfully.")
    else:
        print("Database 'barbtech' already exists.")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
