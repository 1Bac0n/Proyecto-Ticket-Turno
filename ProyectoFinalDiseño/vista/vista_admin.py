# vista/vista_admin.py
import customtkinter as ctk

class VistaAdmin(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("Panel de Administrador - Sistema de Turnos")
        self.geometry("1100x700")

        # --- Frame Superior ---
        frame_top = ctk.CTkFrame(self, height=50)
        frame_top.pack(fill="x", side="top", padx=10, pady=(10, 0))

        lbl_titulo_admin = ctk.CTkLabel(frame_top, 
                                        text="Panel de Administración", 
                                        font=ctk.CTkFont(size=18, weight="bold"))
        lbl_titulo_admin.pack(side="left", padx=20)

        self.btn_cerrar_sistema = ctk.CTkButton(frame_top, text="Cerrar Sistema", fg_color="red")
        self.btn_cerrar_sistema.pack(side="right", padx=20)

        # --- Sistema de Pestañas ---
        self.tab_view = ctk.CTkTabview(self, anchor="w")
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_view.add("Gestión de Citas")
        self.tab_view.add("Dashboard")
        self.tab_view.add("Gestión de Municipios")
        self.tab_view.add("Gestión de Niveles")
        self.tab_view.add("Gestión de Trámites")

        # ======================================================
        # --- 1. Pestaña "Gestión de Citas" ---
        # ======================================================
        tab_citas = self.tab_view.tab("Gestión de Citas")
        
        frame_buscar = ctk.CTkFrame(tab_citas)
        frame_buscar.pack(fill="x", padx=10, pady=10)

        lbl_buscar = ctk.CTkLabel(frame_buscar, text="Buscar por CURP o Nombre:")
        lbl_buscar.pack(side="left", padx=(10, 5))

        self.entry_buscar_cita = ctk.CTkEntry(frame_buscar, width=300)
        self.entry_buscar_cita.pack(side="left", padx=5)
        
        self.btn_buscar_cita = ctk.CTkButton(frame_buscar, text="Buscar")
        self.btn_buscar_cita.pack(side="left", padx=5)

        self.frame_lista_citas = ctk.CTkScrollableFrame(tab_citas)
        self.frame_lista_citas.pack(fill="both", expand=True, padx=10, pady=10)
        self.frames_citas = {}

        frame_acciones_citas = ctk.CTkFrame(tab_citas)
        frame_acciones_citas.pack(fill="x", padx=10, pady=10)
        
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

        # ======================================================
        # --- 2. Pestaña "Dashboard" ---
        # ======================================================
        tab_dashboard = self.tab_view.tab("Dashboard")
        
        frame_filtros_dash = ctk.CTkFrame(tab_dashboard)
        frame_filtros_dash.pack(fill="x", padx=10, pady=10)

        # --- Filtro 1: Municipio ---
        lbl_filtro_muni = ctk.CTkLabel(frame_filtros_dash, text="Filtrar por Municipio:")
        lbl_filtro_muni.pack(side="left", padx=(10, 5))
        self.combo_municipios_dash = ctk.CTkComboBox(frame_filtros_dash, values=["Todos"])
        self.combo_municipios_dash.pack(side="left", padx=5)

        # --- Filtro 2: Nivel  ---
        lbl_filtro_nivel = ctk.CTkLabel(frame_filtros_dash, text="Nivel:")
        lbl_filtro_nivel.pack(side="left", padx=(10, 5))
        self.combo_niveles_dash = ctk.CTkComboBox(frame_filtros_dash, values=["Todos"])
        self.combo_niveles_dash.pack(side="left", padx=5)

        # --- Filtro 3: Trámite  ---
        lbl_filtro_tramite = ctk.CTkLabel(frame_filtros_dash, text="Trámite:")
        lbl_filtro_tramite.pack(side="left", padx=(10, 5))
        self.combo_tramites_dash = ctk.CTkComboBox(frame_filtros_dash, values=["Todos"])
        self.combo_tramites_dash.pack(side="left", padx=5)
        
        # --- Botón de Refrescar ---
        self.btn_refrescar_dash = ctk.CTkButton(frame_filtros_dash, text="Refrescar Gráfica")
        self.btn_refrescar_dash.pack(side="left", padx=20)

        # Frame para la gráfica
        self.frame_grafica = ctk.CTkFrame(tab_dashboard, fg_color="gray20")
        self.frame_grafica.pack(fill="both", expand=True, padx=10, pady=10)
        
        lbl_placeholder_grafica = ctk.CTkLabel(self.frame_grafica, text="[AQUÍ VA LA GRÁFICA DE MATPLOTLIB]", font=("Arial", 20))
        lbl_placeholder_grafica.place(relx=0.5, rely=0.5, anchor="center")

        # ======================================================
        # --- 3. Pestaña "Gestión de Municipios" ---
        # ======================================================
        tab_municipios = self.tab_view.tab("Gestión de Municipios")
        
        frame_form_muni = ctk.CTkFrame(tab_municipios)
        frame_form_muni.pack(fill="x", padx=10, pady=10)
        
        lbl_id_muni = ctk.CTkLabel(frame_form_muni, text="ID:")
        lbl_id_muni.pack(side="left", padx=5)
        self.entry_id_muni = ctk.CTkEntry(frame_form_muni, width=50, state="disabled")
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

        self.frame_lista_municipios = ctk.CTkScrollableFrame(tab_municipios)
        self.frame_lista_municipios.pack(fill="both", expand=True, padx=10, pady=10)
        self.labels_municipios = {} 

        # ======================================================
        # --- 4. Pestaña "Gestión de Niveles" ---
        # ======================================================
        tab_niveles = self.tab_view.tab("Gestión de Niveles")
        
        frame_form_nivel = ctk.CTkFrame(tab_niveles)
        frame_form_nivel.pack(fill="x", padx=10, pady=10)
        
        lbl_id_nivel = ctk.CTkLabel(frame_form_nivel, text="ID:")
        lbl_id_nivel.pack(side="left", padx=5)
        self.entry_id_nivel = ctk.CTkEntry(frame_form_nivel, width=50, state="disabled")
        self.entry_id_nivel.pack(side="left", padx=5)

        lbl_nombre_nivel = ctk.CTkLabel(frame_form_nivel, text="Nombre:")
        lbl_nombre_nivel.pack(side="left", padx=5)
        self.entry_nombre_nivel = ctk.CTkEntry(frame_form_nivel, width=200)
        self.entry_nombre_nivel.pack(side="left", padx=5)

        self.btn_guardar_nivel = ctk.CTkButton(frame_form_nivel, text="Guardar")
        self.btn_guardar_nivel.pack(side="left", padx=5)
        self.btn_eliminar_nivel = ctk.CTkButton(frame_form_nivel, text="Eliminar", fg_color="red")
        self.btn_eliminar_nivel.pack(side="left", padx=5)
        self.btn_nuevo_nivel = ctk.CTkButton(frame_form_nivel, text="Nuevo", fg_color="gray")
        self.btn_nuevo_nivel.pack(side="left", padx=5)

        self.frame_lista_niveles = ctk.CTkScrollableFrame(tab_niveles)
        self.frame_lista_niveles.pack(fill="both", expand=True, padx=10, pady=10)
        self.labels_niveles = {}

        # ======================================================
        # --- 5. Pestaña "Gestión de Trámites" ---
        # ======================================================
        tab_tramites = self.tab_view.tab("Gestión de Trámites")
        
        frame_form_tramite = ctk.CTkFrame(tab_tramites)
        frame_form_tramite.pack(fill="x", padx=10, pady=10)
        
        lbl_id_tramite = ctk.CTkLabel(frame_form_tramite, text="ID:")
        lbl_id_tramite.pack(side="left", padx=5)
        self.entry_id_tramite = ctk.CTkEntry(frame_form_tramite, width=50, state="disabled")
        self.entry_id_tramite.pack(side="left", padx=5)

        lbl_nombre_tramite = ctk.CTkLabel(frame_form_tramite, text="Nombre:")
        lbl_nombre_tramite.pack(side="left", padx=5)
        self.entry_nombre_tramite = ctk.CTkEntry(frame_form_tramite, width=200)
        self.entry_nombre_tramite.pack(side="left", padx=5)

        self.btn_guardar_tramite = ctk.CTkButton(frame_form_tramite, text="Guardar")
        self.btn_guardar_tramite.pack(side="left", padx=5)
        self.btn_eliminar_tramite = ctk.CTkButton(frame_form_tramite, text="Eliminar", fg_color="red")
        self.btn_eliminar_tramite.pack(side="left", padx=5)
        self.btn_nuevo_tramite = ctk.CTkButton(frame_form_tramite, text="Nuevo", fg_color="gray")
        self.btn_nuevo_tramite.pack(side="left", padx=5)

        self.frame_lista_tramites = ctk.CTkScrollableFrame(tab_tramites)
        self.frame_lista_tramites.pack(fill="both", expand=True, padx=10, pady=10)
        self.labels_tramites = {}

# --- Bloque para probar la vista (opcional) ---
if __name__ == "__main__":
    app = VistaAdmin()
    app.mainloop()