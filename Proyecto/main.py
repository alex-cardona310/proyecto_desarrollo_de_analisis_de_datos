import sys
import os

# 1. Encontramos la carpeta "Proyecto"
actual_dir = os.path.dirname(os.path.abspath(__file__))
if actual_dir not in sys.path:
    sys.path.insert(0, actual_dir)

# 2. Encontramos y forzamos la carpeta "app" en el buscador de Python3
app_dir = os.path.join(actual_dir, "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Importamos usando la raíz de la carpeta app
from app.Dataapp import DataApp

if __name__ == "__main__":
    app = DataApp()
    app.run()