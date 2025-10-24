from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import gdown
from transcripte import transcrever_video_whisper

# Inicializa API
app = FastAPI(
    title="API de Transcrição de Vídeos",
    description="Transcreve vídeos locais ou do Google Drive usando Whisper (corrigido para máxima fidelidade)",
    version="2.0.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------
# 1️⃣ Endpoint - Upload direto de arquivo
# ---------------------------------------------------------------
@app.post("/transcrever/upload/")
async def transcrever_upload(file: UploadFile):
    try:
        temp_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"🎥 Arquivo recebido: {file.filename}")
        texto = transcrever_video_whisper(temp_path)

        if not texto:
            raise HTTPException(status_code=400, detail="Falha na transcrição")

        return JSONResponse({
            "status": "sucesso",
            "arquivo": file.filename,
            "tamanho_mb": round(os.path.getsize(temp_path) / (1024 * 1024), 2),
            "preview": texto[:600] + "...",
            "saida_txt": f"{os.path.splitext(temp_path)[0]}_transcricao.txt"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------
# 2️⃣ Endpoint - Link do Google Drive
# ---------------------------------------------------------------
@app.post("/transcrever/drive/")
async def transcrever_drive(link: str = Form(...)):
    try:
        print(f"🔗 Link recebido: {link}")
        arquivo_local = os.path.join(UPLOAD_DIR, "drive_video.mp4")

        gdown.download(link, arquivo_local, quiet=False)
        print(f"✅ Download concluído: {arquivo_local}")

        texto = transcrever_video_whisper(arquivo_local)

        if not texto:
            raise HTTPException(status_code=400, detail="Falha na transcrição")

        return JSONResponse({
            "status": "sucesso",
            "fonte": "Google Drive",
            "arquivo": arquivo_local,
            "preview": texto[:600] + "...",
            "saida_txt": f"{os.path.splitext(arquivo_local)[0]}_transcricao.txt"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------
# 3️⃣ Endpoint raiz - status
# ---------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "API ativa 🚀", "endpoints": ["/transcrever/upload", "/transcrever/drive"]}
