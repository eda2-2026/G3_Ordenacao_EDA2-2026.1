from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import time
import logging
import csv
import io

# Adicionar path do backend original
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src'))

from algoritmos import merge_sort, quick_sort, heap_sort
from csv_io import criar_chave, criar_conversor, obter_indice_coluna

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
        
        try:
            leitor = csv.reader(io.StringIO(csv_text), delimiter=',')
            linhas = [linha for linha in leitor]
        except Exception as e:
            return jsonify({'error': f'Erro ao ler CSV: {str(e)}'}), 400

        if not linhas:
            return jsonify({'error': 'Arquivo CSV inválido'}), 400

        cabecalho = linhas[0]
        dados = [linha for linha in linhas[1:] if linha]
        
        if not dados:
            return jsonify({'error': 'Nenhuma linha de dados no CSV'}), 400
        
        try:
            if isinstance(coluna, str) and not coluna.isdigit():
                coluna = obter_indice_coluna(cabecalho, coluna)
            else:
                coluna = int(coluna)
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Coluna inválida: {str(e)}'}), 400

        # Validar índice da coluna
        num_colunas = len(cabecalho)
        if coluna < 0 or coluna >= num_colunas:
            return jsonify({'error': f'Coluna {coluna} inválida. CSV possui {num_colunas} colunas (índices 0-{num_colunas-1})'}), 400

        for i, linha in enumerate(dados):
            if len(linha) != num_colunas:
                return jsonify({'error': f'Linha {i + 2} possui {len(linha)} colunas; esperado {num_colunas}.'}), 400
        
        try:
            conversor = criar_conversor(tipo)
            chave = criar_chave(coluna, tipo=tipo)
        except ValueError as e:
            return jsonify({'error': f'Erro ao criar chave: {str(e)}'}), 400

        erros = 0
        for i, linha in enumerate(dados[:5]):
            try:
                conversor(linha[coluna])
            except Exception:
                erros += 1
                return jsonify({'error': f'Falha ao converter valor na linha {i + 2}.'}), 400
        
        # Executar algoritmos
        tempos = {}
        arquivos = {}
        
        for alg in algoritmos:
            if alg not in ['merge', 'quick', 'heap']:
                continue
                
            dados_copia = [linha[:] for linha in dados]
            
            try:
                inicio = time.perf_counter()
                
                if alg == 'merge':
                    resultado = merge_sort(dados_copia, chave=chave, reverso=reverso)
                elif alg == 'quick':
                    resultado = quick_sort(dados_copia, chave=chave, reverso=reverso)
                elif alg == 'heap':
                    resultado = heap_sort(dados_copia, chave=chave, reverso=reverso)
                
                fim = time.perf_counter()
                tempos[alg] = fim - inicio
                buffer = io.StringIO()
                escritor = csv.writer(buffer, delimiter=',', lineterminator='\n')
                escritor.writerow(cabecalho)
                escritor.writerows(resultado)
                arquivos[alg] = buffer.getvalue().rstrip('\n')
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