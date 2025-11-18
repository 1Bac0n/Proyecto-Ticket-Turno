import sqlite3
import os

class DatabaseManager:
    _instance = None  # Atributo de clase para guardar la instancia única

    def __new__(cls, *args, **kwargs):
        """
        El método __new__ se llama ANTES que __init__.
        Aquí controlamos la creación de la instancia.
        """
        if cls._instance is None:
            print("Creando NUEVA instancia del DatabaseManager.")
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.initialized = False
        else:
            print("Usando instancia EXISTENTE del DatabaseManager.")
        
        return cls._instance

    def __init__(self, db_name="citas.db"):
        """
        El __init__ se llama CADA VEZ que se "crea" un objeto...
        """
        if self.initialized:
            return  # Si ya está inicializado, no hacer nada.

        # Lógica para encontrar la ruta correcta del archivo .db
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        db_path = os.path.join(project_root, db_name)
        # -----------------------------------------------------------

        print(f"Inicializando conexión a la BD en: {db_path}") 
        try:
            self.conn = sqlite3.connect(db_path) 
            self.cursor = self.conn.cursor()
            self.setup_database() # Llama a la función para crear tablas
            self.initialized = True
            print("Conexión y tablas configuradas exitosamente.")
        except sqlite3.Error as e:
            print(f"Error al conectar o configurar la base de datos: {e}")

    def setup_database(self):
        """
        Crea las tablas necesarias para el proyecto si no existen.
        """
        # 1. Tabla Usuario
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        # 2. Catálogo Municipio
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Municipio (
            id_municipio INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
        """)
        
       
        # 3. Catálogo Nivel
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Nivel (
            id_nivel INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
        """)
        
        # 4. Catálogo TipoTramite
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS TipoTramite (
            id_tipotramite INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
        """)
        # --- FIN DE NUEVAS TABLAS ---

        # 5. Tabla principal de Citas 
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cita (
            curp_alumno TEXT PRIMARY KEY NOT NULL,
            nombre_tutor TEXT NOT NULL,
            nombre_alumno TEXT NOT NULL,
            paterno_alumno TEXT NOT NULL,
            materno_alumno TEXT NOT NULL,
            telefono_contacto TEXT,
            correo_contacto TEXT,
            asunto TEXT,
            estatus TEXT DEFAULT 'Pendiente',
            numero_turno INTEGER,
            
            -- Llaves Foráneas (FKs) --
            id_municipio INTEGER,
            id_nivel INTEGER, 
            id_tipotramite INTEGER, 
            
            FOREIGN KEY (id_municipio) REFERENCES Municipio(id_municipio),
            FOREIGN KEY (id_nivel) REFERENCES Nivel(id_nivel),
            FOREIGN KEY (id_tipotramite) REFERENCES TipoTramite(id_tipotramite)
        )
        """)

        # --- Insertar datos de ejemplo ---
        try:
            self.cursor.execute("INSERT INTO Usuario (username, password) VALUES ('admin', 'admin123')")
        except sqlite3.IntegrityError:
            pass  

        try:
            municipios = [('Saltillo',), ('Ramos Arizpe',), ('Arteaga',), ('Parras',)]
            self.cursor.executemany("INSERT INTO Municipio (nombre) VALUES (?)", municipios)
        except sqlite3.IntegrityError:
            pass 
            
        # --- ¡NUEVOS DATOS DE EJEMPLO! ---
        try:
            niveles = [('Preescolar',), ('Primaria',), ('Secundaria',), ('Preparatoria',), ('Universidad',)]
            self.cursor.executemany("INSERT INTO Nivel (nombre) VALUES (?)", niveles)
        except sqlite3.IntegrityError:
            pass

        try:
            tramites = [('Inscripción',), ('Constancia de Estudios',), ('Trámite de Beca',), ('Baja Temporal',)]
            self.cursor.executemany("INSERT INTO TipoTramite (nombre) VALUES (?)", tramites)
        except sqlite3.IntegrityError:
            pass
        # --- FIN DE NUEVOS DATOS ---

        self.conn.commit()
        print("Tablas verificadas y datos de ejemplo insertados.")

    def get_cursor(self):
        """Devuelve el cursor para hacer consultas."""
        return self.cursor

    def get_connection(self):
        """Devuelve la conexión para hacer commits o rollbacks."""
        return self.conn

    def close_connection(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.commit() 
            self.conn.close()
            print("Conexión a la BD cerrada.")
            DatabaseManager._instance = None
            self.initialized = False