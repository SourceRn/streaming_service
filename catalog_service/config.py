import os

class Settings:
    # Si la variable de entorno no existe, usa la cadena de conexión por defecto al clúster de Docker
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://mongo-primary:27017,mongo-sec1:27017,mongo-sec2:27017/?replicaSet=rs0")
    DB_NAME: str = os.getenv("DB_NAME", "streaming_db")

settings = Settings()