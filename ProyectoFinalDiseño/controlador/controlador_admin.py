# controlador/controlador_admin.py
import customtkinter as ctk
from modelo.municipio_model import Municipio
from modelo.cita_model import Cita
from modelo.nivel_model import Nivel
from modelo.tipotramite_model import TipoTramite
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ControladorAdmin:
    
    def __init__(self, vista_admin):
        self.vista = vista_admin
        # --- Modelos ---
        self.municipio_model = Municipio 
        self.cita_model = Cita           
        self.nivel_model = Nivel
        self.tipotramite_model = TipoTramite
        
        # --- Variables para Dashboard  ---
        self.mapa_municipios_dash = {}
        self.mapa_niveles_dash = {}
        self.mapa_tramites_dash = {}
        
        # --- Variables para guardar la selección de Cita ---
        self.curp_seleccionada = None
        self.frame_cita_seleccionado = None
        
        # --- Configurar listeners (comandos) de los botones ---
        
        # 1. Pestaña de Citas
        self.vista.btn_buscar_cita.configure(command=self._buscar_citas)
        self.vista.btn_eliminar_cita.configure(command=self._eliminar_cita)
        self.vista.btn_resolver_cita.configure(command=self._marcar_cita_resuelta)
        self.vista.btn_poner_pendiente_cita.configure(command=self._marcar_cita_pendiente)
        
        # 2. Pestaña de Dashboard
        self.vista.btn_refrescar_dash.configure(command=self._actualizar_dashboard)
        
        # 3. Pestaña de Municipios
        self.vista.btn_guardar_muni.configure(command=self._guardar_municipio)
        self.vista.btn_eliminar_muni.configure(command=self._eliminar_municipio)
        self.vista.btn_nuevo_muni.configure(command=self._limpiar_form_municipio)
        
        # 4. Pestaña de Niveles
        self.vista.btn_guardar_nivel.configure(command=self._guardar_nivel)
        self.vista.btn_eliminar_nivel.configure(command=self._eliminar_nivel)
        self.vista.btn_nuevo_nivel.configure(command=self._limpiar_form_nivel)
        
        # 5. Pestaña de Trámites
        self.vista.btn_guardar_tramite.configure(command=self._guardar_tramite)
        self.vista.btn_eliminar_tramite.configure(command=self._eliminar_tramite)
        self.vista.btn_nuevo_tramite.configure(command=self._limpiar_form_tramite)
        
        # 6. Botón de Cerrar Sistema
        self.vista.btn_cerrar_sistema.configure(command=self._cerrar_sistema)
        
        # --- Inicializar la vista ---
        self._actualizar_lista_municipios()
        self._limpiar_form_municipio()
        
        self._actualizar_lista_niveles()
        self._limpiar_form_nivel()
        
        self._actualizar_lista_tramites()
        self._limpiar_form_tramite()
        
        self._cargar_comboboxes_dashboard() 
        self._actualizar_dashboard()      

    # ======================================================
    # --- Métodos de Gestión de Municipios ---
    # ======================================================
    
    def _actualizar_lista_municipios(self):
        """Pide al modelo todos los municipios y los muestra."""
        print("Actualizando lista de municipios...")
        try:
            for widget in self.vista.frame_lista_municipios.winfo_children():
                widget.destroy()
            self.vista.labels_municipios = {}
            municipios = self.municipio_model.get_all()
            
            if municipios:
                header_frame = ctk.CTkFrame(self.vista.frame_lista_municipios, fg_color="gray20")
                header_frame.pack(fill="x", pady=(0, 5))
                ctk.CTkLabel(header_frame, text="ID", width=40, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
                ctk.CTkLabel(header_frame, text="Nombre", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

                for muni in municipios:
                    id_muni, nombre_muni = muni
                    
                    muni_frame = ctk.CTkFrame(self.vista.frame_lista_municipios, fg_color="transparent")
                    muni_frame.pack(fill="x", pady=2)
                    
                    label_id = ctk.CTkLabel(muni_frame, text=f"{id_muni}", width=40)
                    label_id.pack(side="left", padx=10)
                    label_nombre = ctk.CTkLabel(muni_frame, text=f"{nombre_muni}", anchor="w")
                    label_nombre.pack(side="left", padx=10, fill="x")
                    
                    click_handler = lambda e, id=id_muni, nombre=nombre_muni: self._seleccionar_municipio(id, nombre)
                    
                    muni_frame.bind("<Button-1>", click_handler)
                    label_id.bind("<Button-1>", click_handler)
                    label_nombre.bind("<Button-1>", click_handler)
                    
                    self.vista.labels_municipios[id_muni] = (label_id, label_nombre)
            else:
                ctk.CTkLabel(self.vista.frame_lista_municipios, text="No hay municipios registrados.").pack()
        except Exception as e:
            print(f"Error al actualizar lista de municipios: {e}")
            ctk.CTkLabel(self.vista.frame_lista_municipios, text="Error al cargar los municipios.").pack()
    
    def _seleccionar_municipio(self, id_muni, nombre_muni):
        """Rellena el formulario de municipios."""
        print(f"Municipio seleccionado: ID={id_muni}, Nombre={nombre_muni}")
        
        self.vista.entry_id_muni.configure(state="normal")
        self.vista.entry_nombre_muni.configure(state="normal")
        
        self.vista.entry_id_muni.delete(0, "end")
        self.vista.entry_nombre_muni.delete(0, "end")
        
        self.vista.entry_id_muni.insert(0, str(id_muni))
        self.vista.entry_nombre_muni.insert(0, nombre_muni)
        
        self.vista.entry_id_muni.configure(state="disabled")

    def _limpiar_form_municipio(self):
        """Limpia el formulario de municipios."""
        self.vista.entry_id_muni.configure(state="normal")
        self.vista.entry_id_muni.delete(0, "end")
        self.vista.entry_id_muni.configure(state="disabled")
        self.vista.entry_nombre_muni.delete(0, "end")

    def _guardar_municipio(self):
        """Guarda (Crea/Actualiza) un municipio."""
        nombre = self.vista.entry_nombre_muni.get()
        
        self.vista.entry_id_muni.configure(state="normal")
        id_muni = self.vista.entry_id_muni.get()
        self.vista.entry_id_muni.configure(state="disabled")

        if not nombre:
            print("El nombre no puede estar vacío.")
            return

        if id_muni: # Actualizar
            modelo = self.municipio_model(id_municipio=int(id_muni), nombre=nombre)
        else: # Crear
            modelo = self.municipio_model(nombre=nombre)

        if modelo.save():
            print("¡Municipio guardado exitosamente!")
            self._actualizar_lista_municipios()
            self._limpiar_form_municipio()
            self._cargar_comboboxes_dashboard() # Recargar el combo del dashboard
        else:
            print("Error al guardar el municipio.")

    def _eliminar_municipio(self):
        """Elimina el municipio seleccionado."""
        self.vista.entry_id_muni.configure(state="normal")
        id_muni = self.vista.entry_id_muni.get()
        self.vista.entry_id_muni.configure(state="disabled")

        if not id_muni:
            print("No hay ningún municipio seleccionado para eliminar.")
            return
        
        print(f"Intentando eliminar municipio ID: {id_muni}")
        modelo = self.municipio_model(id_municipio=int(id_muni))
        
        if modelo.delete():
            print("¡Municipio eliminado exitosamente!")
            self._actualizar_lista_municipios()
            self._limpiar_form_municipio()
            self._cargar_comboboxes_dashboard() # Recargar el combo del dashboard
        else:
            print("Error al eliminar el municipio.")

    # ======================================================
    # --- Métodos de Gestión de Niveles ---
    # ======================================================

    def _actualizar_lista_niveles(self):
        """Pide al modelo todos los niveles y los muestra."""
        print("Actualizando lista de niveles...")
        try:
            for widget in self.vista.frame_lista_niveles.winfo_children():
                widget.destroy()
            self.vista.labels_niveles = {}
            niveles = self.nivel_model.get_all()
            
            if niveles:
                header_frame = ctk.CTkFrame(self.vista.frame_lista_niveles, fg_color="gray20")
                header_frame.pack(fill="x", pady=(0, 5))
                ctk.CTkLabel(header_frame, text="ID", width=40, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
                ctk.CTkLabel(header_frame, text="Nombre", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

                for nivel in niveles:
                    id_nivel, nombre_nivel = nivel
                    
                    nivel_frame = ctk.CTkFrame(self.vista.frame_lista_niveles, fg_color="transparent")
                    nivel_frame.pack(fill="x", pady=2)
                    
                    label_id = ctk.CTkLabel(nivel_frame, text=f"{id_nivel}", width=40)
                    label_id.pack(side="left", padx=10)
                    label_nombre = ctk.CTkLabel(nivel_frame, text=f"{nombre_nivel}", anchor="w")
                    label_nombre.pack(side="left", padx=10, fill="x")
                    
                    click_handler = lambda e, id=id_nivel, nombre=nombre_nivel: self._seleccionar_nivel(id, nombre)
                    
                    nivel_frame.bind("<Button-1>", click_handler)
                    label_id.bind("<Button-1>", click_handler)
                    label_nombre.bind("<Button-1>", click_handler)
                    
                    self.vista.labels_niveles[id_nivel] = (label_id, label_nombre)
            else:
                ctk.CTkLabel(self.vista.frame_lista_niveles, text="No hay niveles registrados.").pack()
        except Exception as e:
            print(f"Error al actualizar lista de niveles: {e}")
            ctk.CTkLabel(self.vista.frame_lista_niveles, text="Error al cargar los niveles.").pack()
    
    def _seleccionar_nivel(self, id_nivel, nombre_nivel):
        """Rellena el formulario de niveles."""
        print(f"Nivel seleccionado: ID={id_nivel}, Nombre={nombre_nivel}")
        
        self.vista.entry_id_nivel.configure(state="normal")
        self.vista.entry_nombre_nivel.configure(state="normal")
        
        self.vista.entry_id_nivel.delete(0, "end")
        self.vista.entry_nombre_nivel.delete(0, "end")
        
        self.vista.entry_id_nivel.insert(0, str(id_nivel))
        self.vista.entry_nombre_nivel.insert(0, nombre_nivel)
        
        self.vista.entry_id_nivel.configure(state="disabled")

    def _limpiar_form_nivel(self):
        """Limpia el formulario de niveles."""
        self.vista.entry_id_nivel.configure(state="normal")
        self.vista.entry_id_nivel.delete(0, "end")
        self.vista.entry_id_nivel.configure(state="disabled")
        self.vista.entry_nombre_nivel.delete(0, "end")

    def _guardar_nivel(self):
        """Guarda (Crea/Actualiza) un nivel."""
        nombre = self.vista.entry_nombre_nivel.get()
        
        self.vista.entry_id_nivel.configure(state="normal")
        id_nivel = self.vista.entry_id_nivel.get()
        self.vista.entry_id_nivel.configure(state="disabled")

        if not nombre:
            print("El nombre no puede estar vacío.")
            return

        if id_nivel: # Actualizar
            modelo = self.nivel_model(id_nivel=int(id_nivel), nombre=nombre)
        else: # Crear
            modelo = self.nivel_model(nombre=nombre)

        if modelo.save():
            print("¡Nivel guardado exitosamente!")
            self._actualizar_lista_niveles()
            self._limpiar_form_nivel()
        else:
            print("Error al guardar el nivel.")

    def _eliminar_nivel(self):
        """Elimina el nivel seleccionado."""
        self.vista.entry_id_nivel.configure(state="normal")
        id_nivel = self.vista.entry_id_nivel.get()
        self.vista.entry_id_nivel.configure(state="disabled")

        if not id_nivel:
            print("No hay ningún nivel seleccionado para eliminar.")
            return
        
        print(f"Intentando eliminar nivel ID: {id_nivel}")
        modelo = self.nivel_model(id_nivel=int(id_nivel))
        
        if modelo.delete():
            print("¡Nivel eliminado exitosamente!")
            self._actualizar_lista_niveles()
            self._limpiar_form_nivel()
        else:
            print("Error al eliminar el nivel.")

    # ======================================================
    # --- Métodos de Gestión de Trámites ---
    # ======================================================

    def _actualizar_lista_tramites(self):
        """Pide al modelo todos los trámites y los muestra."""
        print("Actualizando lista de trámites...")
        try:
            for widget in self.vista.frame_lista_tramites.winfo_children():
                widget.destroy()
            self.vista.labels_tramites = {}
            tramites = self.tipotramite_model.get_all()
            
            if tramites:
                header_frame = ctk.CTkFrame(self.vista.frame_lista_tramites, fg_color="gray20")
                header_frame.pack(fill="x", pady=(0, 5))
                ctk.CTkLabel(header_frame, text="ID", width=40, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
                ctk.CTkLabel(header_frame, text="Nombre", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

                for tramite in tramites:
                    id_tramite, nombre_tramite = tramite
                    
                    tramite_frame = ctk.CTkFrame(self.vista.frame_lista_tramites, fg_color="transparent")
                    tramite_frame.pack(fill="x", pady=2)
                    
                    label_id = ctk.CTkLabel(tramite_frame, text=f"{id_tramite}", width=40)
                    label_id.pack(side="left", padx=10)
                    label_nombre = ctk.CTkLabel(tramite_frame, text=f"{nombre_tramite}", anchor="w")
                    label_nombre.pack(side="left", padx=10, fill="x")
                    
                    click_handler = lambda e, id=id_tramite, nombre=nombre_tramite: self._seleccionar_tramite(id, nombre)
                    
                    tramite_frame.bind("<Button-1>", click_handler)
                    label_id.bind("<Button-1>", click_handler)
                    label_nombre.bind("<Button-1>", click_handler)
                    
                    self.vista.labels_tramites[id_tramite] = (label_id, label_nombre)
            else:
                ctk.CTkLabel(self.vista.frame_lista_tramites, text="No hay trámites registrados.").pack()
        except Exception as e:
            print(f"Error al actualizar lista de trámites: {e}")
            ctk.CTkLabel(self.vista.frame_lista_tramites, text="Error al cargar los trámites.").pack()
    
    def _seleccionar_tramite(self, id_tramite, nombre_tramite):
        """Rellena el formulario de trámites."""
        print(f"Trámite seleccionado: ID={id_tramite}, Nombre={nombre_tramite}")
        
        self.vista.entry_id_tramite.configure(state="normal")
        self.vista.entry_nombre_tramite.configure(state="normal")
        
        self.vista.entry_id_tramite.delete(0, "end")
        self.vista.entry_nombre_tramite.delete(0, "end")
        
        self.vista.entry_id_tramite.insert(0, str(id_tramite))
        self.vista.entry_nombre_tramite.insert(0, nombre_tramite)
        
        self.vista.entry_id_tramite.configure(state="disabled")

    def _limpiar_form_tramite(self):
        """Limpia el formulario de trámites."""
        self.vista.entry_id_tramite.configure(state="normal")
        self.vista.entry_id_tramite.delete(0, "end")
        self.vista.entry_id_tramite.configure(state="disabled")
        self.vista.entry_nombre_tramite.delete(0, "end")

    def _guardar_tramite(self):
        """Guarda (Crea/Actualiza) un trámite."""
        nombre = self.vista.entry_nombre_tramite.get()
        
        self.vista.entry_id_tramite.configure(state="normal")
        id_tramite = self.vista.entry_id_tramite.get()
        self.vista.entry_id_tramite.configure(state="disabled")

        if not nombre:
            print("El nombre no puede estar vacío.")
            return

        if id_tramite: # Actualizar
            modelo = self.tipotramite_model(id_tipotramite=int(id_tramite), nombre=nombre)
        else: # Crear
            modelo = self.tipotramite_model(nombre=nombre)

        if modelo.save():
            print("¡Trámite guardado exitosamente!")
            self._actualizar_lista_tramites()
            self._limpiar_form_tramite()
        else:
            print("Error al guardar el trámite.")

    def _eliminar_tramite(self):
        """Elimina el trámite seleccionado."""
        self.vista.entry_id_tramite.configure(state="normal")
        id_tramite = self.vista.entry_id_tramite.get()
        self.vista.entry_id_tramite.configure(state="disabled")

        if not id_tramite:
            print("No hay ningún trámite seleccionado para eliminar.")
            return
        
        print(f"Intentando eliminar trámite ID: {id_tramite}")
        modelo = self.tipotramite_model(id_tipotramite=int(id_tramite))
        
        if modelo.delete():
            print("¡Trámite eliminado exitosamente!")
            self._actualizar_lista_tramites()
            self._limpiar_form_tramite()
        else:
            print("Error al eliminar el trámite.")

    # ======================================================
    # --- Métodos de Gestión de Citas ---
    # ======================================================

    def _buscar_citas(self):
        """
        Obtiene el texto de búsqueda, consulta al modelo Cita
        y muestra los resultados en el frame de lista de citas.
        """
        filtro = self.vista.entry_buscar_cita.get()
        if not filtro:
            print("El campo de búsqueda está vacío.")
            return

        print(f"Buscando citas con filtro: {filtro}")

        try:
            for widget in self.vista.frame_lista_citas.winfo_children():
                widget.destroy()
            self.vista.frames_citas = {}
            
            self.curp_seleccionada = None
            self.frame_cita_seleccionado = None

            resultados = self.cita_model.get_by_curp_o_nombre(filtro)

            if not resultados:
                ctk.CTkLabel(self.vista.frame_lista_citas, text="No se encontraron citas con ese criterio.").pack(pady=10)
                return

            header_frame = ctk.CTkFrame(self.vista.frame_lista_citas, fg_color="gray20")
            header_frame.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(header_frame, text="CURP", width=160, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Alumno", width=200, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Turno", width=40, font=ctk.CTkFont(weight="bold"), anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Estatus", width=80, font=ctk.CTkFont(weight="bold"), anchor="center").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Municipio", width=100, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Nivel", width=100, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Trámite", width=120, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=5)

            for fila in resultados:
                # La estructura de la 'fila' ha cambiado por la nueva BD
                curp = fila[0]
                nombre_completo = f"{fila[1]} {fila[2]} {fila[3]}"
                turno = fila[4]
                estatus = fila[5]
                municipio_nombre = fila[6] or "N/A"
                nivel_nombre = fila[7] or "N/A"
                tramite_nombre = fila[8] or "N/A"
                
                cita_frame = ctk.CTkFrame(self.vista.frame_lista_citas, fg_color="transparent")
                cita_frame.pack(fill="x", pady=2)
                
                # --- ¡LISTA DE LABELS CORREGIDA! ---
                ctk.CTkLabel(cita_frame, text=curp, width=160, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(cita_frame, text=nombre_completo, width=200, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(cita_frame, text=str(turno), width=40, anchor="center").pack(side="left", padx=5) # <-- Centrado
                
                color = "green" if estatus == "Resuelto" else "orange"
                ctk.CTkLabel(cita_frame, text=estatus, width=80, text_color=color, anchor="center").pack(side="left", padx=5) # <-- Centrado
                
                ctk.CTkLabel(cita_frame, text=municipio_nombre, width=100, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(cita_frame, text=nivel_nombre, width=100, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(cita_frame, text=tramite_nombre, width=120, anchor="w").pack(side="left", padx=5)
                
                click_handler_cita = lambda e, c=curp, frame=cita_frame: self._seleccionar_cita(c, frame)
                
                cita_frame.bind("<Button-1>", click_handler_cita)
                for widget in cita_frame.winfo_children():
                    widget.bind("<Button-1>", click_handler_cita)
                
        except Exception as e:
            print(f"Error al buscar citas: {e}")
            import traceback
            traceback.print_exc() 
            ctk.CTkLabel(self.vista.frame_lista_citas, text="Error al realizar la búsqueda.").pack(pady=10)

    def _seleccionar_cita(self, curp, frame_widget):
        """Resalta la fila seleccionada y guarda la CURP."""
        print(f"Cita seleccionada: CURP={curp}")
        
        if self.frame_cita_seleccionado is not None:
            self.frame_cita_seleccionado.configure(fg_color="transparent")
            
        self.curp_seleccionada = curp
        self.frame_cita_seleccionado = frame_widget
        
        self.frame_cita_seleccionado.configure(fg_color="gray25")

    def _eliminar_cita(self):
        """Elimina la cita que está actualmente seleccionada."""
        if not self.curp_seleccionada:
            print("No hay ninguna cita seleccionada para eliminar.")
            return
            
        print(f"Intentando eliminar cita: {self.curp_seleccionada}")
        
        if self.cita_model.delete_by_curp(self.curp_seleccionada):
            print("¡Cita eliminada exitosamente!")
            self.curp_seleccionada = None
            self.frame_cita_seleccionado = None
            self._buscar_citas() 
        else:
            print("Error al eliminar la cita.")

    def _marcar_cita_resuelta(self):
        """Cambia el estatus a 'Resuelto'."""
        self._cambiar_estatus_cita("Resuelto")

    def _marcar_cita_pendiente(self):
        """Cambia el estatus a 'Pendiente'."""
        self._cambiar_estatus_cita("Pendiente")

    def _cambiar_estatus_cita(self, nuevo_estatus):
        """Función genérica para cambiar el estatus de la cita seleccionada."""
        if not self.curp_seleccionada:
            print(f"No hay ninguna cita seleccionada para marcar como {nuevo_estatus}.")
            return
            
        print(f"Marcando cita {self.curp_seleccionada} como {nuevo_estatus}...")
        
        if self.cita_model.actualizar_estatus(self.curp_seleccionada, nuevo_estatus):
            print("¡Estatus actualizado!")
            self._buscar_citas()
        else:
            print("Error al actualizar el estatus.")

    # ======================================================
    # --- Métodos del Dashboard (¡ACTUALIZADOS!) ---
    # ======================================================
    
    def _cargar_comboboxes_dashboard(self):
        """Carga TODOS los catálogos en los ComboBoxes de la pestaña Dashboard."""
        
        # 1. Cargar Municipios
        try:
            municipios_tuplas = self.municipio_model.get_all()
            self.mapa_municipios_dash = {}
            nombres_municipios = ["Todos"] 
            for id_muni, nombre in municipios_tuplas:
                nombres_municipios.append(nombre)
                self.mapa_municipios_dash[nombre] = id_muni
            self.vista.combo_municipios_dash.configure(values=nombres_municipios)
            self.vista.combo_municipios_dash.set("Todos")
        except Exception as e:
            print(f"Error cargando municipios para dashboard: {e}")
            self.vista.combo_municipios_dash.configure(values=["Error"])
            
        # 2. Cargar Niveles
        try:
            niveles_tuplas = self.nivel_model.get_all()
            self.mapa_niveles_dash = {}
            nombres_niveles = ["Todos"] 
            for id_nivel, nombre in niveles_tuplas:
                nombres_niveles.append(nombre)
                self.mapa_niveles_dash[nombre] = id_nivel
            self.vista.combo_niveles_dash.configure(values=nombres_niveles)
            self.vista.combo_niveles_dash.set("Todos")
        except Exception as e:
            print(f"Error cargando niveles para dashboard: {e}")
            self.vista.combo_niveles_dash.configure(values=["Error"])

        # 3. Cargar Trámites
        try:
            tramites_tuplas = self.tipotramite_model.get_all()
            self.mapa_tramites_dash = {}
            nombres_tramites = ["Todos"] 
            for id_tramite, nombre in tramites_tuplas:
                nombres_tramites.append(nombre)
                self.mapa_tramites_dash[nombre] = id_tramite
            self.vista.combo_tramites_dash.configure(values=nombres_tramites)
            self.vista.combo_tramites_dash.set("Todos")
        except Exception as e:
            print(f"Error cargando trámites para dashboard: {e}")
            self.vista.combo_tramites_dash.configure(values=["Error"])

    def _actualizar_dashboard(self):
        """Obtiene los datos de la BD (con 3 filtros) y dibuja la gráfica."""
        print("Actualizando dashboard...")
        
        # 1. Leer los 3 filtros
        municipio_sel = self.vista.combo_municipios_dash.get()
        nivel_sel = self.vista.combo_niveles_dash.get()
        tramite_sel = self.vista.combo_tramites_dash.get()
        
        # 2. Convertir nombres a IDs (o None si es "Todos")
        id_municipio = self.mapa_municipios_dash.get(municipio_sel)
        id_nivel = self.mapa_niveles_dash.get(nivel_sel)
        id_tramite = self.mapa_tramites_dash.get(tramite_sel)
        
        # 3. Pedir datos al modelo con los 3 filtros
        datos = self.cita_model.get_stats_dashboard(id_municipio, id_nivel, id_tramite)
        
        # 4. Procesar y dibujar
        stats = {'Pendiente': 0, 'Resuelto': 0}
        for estatus, cantidad in datos:
            if estatus in stats:
                stats[estatus] = cantidad
        
        labels = list(stats.keys())
        valores = list(stats.values())

        for widget in self.vista.frame_grafica.winfo_children():
            widget.destroy() 
        
        if sum(valores) == 0:
             lbl_placeholder_grafica = ctk.CTkLabel(self.vista.frame_grafica, 
                                                    text="No hay datos para mostrar con este filtro.", 
                                                    font=("Arial", 20))
             lbl_placeholder_grafica.place(relx=0.5, rely=0.5, anchor="center")
             return

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor("#2b2b2b")
        
        ax = fig.add_subplot(111)
        
        barras = ax.bar(labels, valores, color=["#FF8C00", "#4CAF50"])
        ax.set_title("Estatus de Citas", color="white")
        ax.set_ylabel("Cantidad de Citas", color="white")
        
        ax.bar_label(barras, color="white")
        
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.set_facecolor("#343638")

        canvas = FigureCanvasTkAgg(fig, master=self.vista.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

    # ======================================================
    # --- Métodos Generales ---
    # ======================================================
    
    def _cerrar_sistema(self):
        """Cierra la ventana de administrador (y eventualmente toda la app)."""
        print("Cerrando sistema...")
        self.vista.destroy()