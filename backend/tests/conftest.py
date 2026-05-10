import sys
import os

# Adiciona backend/src ao path para que os testes possam importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
