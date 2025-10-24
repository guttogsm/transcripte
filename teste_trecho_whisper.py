import whisper

# Caminho do arquivo de áudio
audio_trecho = "uploads/stefany_trecho_0220_0240.wav"

print("🔹 Carregando modelo Whisper turbo...")
model = whisper.load_model("turbo")

print("🎧 Transcrevendo trecho 00:02:20–00:02:40...")
result = model.transcribe(audio_trecho, language="pt", fp16=False)

print("\n📝 Transcrição completa:")
print("=" * 60)
print(result["text"].strip())
print("=" * 60)
