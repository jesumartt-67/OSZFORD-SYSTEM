import jwt
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timedelta

SECRET_KEY = "OSZFORD_SUPER_SECRET_2026"
ALGORITHM = "HS256"

def ejecutar_generacion_qr(id_inspeccion: int, id_colaborador: int, placa: str, km_entrega: float):
    payload = {
        "id_inspeccion": id_inspeccion,
        "id_colaborador": id_colaborador,
        "placa": placa,
        "km_entrega": float(km_entrega),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    qr = qrcode.make(token_jwt)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    return {"token_puro": token_jwt, "qr_base64": f"data:image/png;base64,{qr_base64}"}

def ejecutar_validacion_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"status": "success", "data": payload}
    except Exception as e:
        return {"status": "error", "message": str(e)}