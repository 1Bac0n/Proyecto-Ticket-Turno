# modelo/municipio_model.py
import sqlite3 # <--- AÑADIDO
from .database_manager import DatabaseManager

class Municipio:
    
    def __init__(self, id_municipio=None, nombre=None):
        self.id_municipio = id_municipio
        self.nombre = nombre
        self.db = DatabaseManager() # Obtenemos la instancia Singleton
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

    def save(self):
        """
        Guarda un nuevo municipio o actualiza uno existente.
        """
        try:
            if self.id_municipio is None:
                # --- Crear (Create) ---
                self.cursor.execute(
                    "INSERT INTO Municipio (nombre) VALUES (?)",
                    (self.nombre,)
                )
                self.id_municipio = self.cursor.lastrowid # Obtenemos el ID generado
            else:
                # --- Actualizar (Update) ---
                self.cursor.execute(
                    "UPDATE Municipio SET nombre = ? WHERE id_municipio = ?",
                    (self.nombre, self.id_municipio)
                )
            self.conn.commit()
            return True
        except sqlite3.Error as e: # <--- CORREGIDO
            print(f"Error guardando municipio: {e}")
            return False

    def delete(self):
        """
        Borra un municipio de la base de datos.
        """
        if self.id_municipio:
            try:
                # --- Borrar (Delete) ---
                self.cursor.execute(
                    "DELETE FROM Municipio WHERE id_municipio = ?",
                    (self.id_municipio,)
                )
                self.conn.commit()
                return True
            except sqlite3.Error as e: # <--- CORREGIDO
                print(f"Error borrando municipio: {e}")
                return False
        return False

    @staticmethod
    def get_all():
        """
        Obtiene todos los municipios. 
        Lo hacemos 'static' para poder llamarlo sin crear un objeto Municipio.
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            # --- Leer (Read) ---
            cursor.execute("SELECT id_municipio, nombre FROM Municipio ORDER BY nombre")
            # Devolvemos una lista de tuplas (id, nombre)
            return cursor.fetchall() 
        except sqlite3.Error as e: # <--- CORREGIDO
            print(f"Error obteniendo todos los municipios: {e}")
            return []

    @staticmethod
    def get_by_id(id_municipio):
        """Busca un municipio por su ID."""
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            cursor.execute("SELECT id_municipio, nombre FROM Municipio WHERE id_municipio = ?", (id_municipio,))
            row = cursor.fetchone()
            if row:
                return Municipio(id_municipio=row[0], nombre=row[1])
            return None
        except sqlite3.Error as e: # <--- CORREGIDO
            print(f"Error obteniendo municipio por ID: {e}")
            return None