# controlador/controlador_admin.py
import customtkinter as ctk
from modelo.municipio_model import Municipio
from modelo.cita_model import Cita

class ControladorAdmin:
    
    def __init__(self, vista_admin):
        self.vista = vista_admin
        self.municipio_model = Municipio # Acceso al modelo de Municipio
        self.cita_model = Cita           # <-- CORRECTO
        
        # --- Variables para guardar la selección de Cita ---
        self.curp_seleccionada = None
        self.frame_cita_seleccionado = None
        # --------------------------------------------------
        
        # --- Configurar listeners (comandos) de los botones ---
        
        # 1. Pestaña de Municipios (Catálogo)
        self.vista.btn_guardar_muni.configure(command=self._guardar_municipio)
        self.vista.btn_eliminar_muni.configure(command=self._eliminar_municipio)
        self.vista.btn_nuevo_muni.configure(command=self._limpiar_form_municipio)
        
        # 2. Pestaña de Gestión de Citas
        self.vista.btn_buscar_cita.configure(command=self._buscar_citas)
        self.vista.btn_eliminar_cita.configure(command=self._eliminar_cita)
        self.vista.btn_resolver_cita.configure(command=self._marcar_cita_resuelta)
        self.vista.btn_poner_pendiente_cita.configure(command=self._marcar_cita_pendiente)
        
        # 3. Botón de Cerrar Sistema
        self.vista.btn_cerrar_sistema.configure(command=self._cerrar_sistema)
        
        # --- Inicializar la vista ---
        self._actualizar_lista_municipios()
        self._limpiar_form_municipio()

    # --- Métodos de Gestión de Municipios ---
    
    def _actualizar_lista_municipios(self):
        """
        Pide al modelo todos los municipios y los muestra en el
        CTkScrollableFrame como etiquetas clicables.
        """
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
                    id_muni = muni[0]
                    nombre_muni = muni[1]
                    
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
        """
        Se llama cuando el usuario hace clic en un municipio de la lista.
        Rellena el formulario con los datos de ese municipio.
        """
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
        """
En el código que me pasaste, la nueva función `def _abrir_ventana_publica(self):` está **fuera** de la clase `ControladorLogin`. Se quedó al final del archivo, pero no "dentro" de la clase, y por eso Python dice que el objeto no tiene ese atributo (función).
        Toma los datos del formulario de municipios y los manda al modelo
        para CREAR o ACTUALIZAR.
        """
        nombre = self.vista.entry_nombre_muni.get()
        
        self.vista.entry_id_muni.configure(state="normal")
        id_muni = self.vista.entry_id_muni.get()
        self.vista.entry_id_muni.configure(state="disabled")

        if not nombre:
            print("El nombre no puede estar vacío.")
            return

        if id_muni:
            print(f"Actualizando municipio ID: {id_muni}")
            muni_a_actualizar = self.municipio_model(id_municipio=int(id_muni), nombre=nombre)
            exito = muni_a_actualizar.save()
        else:
            print("Creando nuevo municipio...")
            muni_nuevo = self.municipio_model(nombre=nombre)
            exito = muni_nuevo.save()

        if exito:
            print("¡Guardado exitosamente!")
            self._actualizar_lista_municipios()
            self._limpiar_form_municipio()
        else:
            print("Error al guardar el municipio.")

    def _eliminar_municipio(self):
        """
        Elimina el municipio que está actualmente seleccionado en el formulario.
        """
        self.vista.entry_id_muni.configure(state="normal")
        id_muni = self.vista.entry_id_muni.get()
        self.vista.entry_id_muni.configure(state="disabled")

        if not id_muni:
            print("No hay ningún municipio seleccionado para eliminar.")
            return
        
        print(f"Intentando eliminar municipio ID: {id_muni}")
        
        muni_a_eliminar = self.municipio_model(id_municipio=int(id_muni))
        
        if muni_a_eliminar.delete():
            print("¡Municipio eliminado exitosamente!")
            self._actualizar_lista_municipios()
            self._limpiar_form_municipio()
        else:
            print("Error al eliminar el municipio.")

    # --- Métodos de Gestión de Citas ---

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
            
            # Limpiar la selección anterior
            self.curp_seleccionada = None
            self.frame_cita_seleccionado = None

            resultados = self.cita_model.get_by_curp_o_nombre(filtro)

            if not resultados:
                ctk.CTkLabel(self.vista.frame_lista_citas, text="No se encontraron citas con ese criterio.").pack(pady=10)
                return

            header_frame = ctk.CTkFrame(self.vista.frame_lista_citas, fg_color="gray20")
            header_frame.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(header_frame, text="CURP", width=180, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Alumno", width=250, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Turno", width=50, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Estatus", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

            for fila in resultados:
                curp = fila[0]
                nombre_completo = f"{fila[2]} {fila[3]} {fila[4]}" # nombre paterno materno
                estatus = fila[9]
                turno = fila[10]
                
                cita_frame = ctk.CTkFrame(self.vista.frame_lista_citas, fg_color="transparent")
                cita_frame.pack(fill="x", pady=2)
                
                ctk.CTkLabel(cita_frame, text=curp, width=180, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(cita_frame, text=nombre_completo, width=250, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(cita_frame, text=str(turno), width=50).pack(side="left", padx=5)
                
                color = "green" if estatus == "Resuelto" else "orange"
                ctk.CTkLabel(cita_frame, text=estatus, width=100, text_color=color).pack(side="left", padx=5)
                
                # --- ¡AQUÍ ESTÁ LA LÓGICA DE CLIC! ---
                click_handler_cita = lambda e, c=curp, frame=cita_frame: self._seleccionar_cita(c, frame)
                
                cita_frame.bind("<Button-1>", click_handler_cita)
                for widget in cita_frame.winfo_children():
                    widget.bind("<Button-1>", click_handler_cita)
                
        except Exception as e:
            print(f"Error al buscar citas: {e}")
            ctk.CTkLabel(self.vista.frame_lista_citas, text="Error al realizar la búsqueda.").pack(pady=10)

    def _seleccionar_cita(self, curp, frame_widget):
        """
        Se llama al hacer clic en una cita de la lista.
        Resalta la fila seleccionada y guarda la CURP.
        """
        print(f"Cita seleccionada: CURP={curp}")
        
        # 1. Quitar el resaltado de la selección anterior (si existe)
        if self.frame_cita_seleccionado is not None:
            self.frame_cita_seleccionado.configure(fg_color="transparent")
            
        # 2. Guardar la nueva selección
        self.curp_seleccionada = curp
        self.frame_cita_seleccionado = frame_widget
        
        # 3. Resaltar la nueva selección
        self.frame_cita_seleccionado.configure(fg_color="gray25") # Color de resaltado

    # --- ESTAS SON LAS FUNCIONES NUEVAS, AHORA DENTRO DE LA CLASE ---
    def _eliminar_cita(self):
        """
        Elimina la cita que está actualmente seleccionada (self.curp_seleccionada).
        """
        if not self.curp_seleccionada:
            print("No hay ninguna cita seleccionada para eliminar.")
            # (Aquí iría un popup de error)
            return
            
        print(f"Intentando eliminar cita: {self.curp_seleccionada}")
        
        # (Aquí iría un popup de confirmación: "¿Estás seguro?")
        
        if self.cita_model.delete_by_curp(self.curp_seleccionada):
            print("¡Cita eliminada exitosamente!")
            # Limpiamos la selección
            self.curp_seleccionada = None
            self.frame_cita_seleccionado = None
            # Refrescamos la búsqueda actual para que desaparezca de la lista
            self._buscar_citas() 
        else:
            print("Error al eliminar la cita.")

    def _marcar_cita_resuelta(self):
        """
        Llama a la función genérica para cambiar el estatus a 'Resuelto'.
        """
        self._cambiar_estatus_cita("Resuelto")

    def _marcar_cita_pendiente(self):
        """
        Llama a la función genérica para cambiar el estatus a 'Pendiente'.
        """
        self._cambiar_estatus_cita("Pendiente")

    def _cambiar_estatus_cita(self, nuevo_estatus):
        """
        Función genérica para cambiar el estatus de la cita seleccionada.
        """
        if not self.curp_seleccionada:
            print(f"No hay ninguna cita seleccionada para marcar como {nuevo_estatus}.")
            return
            
        print(f"Marcando cita {self.curp_seleccionada} como {nuevo_estatus}...")
        
        if self.cita_model.actualizar_estatus(self.curp_seleccionada, nuevo_estatus):
            print("¡Estatus actualizado!")
            # Refrescamos la búsqueda para ver el cambio de color
            self._buscar_citas()
        else:
            print("Error al actualizar el estatus.")

    # --- Métodos Generales ---
    
    def _cerrar_sistema(self):
        """
        Cierra la ventana de administrador (y eventualmente toda la app).
        """
        print("Cerrando sistema...")
        self.vista.destroy()