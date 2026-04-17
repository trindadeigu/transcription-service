from app.services.transcription_service import TranscriptionService


def transcritor(model=str):
    print("\nCarregando serviço de transcrição...\n")
    
    #model = "small"  # Opções: tiny, base, small, medium, large
    
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
    print(f"Texto transcrito em {model}:")
    print(result["text"])
    
def main():
    model_size = ["tiny",
                  "base",
                  "small",
                  "medium",
                  "large-v1",
                  "large-v2",
                  "large-v3"]
    for model in model_size:
        transcritor(model)

if __name__ == "__main__":
    main()