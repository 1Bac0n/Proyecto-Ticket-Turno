# modelo/usuario_model.py
import sqlite3
from .database_manager import DatabaseManager

class Usuario:
    
    def __init__(self, username=None, password=None, id_usuario=None):
        self.id_usuario = id_usuario
        self.username = username
        self.password = password
    
    @staticmethod
    def verificar_credenciales(username, password):
        """
        Verifica si el usuario y contraseña son correctos.
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            
            # ATENCIÓN: En un proyecto real, la contraseña NUNCA se guarda en texto plano.
            # Se usaría un hash (ej. bcrypt). Por simplicidad del proyecto, lo hacemos así.
            cursor.execute(
                "SELECT id_usuario FROM Usuario WHERE username = ? AND password = ?",
                (username, password)
            )
            
            resultado = cursor.fetchone()
            
            if resultado:
                # Las credenciales son correctas
                return True
            else:
                # Credenciales incorrectas
                return False
        
        # --- ESTA ES LA LÍNEA CORREGIDA ---
        except sqlite3.Error as e:
            print(f"Error verificando credenciales: {e}")
            return False