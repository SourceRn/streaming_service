from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import jwt
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from config import settings

app = FastAPI()

# Configuración del hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración estricta de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, esto debería venir del config.py (ej. ["http://midominio.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente de Base de Datos
db_client = None
db = None

@app.on_event("startup")
async def startup_db_client():
    global db_client, db
    # Nos conectamos al Replica Set usando la variable centralizada
    db_client = AsyncIOMotorClient(settings.MONGO_URI)
    db = db_client[settings.DB_NAME]

@app.on_event("shutdown")
async def shutdown_db_client():
    db_client.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(username: str, role: str):
    with open(settings.PRIVATE_KEY_PATH, "r") as key_file:
        private_key = key_file.read()
    
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    
    return jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Búsqueda asíncrona del usuario en la colección 'users' de MongoDB
    user = await db["users"].find_one({"username": form_data.username})
    
    # Verificación contra el hash de bcrypt
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = create_jwt_token(form_data.username, user.get("role", "free_user"))
    return {"access_token": token, "token_type": "bearer"}