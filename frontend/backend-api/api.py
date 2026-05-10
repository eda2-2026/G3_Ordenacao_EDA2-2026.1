from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import time

# Adicionar path do backend original
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src'))

from ordenacao.algoritmos import merge_sort, quick_sort, heap_sort
from ordenacao.csv_io import criar_chave

app = Flask(__name__)
CORS(app)

@app.route('/api/sort', methods=['POST'])
def sort_csv():
    data = request.json
    csv_text = data['csv']
    coluna = data['coluna']
    tipo = data['tipo']
    reverso = data['reverso']
    algoritmos = data['algoritmos']
    
    # Parse CSV
    linhas = csv_text.strip().split('\n')
    cabecalho = linhas[0]
    dados = [linha.split(',') for linha in linhas[1:] if linha.strip()]
    
    # Criar função chave
    chave = criar_chave(coluna, tipo=tipo)
    
    # Executar algoritmos
    tempos = {}
    arquivos = {}
    
    for alg in algoritmos:
        dados_copia = [linha[:] for linha in dados]
        
        inicio = time.perf_counter()
        
        if alg == 'merge':
            resultado = merge_sort(dados_copia, chave=chave, reverso=reverso)
        elif alg == 'quick':
            resultado = quick_sort(dados_copia, chave=chave, reverso=reverso)
        elif alg == 'heap':
            resultado = heap_sort(dados_copia, chave=chave, reverso=reverso)
        
        fim = time.perf_counter()
        tempos[alg] = fim - inicio
        arquivos[alg] = cabecalho + '\n' + '\n'.join([','.join(row) for row in resultado])
    
    return jsonify({
        'tempos': tempos,
        'arquivos': arquivos
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)