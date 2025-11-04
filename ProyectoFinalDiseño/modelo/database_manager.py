import sqlite3

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
        El __init__ se llama CADA VEZ que se "crea" un objeto (ej. DatabaseManager()),
        incluso cuando __new__ devuelve una instancia ya existente.
        Usamos la bandera 'initialized' para correr la conexión una sola vez.
        """
        if self.initialized:
            return  

        print("Inicializando conexión a la BD...")
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.setup_database()  # Llama a la función para crear tablas
            self.initialized = True # Marcamos como inicializado
            print("Conexión y tablas configuradas exitosamente.")
        except sqlite3.Error as e:
            print(f"Error al conectar o configurar la base de datos: {e}")

    def setup_database(self):
        """
        Crea las tablas necesarias para el proyecto si no existen.
        """
        # Tabla para el login de administradores
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        # Tabla para el catálogo de Municipios
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Municipio (
            id_municipio INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
        """)

        # Tabla principal de Citas (Tickets de Turno)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cita (
            curp_alumno TEXT PRIMARY KEY NOT NULL,
            nombre_tutor TEXT NOT NULL,
            nombre_alumno TEXT NOT NULL,
            paterno_alumno TEXT NOT NULL,
            materno_alumno TEXT NOT NULL,
            telefono_contacto TEXT,
            correo_contacto TEXT,
            nivel_educativo TEXT,
            asunto TEXT,
            estatus TEXT DEFAULT 'Pendiente',
            numero_turno INTEGER,
            id_municipio INTEGER,
            FOREIGN KEY (id_municipio) REFERENCES Municipio(id_municipio)
        )
        """)

      
        try:
            self.cursor.execute("INSERT INTO Usuario (username, password) VALUES ('admin', 'admin123')")
        except sqlite3.IntegrityError:
            pass  

        # Insertar municipios de ejemplo (catálogo)
        try:
            municipios = [('Saltillo',), ('Ramos Arizpe',), ('Arteaga',), ('Parras',)]
            self.cursor.executemany("INSERT INTO Municipio (nombre) VALUES (?)", municipios)
        except sqlite3.IntegrityError:
            pass  # Los municipios ya existen

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
        # Requerido por el proyecto
        if self.conn:
            self.conn.commit() 
            self.conn.close()
            print("Conexión a la BD cerrada.")
            # Reseteamos la instancia para futuras pruebas (opcional, pero útil)
            DatabaseManager._instance = None
            self.initialized = False