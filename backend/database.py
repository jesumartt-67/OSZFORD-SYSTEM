from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 1. CONFIGURACIÓN DE CREDENCIALES (Hardcoded para desarrollo local seguro)
# Según tu 'docker inspect', el password de root es 'root'
DB_USER = "root"
DB_PASS = "root"
#DB_HOST = "127.0.0.1"  # Cambiamos 127.0.0.1 por 10.0.2.2 porque es la "puerta de enlace" (Gateway) hacia tu Windows.
DB_HOST = "10.0.2.2"  
DB_PORT = "3306"
DB_NAME = "oszford_db"

# 2. CONSTRUCCIÓN DE LA URL DE CONEXIÓN
# Usamos el driver pymysql que es el más compatible con Python 3
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:tu_password@10.0.2.2:3306/oszford_db"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@10.0.2.2:3306/oszford_db"
#SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 3. CREACIÓN DEL MOTOR (ENGINE)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
#engine = create_engine(
    # SQLALCHEMY_DATABASE_URL,
    # pool_pre_ping: Verifica que la conexión esté viva antes de cada consulta
    # esencial para que no se caiga la app tras periodos de inactividad
    #pool_pre_ping=True 
#)

# 4. CONFIGURACIÓN DE LA SESIÓN
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. BASE PARA LOS MODELOS (Para que models.py herede de aquí)
Base = declarative_base()

# 6. DEPENDENCIA PARA FASTAPI
def get_db():
    #"""
    #Función generadora para obtener una sesión de base de datos.
    #Se cierra automáticamente después de cada petición HTTP.
    #"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()