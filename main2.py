"""
Exemplo de uso do TranscriptionExporter integrado ao TranscriptionService.
"""

from app.services.transcription_service import TranscriptionService
from app.services.transcription_exporter import TranscriptionExporter


def main():
    service  = TranscriptionService(model_size="base", device="cpu", compute_type="int8")
    exporter = TranscriptionExporter()

    result = service.transcribe("data/input/aula_sample.mp4", language="pt")

    if not result["success"]:
        print("Erro na transcrição:", result["error"])
        return

    # --- Exportar um formato específico ---
    out = exporter.save(result, format="srt")
    print("SRT salvo em:", out["file_path"])

    # --- Exportar todos de uma vez ---
    all_out = exporter.save_all(
        result,
        formats=["srt", "vtt", "json", "docx"],
        output_dir="data/output",
    )

    for fmt, info in all_out["results"].items():
        status = "OK" if info["success"] else f"ERRO — {info['error']}"
        print(f"  {fmt:>5}: {status}")
        if info["success"]:
            print(f"         {info['file_path']}")


if __name__ == "__main__":
    main()