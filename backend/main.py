from fastapi import FastAPI, HTTPException, Depends, status

# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

import jwt
import datetime
from typing import List

# Importamos tus modelos y lógica de la carpeta backend
from backend.database import SessionLocal, engine
from backend.models import Base, Colaborador, Vehiculo, Inspeccion, TransferenciaRelevo
from backend.auth import verificar_codigo_mfa, generar_secreto_mfa
from backend.relevo import ejecutar_generacion_qr, ejecutar_validacion_token

# 1. Crear las tablas en MySQL (Asegúrate que el contenedor Docker esté corriendo)
Base.metadata.create_all(bind=engine)

# 2. Inicialización de la API
app = FastAPI(
    title="OSZFORD-SYSTEM API",
    description="Sistema de Inspección Vehicular con MFA y Relevo por QR - Hackaton PONAO",
    version="1.0.0"
)

# Esta línea es la que "activa" el botón del candado en Swagger
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)

# 3. Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Clave secreta para JWT
SECRET_KEY = "OSZFORD_SUPER_SECRET_2026"

# --- ENDPOINTS DE PRUEBA ---

@app.get("/", tags=["General"])
def read_root():
    return {
        "status": "Online",
        "proyecto": "OSZFORD-SYSTEM",
        "estudiante": "Jesus Fernando, Katherine, Andrea",
        "docs": "/docs"
    }

# --- ENDPOINTS DE AUTENTICACIÓN ---

@app.post("/auth/login", tags=["Seguridad"])
async def login(email: str, password_plano: str, db: Session = Depends(get_db)):
    """
    Paso 1: Verifica credenciales contra la tabla de Colaboradores.
    """
    user = db.query(Colaborador).filter(Colaborador.email == email).first()
    if not user or user.password_hash != password_plano:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    return {
        "message": "Credenciales correctas. Ingrese su código MFA.",
        "id_colaborador": user.id_colaborador,
        "mfa_required": True
    }

@app.post("/auth/verify-mfa", tags=["Seguridad"])
async def verify_mfa(id_colaborador: int, codigo: str, db: Session = Depends(get_db)):
    """
    Paso 2: Valida el código TOTP de 6 dígitos.
    """
    user = db.query(Colaborador).filter(Colaborador.id_colaborador == id_colaborador).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if verificar_codigo_mfa(user.mfa_secret, codigo):
        # Generamos el token de acceso con expiración de 8 horas
        payload = {
            "sub": user.email,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Código MFA incorrecto o expirado")

# --- ENDPOINTS DE RELEVO (TOKEN QR)

@app.post("/relevo/generar-qr", tags=["Relevo Digital"])
async def crear_qr_entrega(
    id_inspeccion: int, 
    id_colaborador: int, 
    placa: str, 
    km_entrega: float, 
    db: Session = Depends(get_db)
):
    """
    PASO B/C: Registra el relevo en la BD y genera el QR con Token para el conductor que sale.
    """
    try:
        # 1. Generamos el Token y la Imagen usando la lógica de relevo.py
        # Esta función devuelve un diccionario con {"token_puro": ..., "qr_base64": ...}
        resultado_qr = ejecutar_generacion_qr(
            id_inspeccion=id_inspeccion,
            id_colaborador=id_colaborador,
            placa=placa,
            km_entrega=km_entrega
        )

        # 2. Creamos el registro en la tabla de transferencias (Tu base de datos)
        nuevo_relevo = TransferenciaRelevo(
            placa=placa,
            id_colaborador_sale=id_colaborador,
            km_entrega=km_entrega,
            token_qr_hash=resultado_qr["token_puro"], # Guardamos el token para validar después
            confirmada=False
        )
        
        db.add(nuevo_relevo)
        db.commit()
        db.refresh(nuevo_relevo)

        # 3. Retornamos la respuesta completa para Swagger
        return {
            "transferencia_id": nuevo_relevo.id_transferencia,
            "id_inspeccion_vinculada": id_inspeccion,
            "token_puro": resultado_qr["token_puro"], # <--- ESTO LO COPIAS EN SWAGGER
            "qr_base64": resultado_qr["qr_base64"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar relevo: {str(e)}")
        
        
@app.post("/relevo/validar-qr", tags=["Relevo Digital"])
async def validar_qr_recepcion(
    token: str, 
    id_colaborador_entra: int, 
    db: Session = Depends(get_db)
):
    """
    PASO C: Simula al conductor que recibe. Valida el token y actualiza la BD.
    """
    # 1. Validamos el token digitalmente (Firma y Expiración)
    resultado = ejecutar_validacion_token(token)
    
    if resultado["status"] == "error":
        raise HTTPException(status_code=401, detail=resultado["message"])
    
    datos_token = resultado["data"]

    # 2. Buscamos el registro en la BD usando el token como llave
    relevo_db = db.query(TransferenciaRelevo).filter(
        TransferenciaRelevo.token_qr_hash == token
    ).first()

    if not relevo_db:
        raise HTTPException(status_code=404, detail="El registro de relevo no existe en la base de datos.")

    # 3. Actualizamos el registro para confirmar la recepción
    relevo_db.id_colaborador_entra = id_colaborador_entra
    relevo_db.confirmada = True
    db.commit()

    return {
        "mensaje": "¡Relevo verificado y confirmado exitosamente!",
        "datos_decodificados": {
            "placa": datos_token["placa"],
            "kilometraje_recibido": datos_token["km_entrega"]
        },
        "registro_db": "Actualizado (confirmada=True)"
    }
    
 # --- ENDPOINTS DE FORMULARIOS ---

@app.post("/inspeccion/crear", tags=["Formularios"])
async def registrar_inspeccion(id_colaborador: int, placa: str, km: float, estado: str, novedades: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Inyecta información técnica de la inspección a la base de datos.
    """
    nueva_inspeccion = Inspeccion(
        id_colaborador=id_colaborador,
        placa=placa,
        km_registro=km,
        estado_visual_ia=estado,
        novedades=novedades
    )
    db.add(nueva_inspeccion)
    db.commit()
    db.refresh(nueva_inspeccion)
    return {
        "status": "Inspección registrada con éxito",
        "id_inspeccion": nueva_inspeccion.id_inspeccion,
        "fecha": nueva_inspeccion.fecha_hora
        #"fecha": nueva_inspeccion.fecha_registro
    }

