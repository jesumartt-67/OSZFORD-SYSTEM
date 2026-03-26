import pyotp
from cryptography.hazmat.primitives.asymmetric import padding
# Otras librerías de seguridad necesarias

def generar_secreto_mfa():
    # """Genera una base32 aleatoria para el secreto del colaborador"""
    return pyotp.random_base32()

def obtener_codigo_qr_url(email, secreto):
    # """Genera la URL que el usuario escaneará en Google Authenticator"""
    return pyotp.totp.TOTP(secreto).provisioning_uri(
        name=email, 
        issuer_name="Oszford System"
    )

import pyotp

def verificar_codigo_mfa(secreto: str, codigo_ingresado: str):
    """
    Valida el código de 6 dígitos con un margen de tolerancia (valid_window).
    """
    if not secreto:
        return False
        
    # .strip() elimina espacios o saltos de línea invisibles de la base de datos
    totp = pyotp.TOTP(secreto.strip())
    
    # valid_window=1 permite que el código anterior o posterior sea válido (30s de margen)
    # Esto ayuda si el reloj del celular y la VM no están 100% idénticos
    return totp.verify(codigo_ingresado, valid_window=1)
        