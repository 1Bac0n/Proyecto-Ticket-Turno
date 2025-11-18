# vista/vista_publica.py
import customtkinter as ctk

class VistaPublica(ctk.CTkToplevel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Registro de Citas")
        self.geometry("600x750")
        self.resizable(False, False)
        
        # Hacemos que esta ventana se quede por encima de la principal
        self.transient(parent)
        self.grab_set()

        # --- Sistema de Pestañas ---
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabs.add("Registrar Cita")
        self.tabs.add("Consultar / Modificar Cita")

        # ======================================================
        # --- Pestaña 1: Registrar Cita (EL FORMULARIO COMPLETO VA AQUÍ) ---
        # ======================================================
        tab_registrar = self.tabs.tab("Registrar Cita")
        
        scroll_frame = ctk.CTkScrollableFrame(tab_registrar)
        scroll_frame.pack(fill="both", expand=True)

        # --- Datos del Alumno ---
        lbl_frame_alumno = ctk.CTkLabel(scroll_frame, text="Datos del Alumno", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_frame_alumno.pack(pady=(10, 5), fill="x", padx=10)
        
        # CURP
        ctk.CTkLabel(scroll_frame, text="CURP del Alumno:*").pack(anchor="w", padx=20)
        self.entry_curp = ctk.CTkEntry(scroll_frame, placeholder_text="PETD800714HCLRNV02")
        self.entry_curp.pack(fill="x", padx=20, pady=(0, 10))

        # Nombre Alumno
        ctk.CTkLabel(scroll_frame, text="Nombre(s) del Alumno:*").pack(anchor="w", padx=20)
        self.entry_nombre_alumno = ctk.CTkEntry(scroll_frame)
        self.entry_nombre_alumno.pack(fill="x", padx=20, pady=(0, 10))
        
        # Apellido Paterno
        ctk.CTkLabel(scroll_frame, text="Apellido Paterno Alumno:*").pack(anchor="w", padx=20)
        self.entry_paterno_alumno = ctk.CTkEntry(scroll_frame)
        self.entry_paterno_alumno.pack(fill="x", padx=20, pady=(0, 10))
        
        # Apellido Materno
        ctk.CTkLabel(scroll_frame, text="Apellido Materno Alumno:").pack(anchor="w", padx=20)
        self.entry_materno_alumno = ctk.CTkEntry(scroll_frame)
        self.entry_materno_alumno.pack(fill="x", padx=20, pady=(0, 10))

        # --- Datos del Tutor (Contacto) ---
        lbl_frame_tutor = ctk.CTkLabel(scroll_frame, text="Datos del Tutor (Contacto)", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_frame_tutor.pack(pady=(10, 5), fill="x", padx=10)

        # Nombre Tutor
        ctk.CTkLabel(scroll_frame, text="Nombre Completo del Tutor:*").pack(anchor="w", padx=20)
        self.entry_nombre_tutor = ctk.CTkEntry(scroll_frame)
        self.entry_nombre_tutor.pack(fill="x", padx=20, pady=(0, 10))

        # Teléfono
        ctk.CTkLabel(scroll_frame, text="Teléfono de Contacto:").pack(anchor="w", padx=20)
        self.entry_telefono = ctk.CTkEntry(scroll_frame)
        self.entry_telefono.pack(fill="x", padx=20, pady=(0, 10))

        # Correo
        ctk.CTkLabel(scroll_frame, text="Correo de Contacto:").pack(anchor="w", padx=20)
        self.entry_correo = ctk.CTkEntry(scroll_frame)
        self.entry_correo.pack(fill="x", padx=20, pady=(0, 10))

        # --- Datos del Trámite ---
        lbl_frame_tramite = ctk.CTkLabel(scroll_frame, text="Datos del Trámite", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_frame_tramite.pack(pady=(10, 5), fill="x", padx=10)

        # Nivel Educativo
        ctk.CTkLabel(scroll_frame, text="Nivel que cursa el alumno:").pack(anchor="w", padx=20)
        niveles = ["Preescolar", "Primaria", "Secundaria", "Preparatoria", "Universidad"]
        self.combo_nivel = ctk.CTkComboBox(scroll_frame, values=niveles)
        self.combo_nivel.pack(fill="x", padx=20, pady=(0, 10))

        # Municipio
        ctk.CTkLabel(scroll_frame, text="Municipio donde estudia:*").pack(anchor="w", padx=20)
        self.combo_municipio = ctk.CTkComboBox(scroll_frame, values=["Cargando..."])
        self.combo_municipio.pack(fill="x", padx=20, pady=(0, 10))

        # Asunto
        ctk.CTkLabel(scroll_frame, text="Asunto a tratar:").pack(anchor="w", padx=20)
        self.entry_asunto = ctk.CTkTextbox(scroll_frame, height=100)
        self.entry_asunto.pack(fill="x", padx=20, pady=(0, 10))
        
        # --- Botón de Acción ---
        self.btn_guardar_cita = ctk.CTkButton(scroll_frame, text="Registrar Cita", font=ctk.CTkFont(weight="bold"))
        self.btn_guardar_cita.pack(fill="x", padx=20, pady=10)
        
        # Label para mensajes de éxito o error
        self.lbl_mensaje_registrar = ctk.CTkLabel(scroll_frame, text="", font=ctk.CTkFont(size=14))
        self.lbl_mensaje_registrar.pack(fill="x", padx=20, pady=10)


        # ======================================================
        # --- Pestaña 2: Consultar / Modificar Cita (SOLO CAMPOS DE BÚSQUEDA) ---
        # ======================================================
        tab_modificar = self.tabs.tab("Consultar / Modificar Cita")
        
        # (Este es el diseño correcto, sin el formulario completo)
        ctk.CTkLabel(tab_modificar, text="Aquí podrás consultar o modificar tu cita.").pack(pady=20)
        ctk.CTkLabel(tab_modificar, text="Ingresa tu CURP:").pack(pady=(10,0))
        self.entry_curp_mod = ctk.CTkEntry(tab_modificar, width=300)
        self.entry_curp_mod.pack()
        
        ctk.CTkLabel(tab_modificar, text="Ingresa tu Número de Turno:").pack(pady=(10,0))
        self.entry_turno_mod = ctk.CTkEntry(tab_modificar, width=300)
        self.entry_turno_mod.pack()
        
        self.btn_buscar_mod = ctk.CTkButton(tab_modificar, text="Buscar Cita para Modificar")
        self.btn_buscar_mod.pack(pady=20)