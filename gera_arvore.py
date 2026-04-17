from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional

'''
Como usar:

python gera_arvore.py --output-txt arvore_projeto.txt

'''

def gerar_arvore_projeto(
    raiz: Path | str = ".",
    *,
    ignorar_pastas: Iterable[str] = (".git", ".venv", "__pycache__", ".pytest_cache"),
    ignorar_arquivos: Iterable[str] = (".DS_Store", "gera_arvore"),
    incluir_ocultos: bool = False,
    max_profundidade: Optional[int] = None,
    ordenar: str = "pastas_primeiro",  # "pastas_primeiro" | "nome"
) -> str:
    raiz_path = Path(raiz).resolve()

    if not raiz_path.exists():
        raise FileNotFoundError(f"Raiz não encontrada: {raiz_path}")

    ignorar_pastas_set = set(ignorar_pastas)
    ignorar_arquivos_set = set(ignorar_arquivos)

    def _deve_ignorar(p: Path) -> bool:
        nome = p.name
        if not incluir_ocultos and nome.startswith("."):
            return True
        if p.is_dir() and nome in ignorar_pastas_set:
            return True
        if p.is_file() and nome in ignorar_arquivos_set:
            return True
        return False

    def _listar_filhos(pasta: Path) -> list[Path]:
        filhos = [p for p in pasta.iterdir() if not _deve_ignorar(p)]
        if ordenar == "pastas_primeiro":
            filhos.sort(key=lambda x: (x.is_file(), x.name.lower()))
        else:
            filhos.sort(key=lambda x: x.name.lower())
        return filhos

    linhas: list[str] = [f"{raiz_path.name}/"]

    def _walk(pasta: Path, prefixo: str, nivel: int) -> None:
        if max_profundidade is not None and nivel >= max_profundidade:
            return

        filhos = _listar_filhos(pasta)
        total = len(filhos)

        for i, filho in enumerate(filhos):
            ultimo = i == (total - 1)
            conector = "└── " if ultimo else "├── "

            nome = f"{filho.name}/" if filho.is_dir() else filho.name
            linhas.append(prefixo + conector + nome)

            if filho.is_dir():
                novo_prefixo = prefixo + ("    " if ultimo else "│   ")
                _walk(filho, novo_prefixo, nivel + 1)

    _walk(raiz_path, prefixo="", nivel=0)
    return "\n".join(linhas)


def _parse_csv_list(value: str) -> list[str]:
    # aceita "a,b,c" ou "a, b, c"
    parts = [p.strip() for p in (value or "").split(",")]
    return [p for p in parts if p]


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="gera_arvore",
        description="Gera uma árvore de diretórios/arquivos (estilo tree) para documentação.",
    )
    parser.add_argument(
        "-r",
        "--raiz",
        default=".",
        help="Caminho raiz do projeto (default: .).",
    )
    parser.add_argument(
        "--max-profundidade",
        type=int,
        default=None,
        help="Limita a profundidade de pastas (ex: 3).",
    )
    parser.add_argument(
        "--incluir-ocultos",
        action="store_true",
        help="Inclui arquivos/pastas ocultos (prefixo '.').",
    )
    parser.add_argument(
        "--ignorar-pastas",
        default=",.git,.venv,__pycache__,.pytest_cache".replace(",,", ","),
        help="Lista separada por vírgulas de pastas ignoradas.",
    )
    parser.add_argument(
        "--ignorar-arquivos",
        default=".DS_Store",
        help="Lista separada por vírgulas de arquivos ignorados.",
    )
    parser.add_argument(
        "--ordenar",
        choices=["pastas_primeiro", "nome"],
        default="pastas_primeiro",
        help="Ordenação de itens.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Se informado, salva a saída em arquivo (ex: README_TREE.txt).",
    )
    parser.add_argument(
        "--output-txt",
        default=None,
        help="Se informado, salva a saída também em arquivo .txt (ex: arvore_projeto.txt).",
    )

    args = parser.parse_args()

    ignorar_pastas = _parse_csv_list(args.ignorar_pastas)
    ignorar_arquivos = _parse_csv_list(args.ignorar_arquivos)

    texto = gerar_arvore_projeto(
        args.raiz,
        ignorar_pastas=ignorar_pastas,
        ignorar_arquivos=ignorar_arquivos,
        incluir_ocultos=args.incluir_ocultos,
        max_profundidade=args.max_profundidade,
        ordenar=args.ordenar,
    )

    # stdout (para visualizar / pipe / redirecionar)
    print(texto)

    # opcional: salvar em arquivo (qualquer extensão)
    if args.output:
        Path(args.output).write_text(texto + "\n", encoding="utf-8")

    # opcional: salvar em arquivo txt
    if args.output_txt:
        output_txt = Path(args.output_txt)
        if output_txt.suffix.lower() != ".txt":
            output_txt = output_txt.with_suffix(".txt")
        output_txt.write_text(texto + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())    