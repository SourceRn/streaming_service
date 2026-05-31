from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente global de BD
db_client = None
db = None

@app.on_event("startup")
async def startup_db_client():
    global db_client, db
    db_client = AsyncIOMotorClient(settings.MONGO_URI)
    db = db_client[settings.DB_NAME]

@app.on_event("shutdown")
async def shutdown_db_client():
    db_client.close()

@app.get("/movies")
async def get_all_movies():
    """Retorna la lista completa del catálogo."""
    try:
        # Explicación Arquitectónica: Usamos {"_id": 0} para excluir el ObjectId nativo de Mongo.
        # Si no lo excluimos, FastAPI arrojará un Internal Server Error porque ObjectId no es serializable a JSON.
        movies_cursor = db["movies"].find({}, {"_id": 0})
        movies = await movies_cursor.to_list(length=100)
        return {"catalog": movies}
    except Exception as e:
        # Manejo de errores robusto
        raise HTTPException(status_code=500, detail=f"Error interno de base de datos: {str(e)}")

@app.get("/movies/{movie_id}")
async def get_movie_by_id(movie_id: str):
    """Retorna los metadatos de una sola película."""
    movie = await db["movies"].find_one({"movie_id": movie_id}, {"_id": 0})
    if not movie:
        raise HTTPException(status_code=404, detail="Película no encontrada en el catálogo")
    return movie