from app.services.transcription_service import TranscriptionService


def main():
    
    print("\nCarregando serviço de transcrição...\n")
    
    model = "large-v2"  # Opções: tiny, base, small, medium (consistente), large-v1, large-v2 (preferível), large-v3, turbo
    service = TranscriptionService(
        model_size=model,
        device="cpu",
        compute_type="int8"
    )
    
    print("Iniciando transcrição...\n")
    result = service.transcribe_batch(save_txt=True, print_result=True)

if __name__ == "__main__":
    main()