from __future__ import annotations

import csv
from typing import Callable, List, Tuple


def ler_csv(
    caminho: str,
    delimitador: str = ",",
    encoding: str = "utf-8",
) -> Tuple[List[str], List[List[str]]]:
    """Le um CSV com cabecalho obrigatorio e retorna (cabecalho, linhas)."""
    with open(caminho, "r", encoding=encoding, newline="") as arquivo:
        leitor = csv.reader(arquivo, delimiter=delimitador)
        linhas = list(leitor)

    if not linhas:
        raise ValueError("Arquivo CSV vazio.")

    cabecalho = linhas[0]
    dados = linhas[1:]
    if not dados:
        raise ValueError("Arquivo CSV sem linhas de dados.")

    return cabecalho, dados


def obter_indice_coluna(cabecalho: List[str], coluna: str) -> int:
    """Retorna o indice da coluna pelo nome, validando existencia."""
    try:
        return cabecalho.index(coluna)
    except ValueError as exc:
        raise ValueError(f"Coluna nao encontrada no cabecalho: {coluna}") from exc


def criar_conversor(tipo: str) -> Callable[[str], object]:
    """Cria conversor de string para str/int/float conforme tipo."""
    if tipo == "int":
        return int
    if tipo == "float":
        return float
    if tipo == "str":
        return str
    raise ValueError("Tipo de chave invalido. Use: str, int, float.")


def criar_chave(indice_coluna: int, tipo: str = "str") -> Callable[[List[str]], object]:
    """Cria funcao chave para ordenar, com validacao e conversao."""
    conversor = criar_conversor(tipo)

    def _chave(linha: List[str]) -> object:
        try:
            return conversor(linha[indice_coluna])
        except IndexError as exc:
            raise ValueError("Linha nao possui a coluna informada.") from exc
        except ValueError as exc:
            raise ValueError("Falha ao converter valor da coluna.") from exc

    return _chave
