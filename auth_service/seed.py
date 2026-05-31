import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    # Conexión directa al Replica Set usando la variable de entorno
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    
    # Matriz de usuarios para pruebas de concurrencia
    users_to_seed = [
        {"username": "alice", "password": "password123", "role": "premium_user"},
        {"username": "bob", "password": "securepass456", "role": "standard_user"},
        {"username": "charlie", "password": "streaming789", "role": "premium_user"},
        {"username": "diana", "password": "adminpass321", "role": "admin"}
    ]

    print("Iniciando inyección masiva de usuarios...")
    
    for user in users_to_seed:
        # Encriptación de la contraseña en texto plano
        hashed_pw = pwd_context.hash(user["password"])
        
        # Inserción (Upsert para no duplicar si lo corres dos veces)
        await db["users"].update_one(
            {"username": user["username"]},
            {"$set": {"password": hashed_pw, "role": user["role"]}},
            upsert=True
        )
        print(f"Usuario '{user['username']}' verificado/creado exitosamente.")

    print("¡Base de datos poblada exitosamente!")

if __name__ == "__main__":
    asyncio.run(seed())