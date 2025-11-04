# vista/vista_admin.py
import customtkinter as ctk

class VistaAdmin(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("Panel de Administrador - Sistema de Turnos")
        self.geometry("1100x700") # Un tamaño más grande

        # --- Frame Superior (para el menú/botón de salida) ---
        frame_top = ctk.CTkFrame(self, height=50)
        frame_top.pack(fill="x", side="top", padx=10, pady=(10, 0))

        lbl_titulo_admin = ctk.CTkLabel(frame_top, 
                                        text="Panel de Administración", 
                                        font=ctk.CTkFont(size=18, weight="bold"))
        lbl_titulo_admin.pack(side="left", padx=20)

        # Botón para "Cerrar Sistema" (Requerido)
        self.btn_cerrar_sistema = ctk.CTkButton(frame_top, text="Cerrar Sistema", fg_color="red")
        self.btn_cerrar_sistema.pack(side="right", padx=20)

        # --- Sistema de Pestañas (Tabs) ---
        self.tab_view = ctk.CTkTabview(self, anchor="w")
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Creamos las pestañas
        self.tab_view.add("Gestión de Citas")
        self.tab_view.add("Gestión de Municipios")
        self.tab_view.add("Dashboard")

        # --- 1. Contenido de la Pestaña "Gestión de Citas" ---
        tab_citas = self.tab_view.tab("Gestión de Citas")
        
        # Frame para buscar
        frame_buscar = ctk.CTkFrame(tab_citas)
        frame_buscar.pack(fill="x", padx=10, pady=10)

        lbl_buscar = ctk.CTkLabel(frame_buscar, text="Buscar por CURP o Nombre:")
        lbl_buscar.pack(side="left", padx=(10, 5))

        self.entry_buscar_cita = ctk.CTkEntry(frame_buscar, width=300)
        self.entry_buscar_cita.pack(side="left", padx=5)
        
        self.btn_buscar_cita = ctk.CTkButton(frame_buscar, text="Buscar")
        self.btn_buscar_cita.pack(side="left", padx=5)

        # Frame para los resultados (por ahora un área de texto)
        self.frame_lista_citas = ctk.CTkScrollableFrame(tab_citas)
        self.frame_lista_citas.pack(fill="both", expand=True, padx=10, pady=10)
        self.frames_citas = {}

        # Frame para botones de acción (Modificar, Eliminar, Cambiar Estatus)
        frame_acciones_citas = ctk.CTkFrame(tab_citas)
        frame_acciones_citas.pack(fill="x", padx=10, pady=10)
        # (Añadiremos los botones de editar/eliminar/estatus aquí)

        # (Justo debajo del bloque anterior)

        self.btn_eliminar_cita = ctk.CTkButton(frame_acciones_citas, 
                                         text="Eliminar Cita Seleccionada", 
                                         fg_color="red")
        self.btn_eliminar_cita.pack(side="left", padx=10, pady=5)

        self.btn_resolver_cita = ctk.CTkButton(frame_acciones_citas, 
                                         text="Marcar como Resuelto", 
                                         fg_color="green")
        self.btn_resolver_cita.pack(side="left", padx=10, pady=5)

        self.btn_poner_pendiente_cita = ctk.CTkButton(frame_acciones_citas, 
                                                text="Marcar como Pendiente", 
                                                fg_color="orange")
        self.btn_poner_pendiente_cita.pack(side="left", padx=10, pady=5)

        # --- 2. Contenido de la Pestaña "Gestión de Municipios" (Catálogo) ---
        tab_municipios = self.tab_view.tab("Gestión de Municipios")
        
        # Frame para el formulario de CRUD
        frame_form_muni = ctk.CTkFrame(tab_municipios)
        frame_form_muni.pack(fill="x", padx=10, pady=10)
        
        lbl_id_muni = ctk.CTkLabel(frame_form_muni, text="ID:")
        lbl_id_muni.pack(side="left", padx=5)
        self.entry_id_muni = ctk.CTkEntry(frame_form_muni, width=50, state="disabled") # El ID no se edita
        self.entry_id_muni.pack(side="left", padx=5)

        lbl_nombre_muni = ctk.CTkLabel(frame_form_muni, text="Nombre:")
        lbl_nombre_muni.pack(side="left", padx=5)
        self.entry_nombre_muni = ctk.CTkEntry(frame_form_muni, width=200)
        self.entry_nombre_muni.pack(side="left", padx=5)

        self.btn_guardar_muni = ctk.CTkButton(frame_form_muni, text="Guardar")
        self.btn_guardar_muni.pack(side="left", padx=5)
        self.btn_eliminar_muni = ctk.CTkButton(frame_form_muni, text="Eliminar", fg_color="red")
        self.btn_eliminar_muni.pack(side="left", padx=5)
        self.btn_nuevo_muni = ctk.CTkButton(frame_form_muni, text="Nuevo", fg_color="gray")
        self.btn_nuevo_muni.pack(side="left", padx=5)

        # Frame con scroll para la lista de municipios (ESTA ES LA PARTE CORREGIDA)
        self.frame_lista_municipios = ctk.CTkScrollableFrame(tab_municipios)
        self.frame_lista_municipios.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Y ESTA LÍNEA ESTÁ AHORA DENTRO DE __init__
        self.labels_municipios = {} 

        # --- 3. Contenido de la Pestaña "Dashboard" ---
        tab_dashboard = self.tab_view.tab("Dashboard")
        
        # Frame para filtros
        frame_filtros_dash = ctk.CTkFrame(tab_dashboard)
        frame_filtros_dash.pack(fill="x", padx=10, pady=10)

        lbl_filtro_muni = ctk.CTkLabel(frame_filtros_dash, text="Filtrar por Municipio:")
        lbl_filtro_muni.pack(side="left", padx=5)
        
        # Este ComboBox se llenará desde la BD
        self.combo_municipios_dash = ctk.CTkComboBox(frame_filtros_dash, values=["Todos"])
        self.combo_municipios_dash.pack(side="left", padx=5)

        self.btn_refrescar_dash = ctk.CTkButton(frame_filtros_dash, text="Refrescar Gráfica")
        self.btn_refrescar_dash.pack(side="left", padx=5)

        # Frame donde irá la gráfica (placeholder)
        self.frame_grafica = ctk.CTkFrame(tab_dashboard, fg_color="gray20")
        self.frame_grafica.pack(fill="both", expand=True, padx=10, pady=10)
        
        lbl_placeholder_grafica = ctk.CTkLabel(self.frame_grafica, text="[AQUÍ VA LA GRÁFICA DE MATPLOTLIB]", font=("Arial", 20))
        lbl_placeholder_grafica.place(relx=0.5, rely=0.5, anchor="center")

# --- Bloque para probar la vista (opcional) ---
if __name__ == "__main__":
    app = VistaAdmin()
    app.mainloop()