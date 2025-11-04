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
        
        self.mapa_municipios = {} 
        
        self.vista.btn_guardar_cita.configure(command=self._guardar_cita)
        # Conectar botones de la pestaña de modificación pública (si existen)
        try:
            self.vista.btn_buscar_mod.configure(command=self._buscar_cita_mod)
            self.vista.btn_guardar_mod.configure(command=self._guardar_mod)
            # Al inicio, deshabilitamos el botón de guardar modificación hasta encontrar una cita
            self.vista.btn_guardar_mod.configure(state="disabled")
        except Exception:
            # Si la vista no tiene aún esos widgets, no hacemos nada
            pass
        
        self._cargar_municipios()

    def _cargar_municipios(self):
        """
        Obtiene los municipios del modelo y los pone en el ComboBox.
        """
        try:
            municipios_tuplas = self.municipio_model.get_all()
            
            nombres_municipios = []
            for id_muni, nombre in municipios_tuplas:
                nombres_municipios.append(nombre)
                self.mapa_municipios[nombre] = id_muni
            
            self.vista.combo_municipio.configure(values=nombres_municipios)
            # Si la vista tiene el combo de modificación, actualizarlo también
            try:
                self.vista.combo_municipio_mod.configure(values=nombres_municipios)
                if nombres_municipios:
                    self.vista.combo_municipio_mod.set(nombres_municipios[0])
            except Exception:
                pass
            if nombres_municipios:
                self.vista.combo_municipio.set(nombres_municipios[0])
            
        except Exception as e:
            print(f"Error cargando municipios: {e}")
            self.vista.combo_municipio.configure(values=["Error al cargar"])

    def _guardar_cita(self):
        """
        Toma todos los datos del formulario, los valida y los guarda
        (ya sea para crear una NUEVA cita o ACTUALIZAR una existente).
        """
        try:
            self.vista.entry_curp.configure(state="normal")
            
            # 1. Recolectar todos los datos de la vista
            curp = self.vista.entry_curp.get().upper()
            nombre_tutor = self.vista.entry_nombre_tutor.get()
            nombre_alumno = self.vista.entry_nombre_alumno.get()
            paterno_alumno = self.vista.entry_paterno_alumno.get()
            materno_alumno = self.vista.entry_materno_alumno.get()
            telefono = self.vista.entry_telefono.get()
            correo = self.vista.entry_correo.get()
            nivel = self.vista.combo_nivel.get()
            asunto = self.vista.entry_asunto.get("1.0", "end-1c")
            
            nombre_municipio_sel = self.vista.combo_municipio.get()
            id_municipio_sel = self.mapa_municipios.get(nombre_municipio_sel)
            
            # Verificamos la intención del usuario
            modo_modificar = (self.vista.btn_guardar_cita.cget("text") == "Guardar Cambios")

            # 2. Validaciones básicas
            if not all([curp, nombre_tutor, nombre_alumno, paterno_alumno, id_municipio_sel]):
                messagebox.showerror("Error de Validación", 
                                     "Los campos con * son obligatorios:\n- CURP\n- Nombre Tutor\n- Nombre Alumno\n- Paterno Alumno\n- Municipio",
                                     parent=self.vista)
                # Re-deshabilitar CURP si estábamos modificando
                if modo_modificar:
                    self.vista.entry_curp.configure(state="disabled")
                return

            # --- ¡¡AQUÍ ESTÁ LA NUEVA REGLA DE NEGOCIO!! ---
            # Si NO estamos en modo modificar (o sea, es un registro nuevo)
            if not modo_modificar:
                # Verificamos si ya hay una cita pendiente con esa CURP
                if self.cita_model.check_pending(curp):
                    messagebox.showerror("Registro Bloqueado",
                                         "Ya existe una cita 'Pendiente' con esta CURP.\nNo puede registrar una nueva hasta que la anterior sea 'Resuelta'.",
                                         parent=self.vista)
                    # Dejamos la CURP editable
                    self.vista.entry_curp.configure(state="normal")
                    return
            # --- FIN DE LA NUEVA REGLA ---

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
                asunto=asunto,
                # Si es admin, puede que quiera cambiar el estatus,
                # pero el público siempre la pone 'Pendiente' al guardar.
                estatus="Pendiente" 
            )
            
            # 4. Guardar (El modelo Cita se encarga de validar CURP y asignar turno)
            exito, mensaje = nueva_cita.save(es_admin=False)
            
            if exito:
                # ¡Éxito!
                turno_asignado = mensaje # El modelo ahora SIEMPRE devuelve el turno
                
                if modo_modificar:
                    # Fue una ACTUALIZACIÓN
                    self.vista.lbl_mensaje_registrar.configure(
                        text=f"¡Cita {curp} actualizada con éxito!\nSu número de turno sigue siendo: {turno_asignado}",
                        text_color="green")
                else:
                    # Fue un REGISTRO NUEVO
                    self.vista.lbl_mensaje_registrar.configure(
                        text=f"¡Cita registrada con éxito!\nSu número de turno es: {turno_asignado}",
                        text_color="green")

                self.vista.btn_guardar_cita.configure(state="disabled")
                self.vista.entry_curp.configure(state="disabled")
                
            else:
                # Error (Ej. CURP inválida, BD, etc.)
                messagebox.showerror("Error al Guardar", mensaje, parent=self.vista)
                # Si falló, volvemos a habilitar la CURP (si no estaba en modo "Guardar Cambios")
                if not modo_modificar:
                     self.vista.entry_curp.configure(state="normal")

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

            # Mostrar búsqueda en la UI para depuración
            try:
                self.vista.lbl_mensaje_mod.configure(text=f"Buscando CURP={curp} Turno={numero_turno}", text_color="black")
            except Exception:
                pass

            fila = self.cita_model.get_by_curp_and_turno(curp, numero_turno)
            print(f"DEBUG: buscar_cita_mod -> CURP={curp}, turno={numero_turno}, fila={fila}")

            if not fila:
                # No encontrada
                try:
                    self.vista.lbl_mensaje_mod.configure(text="No se encontró la cita con esos datos.", text_color="red")
                except Exception:
                    pass
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
                try:
                    self.vista.lbl_mensaje_mod.configure(text=f"Cita encontrada. Estado: {estatus}.", text_color="green")
                except Exception:
                    pass

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

            # Asegurar que actualizamos la cita correcta (CURP + número de turno)
            cita.numero_turno = numero_turno

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