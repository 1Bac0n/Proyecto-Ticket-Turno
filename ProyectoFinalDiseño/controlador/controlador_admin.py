# controlador/controlador_admin.py
import customtkinter as ctk
from modelo.municipio_model import Municipio

class ControladorAdmin:
    
    def __init__(self, vista_admin):
        self.vista = vista_admin
        self.municipio_model = Municipio # Acceso al modelo de Municipio
        
        # --- Configurar listeners (comandos) de los botones ---
        
        # 1. Pestaña de Municipios (Catálogo)
        self.vista.btn_guardar_muni.configure(command=self._guardar_municipio)
        self.vista.btn_eliminar_muni.configure(command=self._eliminar_municipio)
        self.vista.btn_nuevo_muni.configure(command=self._limpiar_form_municipio)
        
        # 2. Botón de Cerrar Sistema
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
            # Limpiar widgets anteriores del frame
            for widget in self.vista.frame_lista_municipios.winfo_children():
                widget.destroy()
            
            # Limpiar el diccionario de labels
            self.vista.labels_municipios = {}

            municipios = self.municipio_model.get_all()
            
            if municipios:
                # Creamos una cabecera
                header_frame = ctk.CTkFrame(self.vista.frame_lista_municipios, fg_color="gray20")
                header_frame.pack(fill="x", pady=(0, 5))
                ctk.CTkLabel(header_frame, text="ID", width=40, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
                ctk.CTkLabel(header_frame, text="Nombre", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

                # Creamos una etiqueta por cada municipio
                for muni in municipios:
                    id_muni = muni[0]
                    nombre_muni = muni[1]
                    
                    muni_frame = ctk.CTkFrame(self.vista.frame_lista_municipios, fg_color="transparent")
                    muni_frame.pack(fill="x", pady=2)
                    
                    label_id = ctk.CTkLabel(muni_frame, text=f"{id_muni}", width=40)
                    label_id.pack(side="left", padx=10)
                    
                    label_nombre = ctk.CTkLabel(muni_frame, text=f"{nombre_muni}", anchor="w")
                    label_nombre.pack(side="left", padx=10, fill="x")
                    
                    # --- LA MAGIA (Hacer clic) ---
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
        Toma los datos del formulario de municipios y los manda al modelo
        para CREAR o ACTUALIZAR. (¡ESTA ES LA VERSIÓN NUEVA!)
        """
        nombre = self.vista.entry_nombre_muni.get()
        
        self.vista.entry_id_muni.configure(state="normal")
        id_muni = self.vista.entry_id_muni.get()
        self.vista.entry_id_muni.configure(state="disabled")

        if not nombre:
            print("El nombre no puede estar vacío.")
            return

        # Decidimos si es CREAR (id vacío) o ACTUALIZAR (id con número)
        if id_muni:
            # --- Lógica de ACTUALIZAR ---
            print(f"Actualizando municipio ID: {id_muni}")
            muni_a_actualizar = self.municipio_model(id_municipio=int(id_muni), nombre=nombre)
            exito = muni_a_actualizar.save()
        else:
            # --- Lógica de CREAR ---
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
        (¡ESTA ES LA VERSIÓN NUEVA!)
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

    # --- Métodos Generales ---
    
    def _cerrar_sistema(self):
        """
        Cierra la ventana de administrador (y eventualmente toda la app).
        """
        print("Cerrando sistema...")
        self.vista.destroy()