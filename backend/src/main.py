import argparse
import time
import sys
import os
from typing import List, Tuple, Callable, Any

from ordenacao.csv_io import ler_csv, criar_chave, obter_indice_coluna
from ordenacao.algoritmos import merge_sort, quick_sort, heap_sort


def gerar_nome_arquivo_saida(entrada: str, algoritmo: str, coluna: str, reverso: bool) -> str:
    nome_base = os.path.splitext(os.path.basename(entrada))[0]
    ordem = "dec" if reverso else "asc"
    return f"{nome_base}_{algoritmo}_{coluna}_{ordem}.csv"


def salvar_csv(caminho: str, dados: List[List[str]], cabecalho: List[str] = None):
    """Salva dados em arquivo CSV."""
    with open(caminho, 'w', encoding='utf-8', newline='') as f:
        if cabecalho:
            f.write(','.join(cabecalho) + '\n')
        for linha in dados:
            f.write(','.join(linha) + '\n')


def executar_algoritmo(
    algoritmo: Callable,
    nome_algoritmo: str,
    dados: List[List[str]],
    chave: Callable[[List[str]], Any],
    reverso: bool,
    arquivo_saida: str,
    cabecalho: List[str] = None
) -> float:
    print(f"  Executando {nome_algoritmo}...", end=" ", flush=True)
    
    inicio = time.perf_counter()
    resultado = algoritmo(dados, chave=chave, reverso=reverso)
    fim = time.perf_counter()
    
    tempo = fim - inicio
    print(f"concluído em {tempo:.6f} segundos")
    
    # Salvar resultado
    salvar_csv(arquivo_saida, resultado, cabecalho)
    print(f"    → Salvo em: {arquivo_saida}")
    
    return tempo


