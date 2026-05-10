import pytest

from algoritmos import heap_sort, merge_sort, quick_sort


@pytest.fixture()
def lista_numeros():
    return [5, 3, 8, 1, 2]


@pytest.fixture()
def lista_tuplas():
    return [("ana", 3), ("bob", 1), ("carla", 2)]


def test_merge_sort_numeros(lista_numeros):
    resultado = merge_sort(lista_numeros, chave=lambda x: x)
    assert resultado == [1, 2, 3, 5, 8]


def test_merge_sort_reverso(lista_numeros):
    resultado = merge_sort(lista_numeros, chave=lambda x: x, reverso=True)
    assert resultado == [8, 5, 3, 2, 1]


def test_quick_sort_tuplas(lista_tuplas):
    resultado = quick_sort(lista_tuplas, chave=lambda x: x[1])
    assert resultado == [("bob", 1), ("carla", 2), ("ana", 3)]


def test_heap_sort_tuplas_reverso(lista_tuplas):
    resultado = heap_sort(lista_tuplas, chave=lambda x: x[1], reverso=True)
    assert resultado == [("ana", 3), ("carla", 2), ("bob", 1)]


def test_lista_original_nao_muda(lista_numeros):
    original = lista_numeros[:]
    merge_sort(lista_numeros, chave=lambda x: x)
    quick_sort(lista_numeros, chave=lambda x: x)
    heap_sort(lista_numeros, chave=lambda x: x)
    assert lista_numeros == original
