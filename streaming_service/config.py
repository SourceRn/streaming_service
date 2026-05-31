import os

class Settings:
    MEDIA_DIR: str = os.getenv("MEDIA_DIR", "/media")
    PUBLIC_KEY_PATH: str = os.getenv("PUBLIC_KEY_PATH", "/secrets/public.pem")
    JWT_ALGORITHM: str = "RS256"
    CHUNK_SIZE: int = 1024 * 1024 
    
    # Política RBAC en memoria para evitar saturar la base de datos por cada HTTP 206
    PREMIUM_MOVIES: set = {
        "movie_7", "movie_8", "movie_9", 
        "movie_10", "movie_11", "movie_12", "movie_42"
    }

settings = Settings()