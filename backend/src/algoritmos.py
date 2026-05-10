from __future__ import annotations
from typing import Callable, List, TypeVar

T = TypeVar("T")


def merge_sort(itens: List[T], chave: Callable[[T], object], reverso: bool = False) -> List[T]:
    """Retorna uma nova lista ordenada usando MergeSort."""
    if len(itens) <= 1:
        return itens[:]

    meio = len(itens) // 2
    esquerda = merge_sort(itens[:meio], chave=chave, reverso=reverso)
    direita = merge_sort(itens[meio:], chave=chave, reverso=reverso)

    return _mesclar(esquerda, direita, chave=chave, reverso=reverso)


def _mesclar(
    esquerda: List[T],
    direita: List[T],
    chave: Callable[[T], object],
    reverso: bool,
) -> List[T]:
    resultado: List[T] = []
    i = 0
    j = 0

    while i < len(esquerda) and j < len(direita):
        chave_esq = chave(esquerda[i])
        chave_dir = chave(direita[j])

        if reverso:
            pega_esquerda = chave_esq > chave_dir
        else:
            pega_esquerda = chave_esq <= chave_dir

        if pega_esquerda:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1

    if i < len(esquerda):
        resultado.extend(esquerda[i:])
    if j < len(direita):
        resultado.extend(direita[j:])

    return resultado


def quick_sort(itens: List[T], chave: Callable[[T], object], reverso: bool = False) -> List[T]:
    """Retorna uma nova lista ordenada usando QuickSort."""
    resultado = itens[:]
    if len(resultado) <= 1:
        return resultado

    _quick_sort_in_place(resultado, 0, len(resultado) - 1, chave=chave, reverso=reverso)
    return resultado


def _quick_sort_in_place(
    itens: List[T],
    baixo: int,
    alto: int,
    chave: Callable[[T], object],
    reverso: bool,
) -> None:
    if baixo >= alto:
        return

    indice_pivo = _particionar(itens, baixo, alto, chave=chave, reverso=reverso)
    _quick_sort_in_place(itens, baixo, indice_pivo - 1, chave=chave, reverso=reverso)
    _quick_sort_in_place(itens, indice_pivo + 1, alto, chave=chave, reverso=reverso)


def _particionar(
    itens: List[T],
    baixo: int,
    alto: int,
    chave: Callable[[T], object],
    reverso: bool,
) -> int:
    indice_pivo = _mediana_de_tres(itens, baixo, alto, chave=chave, reverso=reverso)
    itens[indice_pivo], itens[alto] = itens[alto], itens[indice_pivo]
    chave_pivo = chave(itens[alto])

    indice_troca = baixo
    for i in range(baixo, alto):
        chave_atual = chave(itens[i])
        if reverso:
            deve_trocar = chave_atual > chave_pivo
        else:
            deve_trocar = chave_atual < chave_pivo

        if deve_trocar:
            itens[indice_troca], itens[i] = itens[i], itens[indice_troca]
            indice_troca += 1

    itens[indice_troca], itens[alto] = itens[alto], itens[indice_troca]
    return indice_troca


def _mediana_de_tres(
    itens: List[T],
    baixo: int,
    alto: int,
    chave: Callable[[T], object],
    reverso: bool,
) -> int:
    meio = (baixo + alto) // 2
    chave_baixo = chave(itens[baixo])
    chave_meio = chave(itens[meio])
    chave_alto = chave(itens[alto])

    if reverso:
        if chave_baixo >= chave_meio:
            if chave_meio >= chave_alto:
                return meio
            if chave_baixo >= chave_alto:
                return alto
            return baixo
        if chave_baixo >= chave_alto:
            return baixo
        if chave_meio >= chave_alto:
            return alto
        return meio

    if chave_baixo <= chave_meio:
        if chave_meio <= chave_alto:
            return meio
        if chave_baixo <= chave_alto:
            return alto
        return baixo
    if chave_baixo <= chave_alto:
        return baixo
    if chave_meio <= chave_alto:
        return alto
    return meio


def heap_sort(itens: List[T], chave: Callable[[T], object], reverso: bool = False) -> List[T]:
    """Retorna uma nova lista ordenada usando HeapSort."""
    resultado = itens[:]
    tamanho = len(resultado)
    if tamanho <= 1:
        return resultado

    _construir_heap(resultado, tamanho, chave=chave, reverso=reverso)

    for fim in range(tamanho - 1, 0, -1):
        resultado[0], resultado[fim] = resultado[fim], resultado[0]
        _descer(resultado, 0, fim, chave=chave, reverso=reverso)

    return resultado


def _construir_heap(
    itens: List[T],
    tamanho: int,
    chave: Callable[[T], object],
    reverso: bool,
) -> None:
    for indice in range((tamanho // 2) - 1, -1, -1):
        _descer(itens, indice, tamanho, chave=chave, reverso=reverso)


def _descer(
    itens: List[T],
    inicio: int,
    fim: int,
    chave: Callable[[T], object],
    reverso: bool,
) -> None:
    raiz = inicio
    while True:
        esquerda = (raiz * 2) + 1
        if esquerda >= fim:
            return

        direita = esquerda + 1
        troca = raiz

        if _comparar(itens[esquerda], itens[troca], chave=chave, reverso=reverso):
            troca = esquerda
        if direita < fim and _comparar(itens[direita], itens[troca], chave=chave, reverso=reverso):
            troca = direita

        if troca == raiz:
            return

        itens[raiz], itens[troca] = itens[troca], itens[raiz]
        raiz = troca


def _comparar(a: T, b: T, chave: Callable[[T], object], reverso: bool) -> bool:
    if reverso:
        return chave(a) < chave(b)
    return chave(a) > chave(b)
