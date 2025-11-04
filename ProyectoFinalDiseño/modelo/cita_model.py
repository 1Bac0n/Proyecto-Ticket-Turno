# modelo/cita_model.py
import re # Importamos 're' para Expresiones Regulares
import sqlite3 # <--- AÑADIDO
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
        # 4 letras, 6 números, 1 (H/M), 5 letras, 2 (letra o número)
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
            max_turno = self.cursor.fetchone()[0] # [0] para obtener el valor
            
            if max_turno is None:
                return 1 # Es el primer turno de este municipio
            else:
                return max_turno + 1
        except sqlite3.Error as e: # <--- CORREGIDO
            print(f"Error calculando el siguiente turno: {e}")
            return None # Indicar un error

    def save(self, es_admin=False):
        """
        Guarda una nueva cita o actualiza una existente.
        """
        # --- 1. Validación de CURP ---
        if not self.validar_curp(self.curp_alumno):
            # [cite_start]No pasa la validación, avisamos y no guardamos [cite: 31]
            print("Error: Formato de CURP inválido.")
            return False, "Error: Formato de CURP inválido."
        
        try:
            # --- 2. Revisar si la CURP ya existe (es PK) ---
            self.cursor.execute("SELECT numero_turno FROM Cita WHERE curp_alumno = ?", (self.curp_alumno,))
            existe = self.cursor.fetchone()

            if existe:
                # --- ACTUALIZAR (Update) ---
                # [cite_start]La lógica de modificación [cite: 23, 25]
                # Si es admin, puede cambiar estatus. Si es público, solo sus datos.
                # El número de turno NUNCA se cambia.
                self.numero_turno = existe[0] # Reasignamos el turno que ya tenía
                
                # Campos que el admin SÍ puede cambiar
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
                # --- CREAR (Create) ---
                # [cite_start]3. Lógica de asignación de turno [cite: 28]
                self.numero_turno = self._get_next_turno()
                if self.numero_turno is None:
                    return False, "Error al generar el número de turno."

                # 4. Insertar
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
            # [cite_start]Devolvemos el turno asignado para el comprobante [cite: 24]
            return True, self.numero_turno 

        except sqlite3.Error as e: # <--- CORREGIDO
            print(f"Error al guardar la cita: {e}")
            self.conn.rollback() # Revertir cambios si hay error
            return False, f"Error de base de datos: {e}"

    # [cite_start]--- Métodos para el Administrador --- [cite: 25]

    @staticmethod
    def get_by_curp_o_nombre(filtro):
        """
        Busca citas por CURP o por nombre del alumno.
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            # Busca si el filtro es CURP o parte del nombre completo
            sql = """
                SELECT * FROM Cita 
                WHERE curp_alumno LIKE ? 
                OR (nombre_alumno || ' ' || paterno_alumno || ' ' || materno_alumno) LIKE ?
            """
            # Usamos '%' para búsquedas parciales en el nombre
            param = f"%{filtro}%"
            cursor.execute(sql, (filtro, param))
            return cursor.fetchall()
        except sqlite3.Error as e: # <--- CORREGIDO
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
            return cursor.rowcount > 0 # Devuelve True si se borró algo
        except sqlite3.Error as e: # <--- CORREGIDO
            print(f"Error al eliminar: {e}")
            return False

    # [cite_start]--- Métodos para el Dashboard --- [cite: 29]

    @staticmethod
    def get_stats_dashboard(id_municipio=None):
        """
        Obtiene los conteos de estatus (Pendiente, Resuelto)
        para el dashboard. Si id_municipio es None, obtiene el total.
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
            # Devuelve datos listos para la gráfica, ej: [('Pendiente', 5), ('Resuelto', 2)]
            return cursor.fetchall()
        except sqlite3.Error as e: # <--- CORREGIDO
            print(f"Error obteniendo estadísticas: {e}")
            return [('Pendiente', 0), ('Resuelto', 0)] # Devolver datos vacíos