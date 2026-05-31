import os
import aiofiles
from fastapi import FastAPI, HTTPException, Header, Request, Depends, status, Query
from fastapi.responses import Response, StreamingResponse
import jwt
from config import settings

app = FastAPI()

def verify_token(authorization: str = Header(None), token: str = Query(None)) -> dict:
    """Middleware que acepta JWT por Header o por Query Parameter para el reproductor HTML5."""
    if not authorization and not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token faltante")
    
    # Extraemos el token crudo
    raw_token = authorization.split(" ")[1] if authorization else token
    
    try:
        with open(settings.PUBLIC_KEY_PATH, "r") as key_file:
            public_key = key_file.read()
            
        payload = jwt.decode(raw_token, public_key, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Firma RSA inválida o token expirado: {e}")

async def video_chunk_generator(file_path: str, start: int, end: int, chunk_size: int):
    """Generador asíncrono que lee únicamente la porción de bytes solicitada."""
    async with aiofiles.open(file_path, "rb") as video_file:
        await video_file.seek(start)
        bytes_to_read = (end - start) + 1
        
        while bytes_to_read > 0:
            read_size = min(chunk_size, bytes_to_read)
            data = await video_file.read(read_size)
            if not data:
                break
            bytes_to_read -= len(data)
            yield data

@app.get("/stream/{movie_id}")
async def stream_video(movie_id: str, request: Request, user: dict = Depends(verify_token)):
    """Endpoint que soporta peticiones de rango (Range Requests) con seguridad RBAC."""
    
    # ==========================================
    # 1. CAPA DE SEGURIDAD (RBAC - Role-Based Access Control)
    # ==========================================
    user_role = user.get("role", "standard_user")
    
    if movie_id in settings.PREMIUM_MOVIES and user_role != "premium_user":
        # Bloqueamos la petición a nivel de red antes de procesar archivos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado: Se requiere suscripción Premium para este contenido."
        )

    # ==========================================
    # 2. CAPA DE ALMACENAMIENTO
    # ==========================================
    video_path = os.path.join(settings.MEDIA_DIR, f"{movie_id}.mp4")
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de video no encontrado en el almacenamiento")

    file_size = os.path.getsize(video_path)
    
    # ==========================================
    # 3. CAPA DE NEGOCIACIÓN DE RANGOS
    # ==========================================
    range_header = request.headers.get("Range")
    
    if not range_header:
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4",
        }
        return Response(status_code=status.HTTP_200_OK, headers=headers)
    
    try:
        range_str = range_header.replace("bytes=", "").split("-")
        start = int(range_str[0])
        end = int(range_str[1]) if range_str[1] else min(start + settings.CHUNK_SIZE - 1, file_size - 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cabecera Range malformada")

    if start >= file_size or end >= file_size:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail="Rango fuera de los límites del archivo")

    content_length = (end - start) + 1

    # ==========================================
    # 4. DESPACHO DEL FRAGMENTO (HTTP 206)
    # ==========================================
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Type": "video/mp4",
    }

    return StreamingResponse(
        video_chunk_generator(video_path, start, end, settings.CHUNK_SIZE),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers=headers
    )