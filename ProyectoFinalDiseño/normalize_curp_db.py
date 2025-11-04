import shutil
import os
import time
from modelo.database_manager import DatabaseManager

BACKUP_SUFFIX = ".bak"


def backup_db(conn):
    # Usar PRAGMA database_list para obtener la ruta de archivo exacta
    cur = conn.cursor()
    cur.execute("PRAGMA database_list;")
    rows = cur.fetchall()
    if not rows:
        print("No se encontró la ruta del archivo de la base de datos.")
        return None, None
    # La primera entrada normalmente es la principal
    db_file = rows[0][2]
    if not db_file:
        print("La base de datos parece estar en memoria o la ruta no está disponible.")
        return None, None

    timestamp = time.strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_file}{BACKUP_SUFFIX}.{timestamp}"
    shutil.copy2(db_file, backup_path)
    print(f"Backup creado en: {backup_path}")
    return db_file, backup_path


if __name__ == '__main__':
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = db.get_cursor()

    print("Creando backup de la base de datos antes de normalizar CURP...")
    db_file, backup = backup_db(conn)
    if backup is None:
        print("No se creó backup. Abortando para evitar riesgo de corrupción.")
        exit(1)

    # Contar cambios antes
    before_changes = conn.total_changes

    try:
        # Actualizar CURP: trim, upper y remover espacios internos
        # REPLACE(UPPER(TRIM(curp_alumno)), ' ', '') -> quita espacios y normaliza
        cursor.execute(\
            """
            UPDATE Cita SET curp_alumno = REPLACE(UPPER(TRIM(curp_alumno)), ' ', '')
            WHERE curp_alumno IS NOT NULL
            """
        )
        conn.commit()

        after_changes = conn.total_changes
        modified = after_changes - before_changes
        print(f"Normalización completada. Filas modificadas (aprox): {modified}")
        print("Si hubo errores de integridad, restaura el backup manualmente:")
        print(f"  copia {backup} sobre el archivo de BD actual (asegúrate de cerrar la app antes)")

    except Exception as e:
        print(f"Error al normalizar CURP: {e}")
        print("Restaurando backup...")
        if backup and os.path.exists(backup) and db_file:
            # Intentar restaurar
            shutil.copy2(backup, db_file)
            print("Backup restaurado.")
        else:
            print("No se encontró backup para restaurar. Revisa manualmente.")
        raise
