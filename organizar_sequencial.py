import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
import uuid
from pathlib import Path


CAMINHO_PADRAO = Path("/run/media/ledilson/MUSIC/hinos")
EXTENSOES = {".mp3", ".m4a"}


def remover_numeracao(nome: str) -> str:
    """Remove uma numeração sequencial existente no início do nome."""
    return re.sub(r"^\d{1,3}\s*[-.\s]+", "", nome).strip()


def normalizar_espacos(nome: str) -> str:
    """Colapsa espaços múltiplos e remove espaços no início/fim do nome do arquivo,
    preservando a extensão."""
    caminho = Path(nome)
    stem_normalizado = re.sub(r"\s+", " ", caminho.stem).strip()
    return stem_normalizado + caminho.suffix


def remover_acentos(nome: str) -> str:
    """Remove acentos e caracteres não-ASCII do nome, preservando a extensão.
    Útil para aparelhos de som automotivo com suporte limitado a acentuação."""
    caminho = Path(nome)
    stem_normalizado = unicodedata.normalize("NFKD", caminho.stem)
    stem_sem_acentos = "".join(
        caractere for caractere in stem_normalizado if not unicodedata.combining(caractere)
    )
    stem_ascii = stem_sem_acentos.encode("ascii", "ignore").decode("ascii")
    return stem_ascii + caminho.suffix


def criar_plano(caminho: Path, remover_acentos_ativo: bool = False) -> list[tuple[Path, Path]]:
    arquivos = sorted(
        (
            arquivo
            for arquivo in caminho.iterdir()
            if arquivo.is_file() and arquivo.suffix.lower() in EXTENSOES
        ),
        key=lambda arquivo: arquivo.name.casefold(),
    )

    # Os M4A serão convertidos para MP3 antes da renomeação. Validar colisões
    # considerando o nome MP3 projetado evita sobrescrever um arquivo existente.
    nomes_mp3: dict[str, Path] = {}
    for arquivo in arquivos:
        nome_mp3 = arquivo.stem + ".mp3" if arquivo.suffix.lower() == ".m4a" else arquivo.name
        chave = nome_mp3.casefold()
        if chave in nomes_mp3:
            raise ValueError(
                f"conflito entre '{nomes_mp3[chave].name}' e '{arquivo.name}' "
                f"após conversão para MP3"
            )
        nomes_mp3[chave] = arquivo

    plano = []
    for numero, arquivo in enumerate(arquivos, start=1):
        nome_mp3 = arquivo.stem + ".mp3" if arquivo.suffix.lower() == ".m4a" else arquivo.name
        nome_limpo = remover_numeracao(nome_mp3)
        nome_limpo = normalizar_espacos(nome_limpo)
        if remover_acentos_ativo:
            nome_limpo = remover_acentos(nome_limpo)
        destino = caminho / f"{numero:03} - {nome_limpo}"
        plano.append((arquivo, destino))

    destinos = [destino.name.casefold() for _, destino in plano]
    if len(destinos) != len(set(destinos)):
        raise ValueError("há nomes duplicados depois da remoção da numeração antiga")

    return plano


def converter_m4a(arquivo: Path) -> Path:
    destino = arquivo.with_suffix(".mp3")
    if destino.exists():
        raise FileExistsError(f"o arquivo de destino já existe: {destino}")
    subprocess.run(
        ["ffmpeg", "-n", "-i", str(arquivo), "-codec:a", "libmp3lame", "-q:a", "2", str(destino)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    print(f"Convertido: {arquivo.name} → {destino.name}")
    return destino


def executar_plano(plano: list[tuple[Path, Path]]) -> None:
    # A etapa temporária evita que um arquivo sobrescreva outro durante a troca
    # de numeração.
    temporarios = []
    identificador = uuid.uuid4().hex

    for indice, (origem, destino) in enumerate(plano):
        m4a_original = None
        if origem.suffix.lower() == ".m4a":
            m4a_original = origem
            origem = converter_m4a(origem)
        temporario = origem.with_name(f".organizando-{identificador}-{indice}.tmp")
        origem.rename(temporario)
        temporarios.append((temporario, destino, origem.name, m4a_original))

    for temporario, destino, nome_original, m4a_original in temporarios:
        temporario.rename(destino)
        print(f"Renomeado: {nome_original} → {destino.name}")
        if m4a_original is not None:
            m4a_original.unlink()
            print(f"Removido: {m4a_original.name}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Converte arquivos M4A para MP3 e numera as músicas na raiz de um pendrive."
    )
    parser.add_argument(
        "caminho",
        nargs="?",
        type=Path,
        default=CAMINHO_PADRAO,
        help=f"pasta das músicas (padrão: {CAMINHO_PADRAO})",
    )
    parser.add_argument(
        "--executar",
        action="store_true",
        help="aplica as mudanças; sem esta opção, apenas mostra uma simulação",
    )
    parser.add_argument(
        "--remover-acentos",
        action="store_true",
        help="remove acentos e caracteres não-ASCII dos nomes (para aparelhos de som automotivo mais simples)",
    )
    argumentos = parser.parse_args()
    caminho = argumentos.caminho.expanduser()

    if not caminho.is_dir():
        print(f"Erro: pasta não encontrada: {caminho}", file=sys.stderr)
        return 1

    try:
        plano = criar_plano(caminho, remover_acentos_ativo=argumentos.remover_acentos)
    except (OSError, ValueError) as erro:
        print(f"Erro ao examinar as músicas: {erro}", file=sys.stderr)
        return 1

    if not plano:
        print(f"Nenhum arquivo MP3 ou M4A encontrado em: {caminho}")
        return 0

    if not argumentos.executar:
        print("SIMULAÇÃO — nenhum arquivo será alterado:\n")
        for origem, destino in plano:
            if origem.suffix.lower() == ".m4a":
                print(f"Converter: {origem.name} → {origem.stem}.mp3")
            print(f"{origem.name} → {destino.name}")
        print("\nPara aplicar, execute novamente com a opção --executar.")
        return 0

    if any(origem.suffix.lower() == ".m4a" for origem, _ in plano) and not shutil.which("ffmpeg"):
        print("Erro: ffmpeg não encontrado. Instale o ffmpeg para converter arquivos M4A.", file=sys.stderr)
        return 1

    try:
        executar_plano(plano)
    except (OSError, subprocess.CalledProcessError) as erro:
        detalhe = getattr(erro, "stderr", None)
        if detalhe:
            print(f"Erro durante a conversão/renomeação: {detalhe.strip()}", file=sys.stderr)
        else:
            print(f"Erro durante a conversão/renomeação: {erro}", file=sys.stderr)
        return 1

    print(f"\nConcluído: {len(plano)} música(s) organizada(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())