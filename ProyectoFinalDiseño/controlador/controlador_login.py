# controlador/controlador_login.py
from modelo.usuario_model import Usuario
from vista.vista_login import VistaLogin 
from vista.vista_admin import VistaAdmin
from controlador.controlador_admin import ControladorAdmin
class ControladorLogin:
    
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        
        # Conectamos el botón de la vista a un método de este controlador
        self.vista.btn_ingresar.configure(command=self._handle_login)

    def _handle_login(self):
        """
        Se llama cuando el usuario hace clic en 'Ingresar'.
        """
        # 1. Limpiamos cualquier error previo
        self.vista.limpiar_error()
        
        # 2. Obtenemos los datos de la Vista
        username, password = self.vista.obtener_datos()

        # 3. Validamos que no estén vacíos
        if not username or not password:
            self.vista.mostrar_error("Usuario y contraseña no pueden estar vacíos.")
            return

        # 4. Enviamos los datos al Modelo para verificar
        if self.modelo.verificar_credenciales(username, password):
            # 5. Si es correcto:
            print("¡Login exitoso!")
            # Cerramos la ventana de login
            self.vista.destruir_ventana()
            
            # (Aquí es donde abriremos la ventana principal de admin)
            self._abrir_ventana_admin()
        else:
            # 6. Si es incorrecto:
            print("Login fallido.")
            # Le decimos a la Vista que muestre un error
            self.vista.mostrar_error("Usuario o contraseña incorrectos.")

    def _abrir_ventana_admin(self):
        """Abre la ventana de administración, crea su controlador y lanza su bucle."""
        print("Abriendo la VistaAdmin...")

        # 1. Creamos la nueva ventana de Admin
        self.vista_admin = VistaAdmin()

        # 2. Creamos su controlador
        self.controlador_admin = ControladorAdmin(self.vista_admin)

        # 3. Iniciamos el bucle de la nueva ventana
        self.vista_admin.mainloop()