def main():
    parser = argparse.ArgumentParser(
        description="Ferramenta de ordenação de arquivos CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Ordenar com algoritmo específico
  python -m ordenacao.main dados.csv --coluna idade --tipo int --algoritmo merge
  
  # Executar todos os 3 algoritmos
  python -m ordenacao.main dados.csv --coluna idade --tipo int --run-all
  
  # Ordenação reversa com todos algoritmos
  python -m ordenacao.main dados.csv --coluna altura --tipo float --run-all --reverso
        """
    )
    
    # Argumentos obrigatórios
    parser.add_argument("arquivo", help="Caminho do arquivo CSV")
    
    # Argumentos de ordenação
    parser.add_argument("--coluna", required=True, help="Nome da coluna ou índice (0,1,2...)")
    parser.add_argument("--tipo", default="str", choices=["str", "int", "float"],
                        help="Tipo da coluna para ordenação (default: str)")
    parser.add_argument("--reverso", action="store_true",
                        help="Ordenação decrescente")
    
    # Seleção de algoritmo
    grupo_algoritmo = parser.add_mutually_exclusive_group()
    grupo_algoritmo.add_argument("--algoritmo", choices=["merge", "quick", "heap"],
                                 help="Algoritmo a ser utilizado")
    grupo_algoritmo.add_argument("--run-all", action="store_true",
                                 help="Executa os 3 algoritmos (Merge, Quick, Heap)")
    
    # Opções de cabeçalho
    parser.add_argument("--sem-cabecalho", action="store_true",
                        help="Indica que o CSV não possui linha de cabeçalho")
    
    args = parser.parse_args()
    
    # Verificar se o arquivo existe
    if not os.path.exists(args.arquivo):
        print(f"Erro: Arquivo '{args.arquivo}' não encontrado!")
        sys.exit(1)
    
    # Ler o CSV
    print(f"\nLendo arquivo: {args.arquivo}")
    try:
        if args.sem_cabecalho:
            # CSV sem cabeçalho
            with open(args.arquivo, 'r', encoding='utf-8') as f:
                linhas = [linha.strip().split(',') for linha in f if linha.strip()]
            cabecalho = None
            print(f"  → Modo sem cabeçalho")
        else:
            cabecalho, linhas = ler_csv(args.arquivo)
            print(f"  → Cabeçalho: {cabecalho}")
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        sys.exit(1)
    
    print(f"  → Total de linhas: {len(linhas)}")
    
    # Determinar índice da coluna
    if args.sem_cabecalho:
        try:
            indice = int(args.coluna)
        except ValueError:
            print(f"Erro: Para CSV sem cabeçalho, --coluna deve ser um número (0,1,2...)")
            sys.exit(1)
        nome_coluna = f"col{indice}"
    else:
        try:
            # Tentar como índice numérico primeiro
            indice = int(args.coluna)
            nome_coluna = cabecalho[indice] if indice < len(cabecalho) else f"col{indice}"
        except ValueError:
            # Tratar como nome de coluna
            try:
                indice = obter_indice_coluna(cabecalho, args.coluna)
                nome_coluna = args.coluna
            except ValueError as e:
                print(f"Erro: {e}")
                sys.exit(1)
    
    print(f"  → Coluna: '{nome_coluna}' (índice {indice})")
    print(f"  → Tipo: {args.tipo}")
    print(f"  → Ordem: {'Decrescente' if args.reverso else 'Crescente'}")
    
    # Criar função chave
    chave = criar_chave(indice, tipo=args.tipo)
    
    # Validar dados
    print(f"\n Validando dados da coluna...")
    erros = 0
    for i, linha in enumerate(linhas[:5]):  # Verifica apenas primeiras 5 linhas
        try:
            chave(linha)
        except Exception as e:
            print(f"  ⚠ Linha {i}: erro ao converter '{linha[indice]}' - {e}")
            erros += 1
    if erros == 0:
        print(f"  ✓ Todos os dados válidos")
    
    print("\n" + "=" * 70)
    
    # Executar algoritmos
    tempos = {}
    
    if args.run_all:
        print("EXECUTANDO TODOS OS 3 ALGORITMOS")
        print("-" * 70)
        
        # Gerar nome base para arquivos
        nome_base = os.path.splitext(os.path.basename(args.arquivo))[0]
        ordem = "dec" if args.reverso else "asc"
        
        # Merge Sort
        arquivo_merge = f"{nome_base}_merge_{nome_coluna}_{ordem}.csv"
        tempo_merge = executar_algoritmo(
            merge_sort, "Merge Sort", linhas, chave, args.reverso,
            arquivo_merge, cabecalho if not args.sem_cabecalho else None
        )
        tempos["Merge Sort"] = tempo_merge
        
        # Quick Sort
        arquivo_quick = f"{nome_base}_quick_{nome_coluna}_{ordem}.csv"
        tempo_quick = executar_algoritmo(
            quick_sort, "Quick Sort", linhas, chave, args.reverso,
            arquivo_quick, cabecalho if not args.sem_cabecalho else None
        )
        tempos["Quick Sort"] = tempo_quick
        
        # Heap Sort
        arquivo_heap = f"{nome_base}_heap_{nome_coluna}_{ordem}.csv"
        tempo_heap = executar_algoritmo(
            heap_sort, "Heap Sort", linhas, chave, args.reverso,
            arquivo_heap, cabecalho if not args.sem_cabecalho else None
        )
        tempos["Heap Sort"] = tempo_heap
        
        # Exibir resumo de tempos
        print("\n" + "=" * 70)
        print("RESUMO DE TEMPOS")
        print("=" * 70)
        
        for nome, tempo in tempos.items():
            print(f"  {nome:12} : {tempo:.6f} segundos")
        
        # Determinar o mais rápido
        mais_rapido = min(tempos, key=tempos.get)
        print(f"\n  ⚡ Mais rápido: {mais_rapido} ({tempos[mais_rapido]:.6f}s)")
        
        print("\nExecução concluída! Arquivos gerados:")
        print(f"   {arquivo_merge}")
        print(f"   {arquivo_quick}")
        print(f"   {arquivo_heap}")
        
    elif args.algoritmo:
        print(f"EXECUTANDO {args.algoritmo.upper()} SORT")
        print("-" * 70)
        
        # Mapear nome para função
        algoritmos_map = {
            "merge": merge_sort,
            "quick": quick_sort,
            "heap": heap_sort
        }
        
        algoritmo_func = algoritmos_map[args.algoritmo]
        nome_algoritmo = f"{args.algoritmo.capitalize()} Sort"
        
        # Gerar nome do arquivo
        arquivo_saida = gerar_nome_arquivo_saida(
            args.arquivo, args.algoritmo, nome_coluna, args.reverso
        )
        
        tempo = executar_algoritmo(
            algoritmo_func, nome_algoritmo, linhas, chave, args.reverso,
            arquivo_saida, cabecalho if not args.sem_cabecalho else None
        )
        
        print("\n" + "=" * 70)
        print(f"TEMPO TOTAL: {tempo:.6f} segundos")
        print(f"Arquivo gerado: {arquivo_saida}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()