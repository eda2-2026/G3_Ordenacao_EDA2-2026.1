from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import time
import logging

# Adicionar path do backend original
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src'))

from algoritmos import merge_sort, quick_sort, heap_sort
from csv_io import criar_chave

app = Flask(__name__)
CORS(app)

# Desabilitar logs do Werkzeug em modo debug
logging.getLogger('werkzeug').setLevel(logging.ERROR)

@app.route('/api/sort', methods=['POST'])
def sort_csv():
    """Endpoint para processar ordenação de CSV."""
    try:
        data = request.json
        
        # Validação de dados de entrada
        if not data:
            return jsonify({'error': 'Nenhum dado enviado'}), 400
        
        csv_text = data.get('csv', '')
        coluna = data.get('coluna')
        tipo = data.get('tipo', 'str')
        reverso = data.get('reverso', False)
        algoritmos = data.get('algoritmos', [])
        
        if not csv_text:
            return jsonify({'error': 'CSV vazio'}), 400
        if not algoritmos:
            return jsonify({'error': 'Nenhum algoritmo selecionado'}), 400
        if coluna is None:
            return jsonify({'error': 'Coluna não especificada'}), 400
        
        # Parse CSV
        linhas = csv_text.strip().split('\n')
        if not linhas:
            return jsonify({'error': 'Arquivo CSV inválido'}), 400
            
        cabecalho = linhas[0]
        dados = [linha.split(',') for linha in linhas[1:] if linha.strip()]
        
        if not dados:
            return jsonify({'error': 'Nenhuma linha de dados no CSV'}), 400
        
        # Validar índice da coluna
        num_colunas = len(dados[0])
        if coluna < 0 or coluna >= num_colunas:
            return jsonify({'error': f'Coluna {coluna} inválida. CSV possui {num_colunas} colunas (índices 0-{num_colunas-1})'}), 400
        
        # Criar função chave
        try:
            chave = criar_chave(coluna, tipo=tipo)
        except ValueError as e:
            return jsonify({'error': f'Erro ao criar chave: {str(e)}'}), 400
        
        # Executar algoritmos
        tempos = {}
        arquivos = {}
        
        for alg in algoritmos:
            if alg not in ['merge', 'quick', 'heap']:
                continue
                
            dados_copia = [linha[:] for linha in dados]
            
            try:
                import time as time_module
                inicio = time_module.perf_counter()
                
                if alg == 'merge':
                    resultado = merge_sort(dados_copia, chave=chave, reverso=reverso)
                elif alg == 'quick':
                    resultado = quick_sort(dados_copia, chave=chave, reverso=reverso)
                elif alg == 'heap':
                    resultado = heap_sort(dados_copia, chave=chave, reverso=reverso)
                
                fim = time_module.perf_counter()
                tempos[alg] = fim - inicio
                arquivos[alg] = cabecalho + '\n' + '\n'.join([','.join(row) for row in resultado])
            except Exception as e:
                return jsonify({'error': f'Erro ao executar {alg}: {str(e)}'}), 500
        
        return jsonify({
            'tempos': tempos,
            'arquivos': arquivos
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000, use_reloader=False)