import os
from dotenv import load_dotenv

# Carga las variables desde el archivo .env
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo-primary:27017,mongo-sec1:27017,mongo-sec2:27017/?replicaSet=rs0")
    DB_NAME = os.getenv("DB_NAME", "streaming_db")
    PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "/secrets/private.pem")
    JWT_ALGORITHM = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

settings = Config()