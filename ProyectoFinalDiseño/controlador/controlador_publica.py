# controlador/controlador_publica.py
from modelo.municipio_model import Municipio
from modelo.cita_model import Cita
# Importamos la librería de pop-ups
from tkinter import messagebox 

class ControladorPublica:
    
    def __init__(self, vista_publica):
        self.vista = vista_publica
        self.municipio_model = Municipio
        self.cita_model = Cita
        
        # Guardamos los municipios (id -> nombre)
        self.mapa_municipios = {} 
        
        # Conectar botones
        self.vista.btn_guardar_cita.configure(command=self._guardar_cita)
        
        # Cargar datos iniciales
        self._cargar_municipios()

    def _cargar_municipios(self):
        """
        Obtiene los municipios del modelo y los pone en el ComboBox.
        """
        try:
            municipios_tuplas = self.municipio_model.get_all() # [(1, 'Saltillo'), (2, 'Ramos')]
            
            nombres_municipios = []
            for id_muni, nombre in municipios_tuplas:
                nombres_municipios.append(nombre)
                self.mapa_municipios[nombre] = id_muni # Guardamos el ID
            
            # Actualizamos el ComboBox en la vista
            self.vista.combo_municipio.configure(values=nombres_municipios)
            if nombres_municipios:
                self.vista.combo_municipio.set(nombres_municipios[0]) # Seleccionar el primero
            
        except Exception as e:
            print(f"Error cargando municipios: {e}")
            self.vista.combo_municipio.configure(values=["Error al cargar"])

    def _guardar_cita(self):
        """
        Toma todos los datos del formulario, los valida y los guarda.
        """
        try:
            # 1. Recolectar todos los datos de la vista
            curp = self.vista.entry_curp.get().upper()
            nombre_tutor = self.vista.entry_nombre_tutor.get()
            nombre_alumno = self.vista.entry_nombre_alumno.get()
            paterno_alumno = self.vista.entry_paterno_alumno.get()
            materno_alumno = self.vista.entry_materno_alumno.get()
            telefono = self.vista.entry_telefono.get()
            correo = self.vista.entry_correo.get()
            nivel = self.vista.combo_nivel.get()
            asunto = self.vista.entry_asunto.get("1.0", "end-1c") # Obtener texto del Textbox
            
            # Obtener ID del municipio desde el mapa que creamos
            nombre_municipio_sel = self.vista.combo_municipio.get()
            id_municipio_sel = self.mapa_municipios.get(nombre_municipio_sel)

            # 2. Validaciones básicas
            if not all([curp, nombre_tutor, nombre_alumno, paterno_alumno, id_municipio_sel]):
                messagebox.showerror("Error de Validación", 
                                     "Los campos con * son obligatorios:\n- CURP\n- Nombre Tutor\n- Nombre Alumno\n- Paterno Alumno\n- Municipio",
                                     parent=self.vista)
                return

            # 3. Crear el objeto Cita
            nueva_cita = self.cita_model(
                curp_alumno=curp,
                nombre_tutor=nombre_tutor,
                nombre_alumno=nombre_alumno,
                paterno_alumno=paterno_alumno,
                materno_alumno=materno_alumno,
                id_municipio=id_municipio_sel,
                telefono_contacto=telefono,
                correo_contacto=correo,
                nivel_educativo=nivel,
                asunto=asunto
            )
            
            # 4. Guardar (El modelo Cita se encarga de validar CURP y asignar turno)
            exito, mensaje = nueva_cita.save(es_admin=False)
            
            if exito:
                # ¡Éxito! Mostramos el número de turno (comprobante)
                turno_asignado = mensaje
                self.vista.lbl_mensaje_registrar.configure(
                    text=f"¡Cita registrada con éxito!\nSu número de turno es: {turno_asignado}",
                    text_color="green")
                # (Opcional: deshabilitar el botón para no registrar dos veces)
                self.vista.btn_guardar_cita.configure(state="disabled")
            else:
                # Error (Ej. CURP inválida, BD, etc.)
                messagebox.showerror("Error al Guardar", mensaje, parent=self.vista)

        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}", parent=self.vista)