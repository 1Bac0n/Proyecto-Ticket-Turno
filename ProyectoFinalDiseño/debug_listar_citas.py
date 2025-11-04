from modelo.database_manager import DatabaseManager

if __name__ == '__main__':
    db = DatabaseManager()
    cursor = db.get_cursor()

    curp = input("CURP a buscar: ").strip().upper()
    cursor.execute("SELECT curp_alumno, numero_turno, nombre_tutor, nombre_alumno, paterno_alumno, id_municipio, estatus FROM Cita WHERE curp_alumno = ?", (curp,))
    filas = cursor.fetchall()
    print(f"Encontradas {len(filas)} filas para {curp}:")
    for f in filas:
        print(f)
