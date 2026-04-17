from app.services.transcription_service import TranscriptionService


def main():
    
    print("\nCarregando serviço de transcrição...\n")
    
    model = "tiny"  # Opções: tiny, base, small, medium (consistente), large-v1, large-v2 (preferível), large-v3, turbo
    service = TranscriptionService(
        model_size=model,
        device="cpu",
        compute_type="int8"
    )
    
    print("Iniciando transcrição...\n")
    result = service.transcribe_batch("data/input", language="pt")

    if not result["success"]:
        print("Erro:", result["error"])
        return

    print("Idioma detectado:", result["metadata"]["language"])
    print(f"Texto transcrito com o modelo {model}:")
    print(result["text"])


if __name__ == "__main__":
    main()