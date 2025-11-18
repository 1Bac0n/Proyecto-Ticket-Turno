# modelo/cita_model.py
import sqlite3
import re 
from .database_manager import DatabaseManager

class Cita:
    
    # Atributos de la cita
    def __init__(self, curp_alumno, nombre_tutor, nombre_alumno, paterno_alumno, 
                 materno_alumno, id_municipio, id_nivel, id_tipotramite, asunto="",
                 telefono_contacto="", correo_contacto="", 
                 estatus="Pendiente", numero_turno=None):
        
        self.curp_alumno = curp_alumno
        self.nombre_tutor = nombre_tutor
        self.nombre_alumno = nombre_alumno
        self.paterno_alumno = paterno_alumno
        self.materno_alumno = materno_alumno
        self.telefono_contacto = telefono_contacto
        self.correo_contacto = correo_contacto
        self.asunto = asunto
        self.estatus = estatus
        self.numero_turno = numero_turno
        self.id_municipio = id_municipio
        self.id_nivel = id_nivel
        self.id_tipotramite = id_tipotramite
        
        self.db = DatabaseManager()
        self.conn = self.db.get_connection()
        self.cursor = self.db.get_cursor()

    @staticmethod
    def validar_curp(curp):
        patron_curp = r"^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9]{2}$"
        if re.match(patron_curp, curp):
            return True
        return False

    def _get_next_turno(self):
        try:
            self.cursor.execute(
                "SELECT MAX(numero_turno) FROM Cita WHERE id_municipio = ?",
                (self.id_municipio,)
            )
            max_turno = self.cursor.fetchone()[0]
            return (max_turno or 0) + 1
        except sqlite3.Error as e:
            print(f"Error calculando el siguiente turno: {e}")
            return None

    def save(self, es_admin=False):
        """
        Guarda una nueva cita o actualiza una existente.
        """
        if not self.validar_curp(self.curp_alumno):
            return False, "Error: Formato de CURP inválido."
        
        try:
            self.cursor.row_factory = None
            self.cursor.execute("SELECT numero_turno, estatus FROM Cita WHERE curp_alumno = ?", (self.curp_alumno,))
            existe_tupla = self.cursor.fetchone()

            if existe_tupla:
                # --- ACTUALIZAR (Update) ---
                self.numero_turno = existe_tupla[0]
                estatus_final = self.estatus if es_admin else "Pendiente"
                admin_fields = ", estatus = ?" if es_admin else ""
                admin_values = (estatus_final,) if es_admin else ()

                sql = f"""
                    UPDATE Cita SET
                    nombre_tutor = ?, nombre_alumno = ?, paterno_alumno = ?,
                    materno_alumno = ?, telefono_contacto = ?, correo_contacto = ?,
                    asunto = ?, id_municipio = ?, id_nivel = ?, id_tipotramite = ?
                    {admin_fields}
                    WHERE curp_alumno = ?
                """
                valores = (self.nombre_tutor, self.nombre_alumno, self.paterno_alumno,
                           self.materno_alumno, self.telefono_contacto, self.correo_contacto,
                           self.asunto, self.id_municipio, self.id_nivel, self.id_tipotramite) + \
                           admin_values + (self.curp_alumno,)
                
                self.cursor.execute(sql, valores)
                
            else:
                # --- CREAR (Create) ---
                self.numero_turno = self._get_next_turno()
                if self.numero_turno is None:
                    return False, "Error al generar el número de turno."

                sql = """
                    INSERT INTO Cita (
                        curp_alumno, nombre_tutor, nombre_alumno, paterno_alumno,
                        materno_alumno, telefono_contacto, correo_contacto,
                        asunto, estatus, numero_turno, 
                        id_municipio, id_nivel, id_tipotramite
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                valores = (
                    self.curp_alumno, self.nombre_tutor, self.nombre_alumno,
                    self.paterno_alumno, self.materno_alumno, self.telefono_contacto,
                    self.correo_contacto, self.asunto, "Pendiente", self.numero_turno, 
                    self.id_municipio, self.id_nivel, self.id_tipotramite
                )
                self.cursor.execute(sql, valores)
            
            self.conn.commit()
            return True, self.numero_turno

        except sqlite3.Error as e:
            print(f"Error al guardar la cita: {e}")
            self.conn.rollback()
            return False, f"Error de base de datos: {e}"

    # --- Métodos para el Administrador ---
    @staticmethod
    def get_by_curp_o_nombre(filtro):
        """
        Busca citas por CURP o por nombre del alumno,
        trayendo los NOMBRES de los catálogos en lugar de los IDs.
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            
            sql = """
                SELECT
                    c.curp_alumno, 
                    c.nombre_alumno, 
                    c.paterno_alumno, 
                    c.materno_alumno,
                    c.numero_turno, 
                    c.estatus,
                    m.nombre AS municipio_nombre,
                    n.nombre AS nivel_nombre,
                    t.nombre AS tramite_nombre
                FROM Cita c
                LEFT JOIN Municipio m ON c.id_municipio = m.id_municipio
                LEFT JOIN Nivel n ON c.id_nivel = n.id_nivel
                LEFT JOIN TipoTramite t ON c.id_tipotramite = t.id_tipotramite
                WHERE c.curp_alumno LIKE ? 
                OR (c.nombre_alumno || ' ' || c.paterno_alumno || ' ' || c.materno_alumno) LIKE ?
            """
            param = f"%{filtro}%"
            cursor.execute(sql, (filtro, param))
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Error en la búsqueda (JOIN): {e}")
            return []

    @staticmethod
    def delete_by_curp(curp):
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            cursor.execute("DELETE FROM Cita WHERE curp_alumno = ?", (curp,))
            db.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar: {e}")
            return False

    # --- Métodos para el Dashboard ---
    
    # --- ¡¡ESTA FUNCIÓN ESTÁ ACTUALIZADA!! ---
    @staticmethod
    def get_stats_dashboard(id_municipio=None, id_nivel=None, id_tipotramite=None):
        """
        Obtiene los conteos de estatus (Pendiente, Resuelto)
        para el dashboard, AHORA CON 3 FILTROS OPCIONALES.
        """
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            
            base_sql = "SELECT estatus, COUNT(*) FROM Cita"
            params = []
            where_clauses = []
            
            # Construcción dinámica de la consulta WHERE
            if id_municipio is not None:
                where_clauses.append("id_municipio = ?")
                params.append(id_municipio)
                
            if id_nivel is not None:
                where_clauses.append("id_nivel = ?")
                params.append(id_nivel)
                
            if id_tipotramite is not None:
                where_clauses.append("id_tipotramite = ?")
                params.append(id_tipotramite)

            # Si hay filtros, los unimos con "AND"
            if where_clauses:
                base_sql += " WHERE " + " AND ".join(where_clauses)
            
            base_sql += " GROUP BY estatus"
            
            cursor.execute(base_sql, tuple(params)) # Convertimos la lista a tupla
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Error obteniendo estadísticas: {e}")
            return [('Pendiente', 0), ('Resuelto', 0)]
    
    @staticmethod
    def actualizar_estatus(curp, nuevo_estatus):
        if nuevo_estatus not in ("Pendiente", "Resuelto"):
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
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            cursor.row_factory = sqlite3.Row 
            cursor.execute(
                "SELECT * FROM Cita WHERE curp_alumno = ? AND numero_turno = ?",
                (curp, int(turno))
            )
            resultado = cursor.fetchone()
            cursor.row_factory = None 
            if resultado:
                return dict(resultado)
            else:
                return None
        except (sqlite3.Error, ValueError) as e:
            print(f"Error al buscar por CURP y Turno: {e}")
            return None

    @staticmethod
    def check_pending(curp):
        try:
            db = DatabaseManager()
            cursor = db.get_cursor()
            cursor.row_factory = None
            cursor.execute(
                "SELECT 1 FROM Cita WHERE curp_alumno = ? AND estatus = 'Pendiente'",
                (curp,)
            )
            resultado = cursor.fetchone()
            return bool(resultado) 
        except sqlite3.Error as e:
            print(f"Error en check_pending: {e}")
            return False