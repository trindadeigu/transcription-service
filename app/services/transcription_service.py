from pathlib import Path
from typing import Optional, Dict, Any

from faster_whisper import WhisperModel


class TranscriptionService:
    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".flac", ".ogg"}

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

    def transcribe(self, file_path: str, language: Optional[str] = "pt") -> Dict[str, Any]:
        path = Path(file_path)

        if not path.exists():
            return {
                "success": False,
                "text": None,
                "segments": [],
                "error": f"Arquivo não encontrado: {file_path}"
            }

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return {
                "success": False,
                "text": None,
                "segments": [],
                "error": f"Formato não suportado: {path.suffix}",
                "suported_formats": list(self.SUPPORTED_EXTENSIONS)
            }

        try:
            segments, info = self.model.transcribe(str(path), language=language)

            segment_list = []
            full_text = []

            for segment in segments:
                text = segment.text.strip()

                segment_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": text
                })

                if text:
                    full_text.append(text)

            return {
                "success": True,
                "text": " ".join(full_text).strip(),
                "segments": segment_list,
                "error": None,
                "metadata": {
                    "file_name": path.name,
                    "file_path": str(path),
                    "language": getattr(info, "language", None),
                    "language_probability": getattr(info, "language_probability", None),
                    "duration": getattr(info, "duration", None)
                }
            }

        except Exception as e:
            return {
                "success": False,
                "text": None,
                "segments": [],
                "error": f"Erro ao transcrever arquivo: {str(e)}"
            }