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
        # Botones de la pestaña de modificación pública
        try:
            self.vista.btn_buscar_mod.configure(command=self._buscar_cita_mod)
            self.vista.btn_guardar_mod.configure(command=self._guardar_mod)
            # Al inicio, deshabilitamos el botón de guardar modificación hasta encontrar una cita
            self.vista.btn_guardar_mod.configure(state="disabled")
        except Exception:
            # En caso de que la vista aún no tenga los elementos (compatibilidad), ignorar
            pass
        
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
            # También actualizar el combo de la sección de modificación si existe
            try:
                self.vista.combo_municipio_mod.configure(values=nombres_municipios)
                if nombres_municipios:
                    self.vista.combo_municipio_mod.set(nombres_municipios[0])
            except Exception:
                pass
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

    # --- Funciones para la edición pública ---
    def _buscar_cita_mod(self):
        """Busca la cita por CURP y número de turno y carga los campos en la vista."""
        try:
            curp = self.vista.entry_curp_mod.get().strip().upper()
            turno_txt = self.vista.entry_turno_mod.get().strip()

            if not curp or not turno_txt:
                messagebox.showerror("Error de Validación", "Ingresa CURP y Número de Turno", parent=self.vista)
                return

            try:
                numero_turno = int(turno_txt)
            except ValueError:
                messagebox.showerror("Error de Validación", "El número de turno debe ser un entero.", parent=self.vista)
                return

            fila = self.cita_model.get_by_curp_and_turno(curp, numero_turno)
            if not fila:
                # No encontrada
                self.vista.lbl_mensaje_mod.configure(text="No se encontró la cita con esos datos.", text_color="red")
                # Deshabilitar guardado
                try:
                    self.vista.btn_guardar_mod.configure(state="disabled")
                except Exception:
                    pass
                return

            # La fila sigue el orden de la tabla Cita:
            # (curp_alumno, nombre_tutor, nombre_alumno, paterno_alumno, materno_alumno,
            # telefono_contacto, correo_contacto, nivel_educativo, asunto, estatus, numero_turno, id_municipio)
            (curp_alumno, nombre_tutor, nombre_alumno, paterno_alumno, materno_alumno,
             telefono_contacto, correo_contacto, nivel_educativo, asunto, estatus, numero_turno, id_municipio) = fila

            # Rellenar campos en la vista (asegurando que existen)
            try:
                self.vista.entry_nombre_tutor_mod.delete(0, 'end')
                self.vista.entry_nombre_tutor_mod.insert(0, nombre_tutor)

                self.vista.entry_nombre_alumno_mod.delete(0, 'end')
                self.vista.entry_nombre_alumno_mod.insert(0, nombre_alumno)

                self.vista.entry_paterno_alumno_mod.delete(0, 'end')
                self.vista.entry_paterno_alumno_mod.insert(0, paterno_alumno)

                self.vista.entry_materno_alumno_mod.delete(0, 'end')
                self.vista.entry_materno_alumno_mod.insert(0, materno_alumno)

                self.vista.entry_telefono_mod.delete(0, 'end')
                self.vista.entry_telefono_mod.insert(0, telefono_contacto or '')

                self.vista.entry_correo_mod.delete(0, 'end')
                self.vista.entry_correo_mod.insert(0, correo_contacto or '')

                # Nivel
                try:
                    self.vista.combo_nivel_mod.set(nivel_educativo)
                except Exception:
                    pass

                # Municipio: buscar el nombre a partir del id
                nombre_muni = None
                for nombre, id_m in self.mapa_municipios.items():
                    if id_m == id_municipio:
                        nombre_muni = nombre
                        break
                if nombre_muni:
                    try:
                        self.vista.combo_municipio_mod.set(nombre_muni)
                    except Exception:
                        pass

                # Asunto
                self.vista.entry_asunto_mod.delete('1.0', 'end')
                self.vista.entry_asunto_mod.insert('1.0', asunto or '')

                # Mensaje de éxito
                self.vista.lbl_mensaje_mod.configure(text=f"Cita encontrada. Estado: {estatus}.", text_color="green")

                # Habilitar botón guardar
                try:
                    self.vista.btn_guardar_mod.configure(state="normal")
                except Exception:
                    pass

            except Exception as e:
                messagebox.showerror("Error", f"Error cargando datos en la vista: {e}", parent=self.vista)

        except Exception as e:
            messagebox.showerror("Error inesperado", f"{e}", parent=self.vista)

    def _guardar_mod(self):
        """Guarda los cambios hechos desde la vista pública para una cita existente."""
        try:
            curp = self.vista.entry_curp_mod.get().strip().upper()
            turno_txt = self.vista.entry_turno_mod.get().strip()
            if not curp or not turno_txt:
                messagebox.showerror("Error de Validación", "Ingresa CURP y Número de Turno", parent=self.vista)
                return

            try:
                numero_turno = int(turno_txt)
            except ValueError:
                messagebox.showerror("Error de Validación", "El número de turno debe ser un entero.", parent=self.vista)
                return

            # Recolectar campos editables
            nombre_tutor = self.vista.entry_nombre_tutor_mod.get()
            nombre_alumno = self.vista.entry_nombre_alumno_mod.get()
            paterno_alumno = self.vista.entry_paterno_alumno_mod.get()
            materno_alumno = self.vista.entry_materno_alumno_mod.get()
            telefono = self.vista.entry_telefono_mod.get()
            correo = self.vista.entry_correo_mod.get()
            nivel = self.vista.combo_nivel_mod.get()
            asunto = self.vista.entry_asunto_mod.get('1.0', 'end-1c')

            nombre_municipio_sel = self.vista.combo_municipio_mod.get()
            id_municipio_sel = self.mapa_municipios.get(nombre_municipio_sel)

            if not all([curp, nombre_tutor, nombre_alumno, paterno_alumno, id_municipio_sel]):
                messagebox.showerror("Error de Validación", "Faltan campos obligatorios.", parent=self.vista)
                return

            # Crear objeto Cita con los datos nuevos
            cita = self.cita_model(
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

            exito, mensaje = cita.save(es_admin=False)
            if exito:
                messagebox.showinfo("Guardado", f"Cambios guardados. Número de turno: {mensaje}", parent=self.vista)
                # Deshabilitar boton guardar para evitar reenvíos
                try:
                    self.vista.btn_guardar_mod.configure(state="disabled")
                except Exception:
                    pass
            else:
                messagebox.showerror("Error al Guardar", mensaje, parent=self.vista)

        except Exception as e:
            messagebox.showerror("Error inesperado", f"{e}", parent=self.vista)