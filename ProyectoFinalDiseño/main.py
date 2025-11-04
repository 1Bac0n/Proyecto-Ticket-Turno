# main.py
import sys
import os

# --- Esto es un truco para que Python encuentre tus carpetas ---
# Añade la carpeta principal del proyecto a la ruta de búsqueda
# para que podamos importar 'modelo', 'vista', etc.
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
# -------------------------------------------------------------

from vista.vista_login import VistaLogin
from modelo.usuario_model import Usuario
from controlador.controlador_login import ControladorLogin
from modelo.database_manager import DatabaseManager # Importante

class Aplicacion:
    def __init__(self):
        # 1. Creamos la conexión a la BD (Singleton)
        self.db_manager = DatabaseManager()

        # 2. Creamos el Modelo (solo necesitamos la clase estática)
        self.usuario_modelo = Usuario

        # 3. Creamos la Vista
        self.vista_login = VistaLogin()

        # 4. Creamos el Controlador y le pasamos la Vista y el Modelo
        self.controlador_login = ControladorLogin(self.vista_login, self.usuario_modelo)

    def run(self):
        # 5. Iniciamos el bucle principal de la aplicación (mostramos la ventana)
        self.vista_login.mainloop()
        
        # 6. Cuando la app termine, cerramos la BD
        print("Cerrando la aplicación...")
        self.db_manager.close_connection()

# --- Punto de entrada de la aplicación ---
if __name__ == "__main__":
    app = Aplicacion()
    app.run()