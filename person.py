import warnings
warnings.filterwarnings("ignore")

import os
import sys
import argparse
from tqdm import tqdm

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================
ARQUIVO_AUDIO = "teste.mp4"       # Nome do seu arquivo
NUM_PESSOAS = 2                    # Quantas pessoas falam no áudio
# ============================================================================

# CLI Argumentos
parser = argparse.ArgumentParser(description="Transcrição de vídeo com modo diagnóstico opcional")
parser.add_argument("--debug", action="store_true", help="Ativa o modo diagnóstico detalhado")
args = parser.parse_args()

# FIX WINDOWS
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
CACHE = os.path.join(os.getcwd(), "cache")
os.makedirs(CACHE, exist_ok=True)
os.environ["HF_HOME"] = CACHE

print("\n" + "=" * 80)
print("TRANSCRIÇÃO - FORMATO DIÁLOGO")
print("=" * 80)
print(f"Arquivo: {ARQUIVO_AUDIO}")
print(f"Pessoas: {NUM_PESSOAS}")
if args.debug:
    print("Modo diagnóstico: ATIVADO")
print("=" * 80 + "\n")

# Verifica arquivo
if not os.path.exists(ARQUIVO_AUDIO):
    print(f" ERRO: '{ARQUIVO_AUDIO}' não encontrado!")
    print(f"\nColoque o arquivo na pasta: {os.getcwd()}")
    sys.exit(1)

# CARREGA WHISPER
print("⏳ Carregando Whisper large-v3-turbo...")

try:
    from faster_whisper import WhisperModel
    
    model = WhisperModel(
        "large-v3-turbo",
        device="cpu",
        compute_type="int8",
        download_root=CACHE
    )
    
    print("Modelo carregado!\n")
    
except Exception as e:
    print(f" Erro ao carregar modelo: {e}")
    sys.exit(1)

# TRANSCREVE
print("🎙️  Transcrevendo...")

try:
    segments, info = model.transcribe(
        ARQUIVO_AUDIO,
        language="pt",
        beam_size=5,
        vad_filter=False,
        temperature=0.2,
        no_speech_threshold=0.05,
        word_timestamps=True
    )

    duracao = info.duration
    print(f"Duração: {duracao:.1f}s ({duracao/60:.1f} min)\n")

    segmentos = []

    with tqdm(total=int(duracao), desc="Progresso", unit="s", ncols=80) as pbar:
        ultimo_tempo = 0

        for i, seg in enumerate(segments):
            try:
                start = getattr(seg, 'start', 0)
                end = getattr(seg, 'end', start + 1)
                text = getattr(seg, 'text', '').strip()
                
                if not text:
                    continue

                pausa = 0
                if segmentos:
                    pausa = start - segmentos[-1]['end']

                segmentos.append({
                    "start": start,
                    "end": end,
                    "text": text,
                    "pausa": pausa
                })

                tempo_atual = int(end)
                if tempo_atual > ultimo_tempo:
                    incremento = min(tempo_atual - ultimo_tempo, int(duracao) - ultimo_tempo)
                    pbar.update(incremento)
                    ultimo_tempo = tempo_atual

                if args.debug and pausa > 2:
                    tqdm.write(f"⚠️ Gap detectado: {pausa:.2f}s entre {segmentos[-2]['end']:.2f}s e {start:.2f}s")

                if len(segmentos) % 20 == 0:
                    preview = text[:50] + "..." if len(text) > 50 else text
                    tqdm.write(f"   Seg {len(segmentos)}: {preview}")

            except Exception as e:
                print(f"\nErro no segmento {i}: {e}")
                continue

        if ultimo_tempo < int(duracao):
            pbar.update(int(duracao) - ultimo_tempo)

    if not segmentos:
        print("\n Nenhum segmento foi transcrito!")
        sys.exit(1)

    print(f"\n{len(segmentos)} segmentos transcritos!\n")

except Exception as e:
    print(f"\n Erro durante transcrição: {e}")
    sys.exit(1)

# Identificação de speakers
print("👥 Identificando speakers...")
try:
    pausas = [s['pausa'] for s in segmentos if s['pausa'] > 0]

    if pausas:
        pausa_media = sum(pausas) / len(pausas)
        threshold = max(pausa_media * 1.5, 0.8)
    else:
        threshold = 1.0

    speaker_atual = 0
    for i, seg in enumerate(segmentos):
        if i > 0 and seg['pausa'] > threshold:
            speaker_atual = (speaker_atual + 1) % NUM_PESSOAS
        seg['speaker'] = f"SPEAKER_{speaker_atual}"

except Exception as e:
    print(f"Erro na identificação de speakers: {e}")

# Salva os arquivos
print("\nSalvando arquivos...")

try:
    nome_base = os.path.splitext(ARQUIVO_AUDIO)[0]

    with open(f"{nome_base}_dialogo.txt", "w", encoding="utf-8") as f:
        for seg in segmentos:
            f.write(f"{seg['speaker']}\n\"{seg['text']}\"\n\n")

    with open(f"{nome_base}_com_tempo.txt", "w", encoding="utf-8") as f:
        for seg in segmentos:
            minutos = int(seg['start'] // 60)
            segundos = int(seg['start'] % 60)
            tempo = f"[{minutos:02d}:{segundos:02d}]"
            f.write(f"{tempo} {seg['speaker']}\n\"{seg['text']}\"\n\n")

    print("Arquivos salvos com sucesso!\n")

except Exception as e:
    print(f"Erro ao salvar arquivos: {e}")
