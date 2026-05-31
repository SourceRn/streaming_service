import asyncio
import logging
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

# Configuración centralizada de logging para el script
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

async def seed_movies() -> None:
    """
    Siembra la base de datos con el catálogo de clips de 2XKO (Ekko & Jinx).
    Incluye manejo de errores robusto para prevenir caídas de orquestación.
    """
    client: AsyncIOMotorClient = None
    
    try:
        # Zero Hardcoding: Conexión mediante variables de entorno
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[settings.DB_NAME]
        
        # Catálogo temático: Ekko (Point) & Jinx (Assist)
        clips: List[Dict[str, Any]] = [
            {
                "movie_id": "movie_1", "title": "Ekko/Jinx: Sinergia Básica", "genre": "Guía Básica", "year": 2024,
                "description": "Conceptos fundamentales para combinar los ataques rápidos de Ekko con la asistencia de fuego de cobertura de Jinx.",
                "required_role": "standard_user"
            },
            {
                "movie_id": "movie_2", "title": "Time Rewind & Flame Chompers", "genre": "Tutorial", "year": 2024,
                "description": "Cómo asegurar que el oponente caiga en las trampas de Jinx forzando el retroceso temporal de Ekko.",
                "required_role": "standard_user"
            },
            {
                "movie_id": "movie_3", "title": "Neutral Game: Zap! Control", "genre": "Highlights", "year": 2024,
                "description": "Uso del láser de Jinx (Assist) para controlar el espacio neutral y permitir que Ekko entre con su dash.",
                "required_role": "standard_user"
            },
            {
                "movie_id": "movie_4", "title": "Corner Carry Extensions", "genre": "Guía Básica", "year": 2025,
                "description": "Arrastra al oponente de esquina a esquina usando el Z-Drive de Ekko y los cohetes de Jinx para extender el combo.",
                "required_role": "standard_user"
            },
            {
                "movie_id": "movie_5", "title": "Ekko Mixups (High/Low) con Jinx", "genre": "Highlights", "year": 2025,
                "description": "Forzando al rival a adivinar la defensa mientras Jinx cubre tus opciones más arriesgadas en el suelo.",
                "required_role": "standard_user"
            },
            {
                "movie_id": "movie_6", "title": "EVO 2024 - Ekko/Jinx Pools", "genre": "Torneo", "year": 2024,
                "description": "Demostración de esta composición en las fases de grupo del EVO. Pura presión agresiva.",
                "required_role": "standard_user"
            },
            {
                "movie_id": "movie_7", "title": "Doble Súper: Z-Drive & Death Rocket", "genre": "Pro Guide", "year": 2025,
                "description": "Ruta óptima para conectar ambos ataques definitivos y maximizar el daño al gastar dos barras de súper.",
                "required_role": "premium_user"
            },
            {
                "movie_id": "movie_8", "title": "Dynamic Save: Jinx al Rescate", "genre": "Pro Guide", "year": 2025,
                "description": "Tiempos perfectos para usar a Jinx como rompedora de combos y salvar a Ekko de situaciones letales.",
                "required_role": "premium_user"
            },
            {
                "movie_id": "movie_9", "title": "Active Switch: Jinx Point", "genre": "Pro Guide", "year": 2025,
                "description": "Transiciones seguras para cambiar a Jinx como personaje principal cuando Ekko necesita recuperar vida gris.",
                "required_role": "premium_user"
            },
            {
                "movie_id": "movie_10", "title": "Grand Finals: Optimal Blockstrings", "genre": "Torneo", "year": 2024,
                "description": "Análisis de las cadenas de bloqueo infinitas usadas en la Gran Final con esta composición.",
                "required_role": "premium_user"
            },
            {
                "movie_id": "movie_11", "title": "Ekko ToD (Touch of Death)", "genre": "Análisis", "year": 2025,
                "description": "Combo de 100% de daño utilizando a Jinx en el momento exacto para evitar el drop por scaling.",
                "required_role": "premium_user"
            },
            {
                "movie_id": "movie_12", "title": "Frame Data: Castigando Whiffs", "genre": "Análisis", "year": 2025,
                "description": "Estudio de fotogramas para usar la movilidad de Ekko y castigar ataques fallidos del rival apoyado por Jinx.",
                "required_role": "premium_user"
            },
            {
                "movie_id": "movie_42", "title": "SonicFox (Ekko/Jinx) - Exhibition", "genre": "Torneo", "year": 2024,
                "description": "Exhibición magistral de SonicFox utilizando esta dupla, demostrando un juego neutral impecable.",
                "required_role": "premium_user"
            }
        ]
        
        # Operaciones de escritura
        await db["movies"].delete_many({})
        result = await db["movies"].insert_many(clips)
        
        logging.info(f"¡Catálogo de 2XKO (Ekko/Jinx) sembrado! {len(result.inserted_ids)} documentos insertados.")

    except Exception as e:
        logging.error(f"Fallo crítico al sembrar la base de datos: {e}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    asyncio.run(seed_movies())