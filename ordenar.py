import sys
import os

# Adiciona backend/src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from main import main



if __name__ == "__main__":
    main()