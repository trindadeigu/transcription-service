from app.services.transcription_service import TranscriptionService


def main():
    print("\nCarregando serviço de transcrição...\n")
    
    model = "large-v2"  # Opções: tiny, base, small, medium, large-v1, large-v2, large-v3
    
    service = TranscriptionService(
        model_size=model,
        device="cpu",
        compute_type="int8"
    )
    print("Iniciando transcrição...\n")
    result = service.transcribe("data/input/audio_teste.mp3", language="pt")

    if not result["success"]:
        print("Erro:", result["error"])
        return

    print("Idioma detectado:", result["metadata"]["language"])
    print(f"Texto transcrito em {model_size}:")
    print(result["text"])


if __name__ == "__main__":
    main()