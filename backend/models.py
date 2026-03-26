from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, Text, DECIMAL, Boolean, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# Busca en tu carpeta raíz un archivo que se llame database.py. Es ahí donde se suele configurar SQLAlchemy.
# Si el archivo se llama database.py (Asi se llama): Entonces la importación 'from database import Base' es correcta.
from backend.database import Base

Base = declarative_base()

class Colaborador(Base):
    __tablename__ = "colaboradores"
    id_colaborador = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String(15), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    mfa_secret = Column(String(32), nullable=True) # Secreto para MFA/2FA 
    cargo = Column(String(50))
    licencia_nro = Column(String(20))
    licencia_vigencia = Column(Date)
    activo = Column(Boolean, default=True)
 
    # Relaciones
    inspecciones = relationship("Inspeccion", back_populates="colaborador")
    transferencias_sale = relationship("TransferenciaRelevo", foreign_keys="[TransferenciaRelevo.id_colaborador_sale]", back_populates="colaborador_sale")
    transferencias_entra = relationship("TransferenciaRelevo", foreign_keys="[TransferenciaRelevo.id_colaborador_entra]", back_populates="colaborador_entra")

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    placa = Column(String(10), primary_key=True)
    tipo = Column(Enum('Moto', 'Bicicleta', 'Patineta Eléctrica', 'Moto Eléctrica'), nullable=False)
    propiedad = Column(Enum('Empresa', 'Propio'), nullable=False)
    soat_vencimiento = Column(Date)
    tecnico_vencimiento = Column(Date) 
    foto_referencia_url = Column(String(255)) # URL en Google Cloud Storage

    # Relaciones
    inspecciones = relationship("Inspeccion", back_populates="vehiculo")

class Inspeccion(Base):
    __tablename__ = "inspecciones"

    id_inspeccion = Column(Integer, primary_key=True, autoincrement=True) 
    id_colaborador = Column(Integer, ForeignKey("colaboradores.id_colaborador"))
    placa = Column(String(10), ForeignKey("vehiculos.placa")) 
    fecha_hora = Column(TIMESTAMP, server_default=func.current_timestamp()) 
    km_registro = Column(DECIMAL(10, 2)) 
    estado_visual_ia = Column(Enum('Verde', 'Amarillo', 'Rojo'))
    # --- NUEVOS CAMPOS AGREGADOS A LA BD ---
    confianza_ia = Column(Float, default=0.0) 
    url_foto_verificacion = Column(String(255)) 
    alerta_enviada = Column(Boolean, default=False) 

    novedades = Column(Text) 

    # Relaciones
    colaborador = relationship("Colaborador", back_populates="inspecciones")
    vehiculo = relationship("Vehiculo", back_populates="inspecciones")

class TransferenciaRelevo(Base):
    __tablename__ = "transferencias_relevo"
    id_transferencia = Column(Integer, primary_key=True, autoincrement=True) 
    placa = Column(String(10), ForeignKey("vehiculos.placa")) 
    id_colaborador_sale = Column(Integer, ForeignKey("colaboradores.id_colaborador")) 
    id_colaborador_entra = Column(Integer, ForeignKey("colaboradores.id_colaborador")) 
    km_entrega = Column(DECIMAL(10, 2)) 
    token_qr_hash = Column(String(64), unique=True) 
    fecha_generacion = Column(TIMESTAMP, server_default=func.current_timestamp()) 
    confirmada = Column(Boolean, default=False) 

    # Relaciones
    colaborador_sale = relationship("Colaborador", foreign_keys=[id_colaborador_sale], back_populates="transferencias_sale")
    colaborador_entra = relationship("Colaborador", foreign_keys=[id_colaborador_entra], back_populates="transferencias_entra")