import cv2
import os
import glob
import time

# Zero Hardcoding: Leemos la ruta desde las variables de entorno inyectadas por Docker
MEDIA_DIR = os.getenv("MEDIA_DIR", "/media")
# Frecuencia de escaneo en segundos
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", 60))
TARGET_FRAME = int(os.getenv("TARGET_FRAME", 100))

def process_new_videos():
    """Busca videos sin miniatura y genera el frame estático."""
    video_files = glob.glob(os.path.join(MEDIA_DIR, "*.mp4"))
    
    for video_path in video_files:
        filename = os.path.basename(video_path)
        movie_id, _ = os.path.splitext(filename)
        img_path = os.path.join(MEDIA_DIR, f"{movie_id}.jpg")

        # Principio de Idempotencia: Solo procesamos si la imagen NO existe
        if not os.path.exists(img_path):
            print(f"[Ingestion Worker] Nuevo video detectado: {filename}. Extrayendo frame 100...", flush=True)
            
            try:
                cap = cv2.VideoCapture(video_path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, TARGET_FRAME) 
                ret, frame = cap.read()
                
                if ret:
                    cv2.imwrite(img_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    print(f"[Ingestion Worker] Éxito: {movie_id}.jpg guardado.", flush=True)
                else:
                    print(f"[Ingestion Worker] Error: {filename} no tiene suficientes frames.", flush=True)
            except Exception as e:
                print(f"[Ingestion Worker] Error procesando {filename}: {e}", flush=True)
            finally:
                if 'cap' in locals():
                    cap.release()

if __name__ == "__main__":
    print("[Ingestion Worker] Iniciando vigilancia del directorio de medios...", flush=True)
    # Ciclo de vida del demonio (Daemon)
    while True:
        process_new_videos()
        # Dormimos el proceso para no consumir CPU innecesariamente
        time.sleep(SCAN_INTERVAL)