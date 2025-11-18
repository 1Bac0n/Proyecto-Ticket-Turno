# modelo/nivel_model.py
import sqlite3
from .database_manager import DatabaseManager

class Nivel:
    
    def __init__(self, id_nivel=None, nombre=None):
        self.id_nivel = id_nivel
        self.nombre = nombre
        self.db = DatabaseManager() # Singleton
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

    def save(self):
        """
        Guarda un nuevo nivel o actualiza uno existente.
        """
        try:
            if self.id_nivel is None:
                # --- Crear (Create) ---
                self.cursor.execute(
                    "INSERT INTO Nivel (nombre) VALUES (?)",
                    (self.nombre,)
                )
                self.id_nivel = self.cursor.lastrowid
            else:
                # --- Actualizar (Update) ---
                self.cursor.execute(
                    "UPDATE Nivel SET nombre = ? WHERE id_nivel = ?",
                    (self.nombre, self.id_nivel)
                )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error guardando nivel: {e}")
            return False

    def delete(self):
        """
        Borra un nivel de la base de datos.
        """
        if self.id_nivel:
            try:
                # --- Borrar (Delete) ---
                self.cursor.execute(
                    "DELETE FROM Nivel WHERE id_nivel = ?",
                    (self.id_nivel,)
                )
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error borrando nivel: {e}")
                return False
        return False

    @staticmethod
    def get_all():
        """
        Obtiene todos los niveles. 
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            # --- Leer (Read) ---
            cursor.execute("SELECT id_nivel, nombre FROM Nivel ORDER BY nombre")
            return cursor.fetchall() 
        except sqlite3.Error as e:
            print(f"Error obteniendo todos los niveles: {e}")
            return []

    @staticmethod
    def get_by_id(id_nivel):
        """Busca un nivel por su ID."""
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            cursor.execute("SELECT id_nivel, nombre FROM Nivel WHERE id_nivel = ?", (id_nivel,))
            row = cursor.fetchone()
            if row:
                return Nivel(id_nivel=row[0], nombre=row[1])
            return None
        except sqlite3.Error as e:
            print(f"Error obteniendo nivel por ID: {e}")
            return None