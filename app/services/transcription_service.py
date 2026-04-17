from pathlib import Path
from typing import Optional, Dict, Any, List

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
                "error": f"Erro ao transcrever arquivo: {str(e)}",
                "metadata": {
                    "file_name": path.name,
                    "file_path": str(path),
                    "language": getattr(info, "language", None),
                    "language_probability": getattr(info, "language_probability", None),
                    "duration": getattr(info, "duration", None)
                }
            }
            
    def save_as_txt(
        self,
        result: Dict[str, Any],
        output_dir: str = "data/output",
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        if not result.get("success"):
            return {
                "success": False,
                "file_path": None,
                "error": "Não é possível salvar TXT de uma transcrição com erro."
            }

        text = result.get("text")
        if not text:
            return {
                "success": False,
                "file_path": None,
                "error": "A transcrição não possui texto para salvar."
            }

        metadata = result.get("metadata", {})
        original_file_name = metadata.get("file_name", "transcricao")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        final_name = file_name if file_name else Path(original_file_name).stem
        txt_path = output_path / f"{final_name}.txt"

        try:
            txt_path.write_text(text, encoding="utf-8")

            return {
                "success": True,
                "file_path": str(txt_path),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "file_path": None,
                "error": f"Erro ao salvar TXT: {str(e)}"
            }

    def transcribe_batch(
        self,
        input_dir: str = "data/input",
        language: Optional[str] = "pt",
        save_txt: bool = False,
        output_dir: str = "data/output",
        print_result: bool = False,
    ) -> Dict[str, Any]:
        input_path = Path(input_dir)

        if not input_path.exists():
            return {
                "success": False,
                "results": [],
                "error": f"Diretório não encontrado: {input_dir}"
            }

        if not input_path.is_dir():
            return {
                "success": False,
                "results": [],
                "error": f"O caminho informado não é um diretório: {input_dir}"
            }

        files = [
            file for file in input_path.iterdir()
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]

        if not files:
            return {
                "success": False,
                "results": [],
                "error": "Nenhum arquivo de mídia suportado encontrado no diretório."
            }

        results = []

        for file in files:
            result = self.transcribe(str(file), language=language)

            item = {
                "file": file.name,
                "result": result
            }

            if save_txt and result.get("success"):
                save_result = self.save_as_txt(
                    result=result,
                    output_dir=output_dir
                )
                item["txt_save"] = save_result

            results.append(item)
            if print_result:
                print(f"Arquivo: {file.name}")
                if result.get("success"):
                    print(f"Transcrição: {result.get('text')}\n")
                else:
                    print(f"Erro: {result.get('error')}\n")

        success_count = sum(1 for item in results if item["result"].get("success"))
        error_count = len(results) - success_count

        return {
            "success": True,
            "results": results,
            "summary": {
                "total_files": len(results),
                "success_count": success_count,
                "error_count": error_count
            },
            "error": None
        }