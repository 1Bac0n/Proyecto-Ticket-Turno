# modelo/tipotramite_model.py
import sqlite3
from .database_manager import DatabaseManager

class TipoTramite:
    
    def __init__(self, id_tipotramite=None, nombre=None):
        self.id_tipotramite = id_tipotramite
        self.nombre = nombre
        self.db = DatabaseManager() # Singleton
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

    def save(self):
        """
        Guarda un nuevo tipo de trámite o actualiza uno existente.
        """
        try:
            if self.id_tipotramite is None:
                # --- Crear (Create) ---
                self.cursor.execute(
                    "INSERT INTO TipoTramite (nombre) VALUES (?)",
                    (self.nombre,)
                )
                self.id_tipotramite = self.cursor.lastrowid
            else:
                # --- Actualizar (Update) ---
                self.cursor.execute(
                    "UPDATE TipoTramite SET nombre = ? WHERE id_tipotramite = ?",
                    (self.nombre, self.id_tipotramite)
                )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error guardando tipo de trámite: {e}")
            return False

    def delete(self):
        """
        Borra un tipo de trámite de la base de datos.
        """
        if self.id_tipotramite:
            try:
                # --- Borrar (Delete) ---
                self.cursor.execute(
                    "DELETE FROM TipoTramite WHERE id_tipotramite = ?",
                    (self.id_tipotramite,)
                )
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error borrando tipo de trámite: {e}")
                return False
        return False

    @staticmethod
    def get_all():
        """
        Obtiene todos los tipos de trámite. 
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            # --- Leer (Read) ---
            cursor.execute("SELECT id_tipotramite, nombre FROM TipoTramite ORDER BY nombre")
            return cursor.fetchall() 
        except sqlite3.Error as e:
            print(f"Error obteniendo todos los tipos de trámite: {e}")
            return []

    @staticmethod
    def get_by_id(id_tipotramite):
        """Busca un tipo de trámite por su ID."""
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            cursor.execute("SELECT id_tipotramite, nombre FROM TipoTramite WHERE id_tipotramite = ?", (id_tipotramite,))
            row = cursor.fetchone()
            if row:
                return TipoTramite(id_tipotramite=row[0], nombre=row[1])
            return None
        except sqlite3.Error as e:
            print(f"Error obteniendo tipo de trámite por ID: {e}")
            return None