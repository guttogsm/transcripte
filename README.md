\# 🎧 Transcripte – API de Transcrição de Vídeos (FastAPI + Whisper)



Uma API simples e eficiente para \*\*transcrever vídeos automaticamente\*\* usando o modelo \*\*Whisper\*\* da OpenAI.  

Suporta \*\*upload direto\*\* e \*\*links do Google Drive\*\*, com resultados salvos em `.txt` e preview via API.



---



\## 🚀 Tecnologias Utilizadas



\- \*\*Python 3.10+\*\*

\- \*\*FastAPI\*\* (backend leve e rápido)

\- \*\*Whisper (OpenAI)\*\* – modelo de transcrição

\- \*\*gdown\*\* – download direto do Google Drive

\- \*\*Uvicorn\*\* – servidor ASGI para execução local



---



\## 📦 Instalação



\### 1️⃣ Clone o repositório

```bash

git clone https://github.com/guttogsm/transcripte.git

cd transcripte



2️⃣ Crie o ambiente virtual e ative

python -m venv .venv

.venv\\Scripts\\Activate.ps1   # PowerShell no Windows

\# ou

source .venv/bin/activate    # Linux / macOS



3️⃣ Instale as dependências

pip install -r requirements.txt





💡 Se for a primeira vez rodando Whisper, o modelo “turbo” será baixado automaticamente (~1.4 GB).



▶️ Execução da API



Inicie o servidor local:



uvicorn api\_transcricao:app --reload
ou
python -m uvicorn api_transcricao:app --reload





Acesse a documentação interativa:

👉 http://127.0.0.1:8000/docs



🧩 Endpoints Principais

🔹 POST /transcrever/upload/



Faz upload de um vídeo local e retorna a transcrição.



Exemplo via curl:



curl -X POST "http://127.0.0.1:8000/transcrever/upload/" ^

&nbsp; -F "file=@uploads/video.mp4"





Resposta:



{

&nbsp; "status": "sucesso",

&nbsp; "arquivo": "video.mp4",

&nbsp; "tamanho\_mb": 42.3,

&nbsp; "preview": "Olá, tudo bem? Hoje vamos falar sobre...",

&nbsp; "saida\_txt": "uploads/video\_transcricao.txt"

}



🔹 POST /transcrever/drive/



Baixa e transcreve vídeos diretamente de um link do Google Drive.



Exemplo via curl:



curl -X POST "http://127.0.0.1:8000/transcrever/drive/" ^

&nbsp; -F "link=https://drive.google.com/uc?id=SEU\_ID\_DO\_VIDEO"



🔹 GET /



Endpoint raiz de status:



{

&nbsp; "status": "API ativa 🚀",

&nbsp; "endpoints": \["/transcrever/upload", "/transcrever/drive"]

}



📂 Estrutura do Projeto

transcripte/

├── api\_transcricao.py        # API FastAPI principal

├── transcripte.py            # Função de transcrição Whisper

├── person.py                 # Script auxiliar (correções e testes)

├── requirements.txt          # Dependências

├── uploads/                  # Pasta de vídeos enviados

├── modelos\_cache/            # Cache opcional do Whisper

└── whisper\_cache/            # Cache dos modelos baixados



🧾 Logs e Saídas



Cada vídeo transcrito gera um arquivo .txt com o mesmo nome:



uploads/

&nbsp;├── video.mp4

&nbsp;└── video\_transcricao.txt





O terminal exibe o progresso completo da transcrição com timestamps e correções automáticas.



⚙️ Personalização



Você pode alterar o modelo de transcrição (ex.: base, small, large) editando esta linha no arquivo transcripte.py:



model = whisper.load\_model("turbo")



