from pathlib import Path
from typing import Optional, Dict, Any, List

from faster_whisper import WhisperModel


class TranscriptionService:
    # Formatos de entrada aceitos pelo modelo
    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".flac", ".ogg"}

    def __init__(
        self,
        model_size: str = "base",   # Opções: tiny, base, small, medium, large-v1, large-v2, large-v3
        device: str = "cpu",        # Opções: "cpu", "cuda" (NVIDIA) — AMD não suporta cuda
        compute_type: str = "int8"  # Opções: "int8" (cpu), "float16" / "int8_float16" (cuda)
    ):
        # Carrega o modelo na inicialização — custo alto feito uma vez, reutilizado em todas as transcrições
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

    def transcribe(self, file_path: str, language: Optional[str] = "pt") -> Dict[str, Any]:
        path = Path(file_path)

        # Validações fail-fast — retornam antes de chegar ao modelo
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
            
        info = None  # Variável para armazenar metadados do áudio, mesmo em caso de erro

        try:
            # model.transcribe() retorna um gerador de segmentos + objeto info com metadados do áudio
            segments, info = self.model.transcribe(str(path), language=language)

            segment_list = []
            full_text = []

            # Itera o gerador — os segmentos são processados sob demanda, não todos de uma vez
            for segment in segments:
                text = segment.text.strip()

                segment_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": text
                })

                # Segmentos vazios são ignorados no texto completo mas preservados na lista de segmentos
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
                    # getattr com fallback None — campos podem não existir dependendo da versão do modelo
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
                # Metadados preservados mesmo no erro — útil para rastrear qual arquivo falhou
                "metadata": {
                    "file_name": path.name,
                    "file_path": str(path),
                    "language": getattr(info, "language", None),
                    "language_probability": getattr(info, "language_probability", None),
                    "duration": getattr(info, "duration", None)
                }
            }

    def transcribe_batch(
        self,
        input_dir: str = "data/input",
        language: Optional[str] = "pt",
        print_result: bool = False,   # Se True, imprime o resultado de cada arquivo no terminal
    ) -> Dict[str, Any]:
        
        input_path = Path(input_dir)

        # Validações do diretório — fail-fast antes de qualquer transcrição
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

        # Filtra apenas arquivos com extensões suportadas — ignora subdiretórios e outros arquivos
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

        # Itera sem interrupção — falha em um arquivo não cancela os demais
        for file in files:
            result = self.transcribe(str(file), language=language)

            item = {
                "file": file.name,
                "result": result
            }

            results.append(item)
            
            # Feedback imediato no terminal — útil para monitorar lotes longos
            if print_result:
                print(f"Arquivo: {file.name}")
                if result.get("success"):
                    print(f"Transcrição: {result.get('text')}\n")
                else:
                    print(f"Erro: {result.get('error')}\n")

        # Contadores derivados dos resultados — calculados ao final, não incrementados no loop
        success_count = sum(1 for item in results if item["result"].get("success"))
        error_count = len(results) - success_count

        return {
            "success": True,  # True mesmo com erros parciais — indica que o batch executou
            "results": results,
            "summary": {
                "total_files": len(results),
                "success_count": success_count,
                "error_count": error_count
            },
            "error": None
        }