# modelo/cita_model.py
import sqlite3
import re 
from .database_manager import DatabaseManager

class Cita:
    
    # Atributos de la cita
    def __init__(self, curp_alumno, nombre_tutor, nombre_alumno, paterno_alumno, 
                 materno_alumno, id_municipio, telefono_contacto="", 
                 correo_contacto="", nivel_educativo="", asunto="", 
                 estatus="Pendiente", numero_turno=None):
        
        self.curp_alumno = curp_alumno
        self.nombre_tutor = nombre_tutor
        self.nombre_alumno = nombre_alumno
        self.paterno_alumno = paterno_alumno
        self.materno_alumno = materno_alumno
        self.id_municipio = id_municipio
        self.telefono_contacto = telefono_contacto
        self.correo_contacto = correo_contacto
        self.nivel_educativo = nivel_educativo
        self.asunto = asunto
        self.estatus = estatus
        self.numero_turno = numero_turno
        
        self.db = DatabaseManager()
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

    @staticmethod
    def validar_curp(curp):
        """
        Valida que el formato de la CURP sea correcto usando RegEx.
        Formato: PETD800714HCLRNV02
        """
        patron_curp = r"^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9]{2}$"
        
        if re.match(patron_curp, curp):
            return True
        return False

    def _get_next_turno(self):
        """
        Lógica de negocio: Obtiene el siguiente turno para el municipio
        específico de esta cita.
        """
        try:
            self.cursor.execute(
                "SELECT MAX(numero_turno) FROM Cita WHERE id_municipio = ?",
                (self.id_municipio,)
            )
            max_turno = self.cursor.fetchone()[0]
            
            if max_turno is None:
                return 1
            else:
                return max_turno + 1
        except sqlite3.Error as e:
            print(f"Error calculando el siguiente turno: {e}")
            return None

    def save(self, es_admin=False):
        """
        Guarda una nueva cita o actualiza una existente.
        """
        if not self.validar_curp(self.curp_alumno):
            print("Error: Formato de CURP inválido.")
            return False, "Error: Formato de CURP inválido."
        
        try:
            self.cursor.execute("SELECT numero_turno FROM Cita WHERE curp_alumno = ?", (self.curp_alumno,))
            existe = self.cursor.fetchone()

            if existe:
                
                self.numero_turno = existe[0]
                
                admin_fields = ", estatus = ?" if es_admin else ""
                admin_values = (self.estatus,) if es_admin else ()

                sql = f"""
                    UPDATE Cita SET
                    nombre_tutor = ?, nombre_alumno = ?, paterno_alumno = ?,
                    materno_alumno = ?, telefono_contacto = ?, correo_contacto = ?,
                    nivel_educativo = ?, asunto = ?, id_municipio = ?
                    {admin_fields}
                    WHERE curp_alumno = ?
                """
                
                valores = (self.nombre_tutor, self.nombre_alumno, self.paterno_alumno,
                           self.materno_alumno, self.telefono_contacto, self.correo_contacto,
                           self.nivel_educativo, self.asunto, self.id_municipio) + \
                           admin_values + (self.curp_alumno,)
                
                self.cursor.execute(sql, valores)
                
            else:
                
                self.numero_turno = self._get_next_turno()
                if self.numero_turno is None:
                    return False, "Error al generar el número de turno."

                sql = """
                    INSERT INTO Cita (
                        curp_alumno, nombre_tutor, nombre_alumno, paterno_alumno,
                        materno_alumno, telefono_contacto, correo_contacto,
                        nivel_educativo, asunto, estatus, numero_turno, id_municipio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                valores = (
                    self.curp_alumno, self.nombre_tutor, self.nombre_alumno,
                    self.paterno_alumno, self.materno_alumno, self.telefono_contacto,
                    self.correo_contacto, self.nivel_educativo, self.asunto,
                    self.estatus, self.numero_turno, self.id_municipio
                )
                self.cursor.execute(sql, valores)
            
            self.conn.commit()
            
            mensaje_exito = self.curp_alumno if existe else self.numero_turno
            return True, mensaje_exito

        except sqlite3.Error as e:
            print(f"Error al guardar la cita: {e}")
            self.conn.rollback()
            return False, f"Error de base de datos: {e}"

    #  Métodos para el Administrador 

    @staticmethod
    def get_by_curp_o_nombre(filtro):
        """
        Busca citas por CURP o por nombre del alumno.
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            sql = """
                SELECT * FROM Cita 
                WHERE curp_alumno LIKE ? 
                OR (nombre_alumno || ' ' || paterno_alumno || ' ' || materno_alumno) LIKE ?
            """
            param = f"%{filtro}%"
            cursor.execute(sql, (filtro, param))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error en la búsqueda: {e}")
            return []

    @staticmethod
    def delete_by_curp(curp):
        """Elimina una cita por CURP."""
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            cursor.execute("DELETE FROM Cita WHERE curp_alumno = ?", (curp,))
            db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar: {e}")
            return False

    # Métodos para el Dashboard 

    @staticmethod
    def get_stats_dashboard(id_municipio=None):
        """
        Obtiene los conteos de estatus (Pendiente, Resuelto)
        para el dashboard.
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            
            base_sql = "SELECT estatus, COUNT(*) FROM Cita"
            params = ()
            
            if id_municipio is not None:
                base_sql += " WHERE id_municipio = ?"
                params = (id_municipio,)

            base_sql += " GROUP BY estatus"
            
            cursor.execute(base_sql, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error obteniendo estadísticas: {e}")
            return [('Pendiente', 0), ('Resuelto', 0)]
    
    @staticmethod
    def actualizar_estatus(curp, nuevo_estatus):
        """
        Actualiza ÚNICAMENTE el estatus de una cita usando su CURP.
        """
        if nuevo_estatus not in ("Pendiente", "Resuelto"):
            print(f"Error: Estatus '{nuevo_estatus}' no es válido.")
            return False
            
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            
            cursor.execute(
                "UPDATE Cita SET estatus = ? WHERE curp_alumno = ?",
                (nuevo_estatus, curp)
            )
            db.get_connection().commit()
            
            return cursor.rowcount > 0 
            
        except sqlite3.Error as e:
            print(f"Error al actualizar estatus: {e}")
            db.get_connection().rollback()
            return False

    
    @staticmethod
    def get_by_curp_and_turno(curp, turno):
        """
        Busca una cita específica por CURP y Número de Turno.
        Devuelve los datos de la cita si la encuentra, o None si no.
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            
            # Hacemos que la consulta devuelva un diccionario
            cursor.row_factory = sqlite3.Row 
            
            cursor.execute(
                "SELECT * FROM Cita WHERE curp_alumno = ? AND numero_turno = ?",
                (curp, int(turno)) # Aseguramos que el turno sea un número
            )
            
            resultado = cursor.fetchone()
            
            # Restablecer el row_factory para no afectar otras consultas
            cursor.row_factory = None 
            
            if resultado:
                # Convertimos el resultado (sqlite3.Row) a un diccionario estándar
                return dict(resultado)
            else:
                return None
                
        except (sqlite3.Error, ValueError) as e: # Capturamos también si el turno no es número
            print(f"Error al buscar por CURP y Turno: {e}")
            return None