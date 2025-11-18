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
        self.vista.btn_buscar_mod.configure(command=self._buscar_cita_modificar)
        
        # Cargar datos iniciales
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
            
            modo_modificar = (self.vista.btn_guardar_cita.cget("text") == "Guardar Cambios")

            # 2. Validaciones básicas
            if not all([curp, nombre_tutor, nombre_alumno, paterno_alumno, id_municipio_sel]):
                messagebox.showerror("Error de Validación", 
                                     "Los campos con * son obligatorios:\n- CURP\n- Nombre Tutor\n- Nombre Alumno\n- Paterno Alumno\n- Municipio",
                                     parent=self.vista)
                if modo_modificar:
                    self.vista.entry_curp.configure(state="disabled")
                return

            # 3. Nueva Regla de Negocio
            if not modo_modificar:
                if self.cita_model.check_pending(curp):
                    messagebox.showerror("Registro Bloqueado",
                                         "Ya existe una cita 'Pendiente' con esta CURP.\nNo puede registrar una nueva hasta que la anterior sea 'Resuelta'.",
                                         parent=self.vista)
                    self.vista.entry_curp.configure(state="normal")
                    return
            
            # 4. Crear el objeto Cita
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
                estatus="Pendiente" 
            )
            
            # 5. Guardar
            exito, mensaje = nueva_cita.save(es_admin=False)
            
            if exito:
                turno_asignado = mensaje # El modelo ahora SIEMPRE devuelve el turno
                
                if modo_modificar:
                    self.vista.lbl_mensaje_registrar.configure(
                        text=f"¡Cita {curp} actualizada con éxito!\nSu número de turno sigue siendo: {turno_asignado}",
                        text_color="green")
                else:
                    self.vista.lbl_mensaje_registrar.configure(
                        text=f"¡Cita registrada con éxito!\nSu número de turno es: {turno_asignado}",
                        text_color="green")

                self.vista.btn_guardar_cita.configure(state="disabled")
                self.vista.entry_curp.configure(state="disabled")
                
            else:
                messagebox.showerror("Error al Guardar", mensaje, parent=self.vista)
                if not modo_modificar:
                     self.vista.entry_curp.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}", parent=self.vista)
            # Manejo de error para re-habilitar la CURP si falla
            if self.vista.btn_guardar_cita.cget("text") != "Guardar Cambios":
                 self.vista.entry_curp.configure(state="normal")

    
    def _buscar_cita_modificar(self):
        """
        Busca la cita por CURP y Turno para poblar el formulario de modificación.
        """
        curp = self.vista.entry_curp_mod.get().upper()
        turno_str = self.vista.entry_turno_mod.get()
        
        if not curp or not turno_str:
            messagebox.showerror("Campos Vacíos", "Debe ingresar la CURP y el Número de Turno.", parent=self.vista)
            return
            
        try:
            turno = int(turno_str)
        except ValueError:
            messagebox.showerror("Dato Inválido", "El número de turno debe ser un número.", parent=self.vista)
            return
            
        cita_data = self.cita_model.get_by_curp_and_turno(curp, turno)
        
        if cita_data:
            print("Cita encontrada, poblando formulario...")
            # ¡Llama a la función que rellena el formulario de la Pestaña 1!
            self._poblar_formulario(cita_data)
            # ¡Cambia a la Pestaña 1!
            self.vista.tabs.set("Registrar Cita")
        else:
            messagebox.showerror("No Encontrada", "No se encontró ninguna cita con esa CURP y Número de Turno.", parent=self.vista)

    def _poblar_formulario(self, cita_dict):
        """
        Rellena el formulario de "Registrar Cita" (PESTAÑA 1) con los datos
        de la cita encontrada para modificarla.
        """
        # Habilitar campos para limpiarlos
        self.vista.entry_curp.configure(state="normal")
        self.vista.btn_guardar_cita.configure(state="normal")
        
        # Limpiar campos (¡ESTOS SON LOS NOMBRES CORRECTOS!)
        self.vista.entry_curp.delete(0, "end")
        self.vista.entry_nombre_alumno.delete(0, "end")
        self.vista.entry_paterno_alumno.delete(0, "end")
        self.vista.entry_materno_alumno.delete(0, "end")
        self.vista.entry_nombre_tutor.delete(0, "end")
        self.vista.entry_telefono.delete(0, "end")
        self.vista.entry_correo.delete(0, "end")
        self.vista.entry_asunto.delete("1.0", "end")
        self.vista.lbl_mensaje_registrar.configure(text="")
        
        # Rellenar campos (¡ESTOS SON LOS NOMBRES CORRECTOS!)
        self.vista.entry_curp.insert(0, cita_dict.get("curp_alumno", ""))
        self.vista.entry_nombre_alumno.insert(0, cita_dict.get("nombre_alumno", ""))
        self.vista.entry_paterno_alumno.insert(0, cita_dict.get("paterno_alumno", ""))
        self.vista.entry_materno_alumno.insert(0, cita_dict.get("materno_alumno", ""))
        self.vista.entry_nombre_tutor.insert(0, cita_dict.get("nombre_tutor", ""))
        self.vista.entry_telefono.insert(0, cita_dict.get("telefono_contacto", ""))
        self.vista.entry_correo.insert(0, cita_dict.get("correo_contacto", ""))
        self.vista.entry_asunto.insert("1.0", cita_dict.get("asunto", ""))
        
        self.vista.combo_nivel.set(cita_dict.get("nivel_educativo", "Primaria"))
        
        id_muni = cita_dict.get("id_municipio")
        nombre_muni_encontrado = ""
        for nombre, id_val in self.mapa_municipios.items():
            if id_val == id_muni:
                nombre_muni_encontrado = nombre
                break
        self.vista.combo_municipio.set(nombre_muni_encontrado)
        
        self.vista.btn_guardar_cita.configure(text="Guardar Cambios")
        self.vista.entry_curp.configure(state="disabled")