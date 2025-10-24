import whisper
import os

def corrigir_palavras(texto):
    """
    Corrige variações incorretas de palavras específicas no texto.
    """
    substituicoes = {
        'Seg Hub': 'Sieg Hub',
        'SEG Hub': 'Sieg Hub', 
        'CegHub': 'Sieg Hub',
        'CIEG Hub': 'Sieg Hub',
        'Ceg Hub': 'Sieg Hub',
        'CIEG': 'Sieg',
        'Cieg': 'Sieg',
        'Autodox': 'Autodocs',
        'AutoDocs': 'Autodocs'
    }

    for palavra_errada, palavra_correta in substituicoes.items():
        texto = texto.replace(palavra_errada, palavra_correta)
    
    return texto

def transcrever_video_whisper(caminho_video):
    """
    Transcreve vídeo usando o Whisper original (OpenAI).
    Corrigido para capturar todo o áudio, inclusive trechos após longas pausas.
    """

    if not os.path.exists(caminho_video):
        print(f"❌ ERRO: Arquivo '{caminho_video}' não encontrado!")
        return None

    print("🔹 Carregando modelo Whisper turbo...")
    model = whisper.load_model("turbo")

    print(f"🎧 Transcrevendo: {caminho_video}\n")

    # Transcrição com parâmetros otimizados para não cortar finais
    resultado = model.transcribe(
        caminho_video,
        language="pt",
        fp16=False,
        verbose=False,
        temperature=0.2,
        no_speech_threshold=0.0,           # 🧩 Desativa corte por silêncio
        condition_on_previous_text=False,  # 🧩 Não interrompe por pausas
        suppress_blank=True,               # evita blocos vazios
        logprob_threshold=-2.0,            # aceita baixa confiança em trechos suaves
        compression_ratio_threshold=2.4,   # aceita compressão alta (voz + música)
    )

    print("\n" + "=" * 60)
    print("📝 TRANSCRIÇÃO COMPLETA COM TIMESTAMPS")
    print("=" * 60)

    for segment in resultado["segments"]:
        inicio = segment["start"]
        fim = segment["end"]
        texto = segment["text"].strip()
        texto_corrigido = corrigir_palavras(texto)
        print(f"[{inicio:.2f}s - {fim:.2f}s] {texto_corrigido}")

    texto_completo = resultado["text"]
    texto_completo_corrigido = corrigir_palavras(texto_completo)

    nome_base = os.path.splitext(caminho_video)[0]
    arquivo_saida = f"{nome_base}_transcricao.txt"

    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write(texto_completo_corrigido)

    print("\n" + "=" * 60)
    print(f"✅ Transcrição salva em: {arquivo_saida}")
    print("=" * 60)

    return texto_completo_corrigido


if __name__ == "__main__":
    video = "uploads/stefany (2160p).mp4"
    transcricao = transcrever_video_whisper(video)
    if transcricao:
        print("\n🧠 Trecho final:")
        print(transcricao[-500:])