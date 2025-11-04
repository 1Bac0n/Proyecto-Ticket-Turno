# vista/vista_login.py
import customtkinter as ctk

# Configuramos el tema de la aplicación
ctk.set_appearance_mode("dark")  # O "light"
ctk.set_default_color_theme("blue") # O "green", "dark-blue"

class VistaLogin(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        # --- Configuración de la Ventana Principal ---
        self.title("Sistema de Turnos - Login")
        self.geometry("400x500") # Tamaño de la ventana (ancho x alto)
        self.resizable(False, False)
        
        # --- Frame Principal ---
        # Un frame para centrar todo el contenido
        frame_principal = ctk.CTkFrame(self)
        frame_principal.pack(padx=20, pady=20, fill="both", expand=True)

        # --- Widgets de la Vista ---

        # Título
        self.lbl_titulo = ctk.CTkLabel(frame_principal, 
                                       text="Acceso de Administrador", 
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 20)) # (padding_top, padding_bottom)

        # Campo de Usuario
        self.lbl_usuario = ctk.CTkLabel(frame_principal, 
                                        text="Usuario:",
                                        font=ctk.CTkFont(size=14))
        self.lbl_usuario.pack(pady=(20, 5))
        
        self.entry_usuario = ctk.CTkEntry(frame_principal, 
                                          width=250, 
                                          placeholder_text="admin")
        self.entry_usuario.pack(pady=(0, 10))

        # Campo de Contraseña
        self.lbl_password = ctk.CTkLabel(frame_principal, 
                                         text="Contraseña:",
                                         font=ctk.CTkFont(size=14))
        self.lbl_password.pack(pady=(10, 5))
        
        self.entry_password = ctk.CTkEntry(frame_principal, 
                                           width=250, 
                                           placeholder_text="admin123",
                                           show="*") # Oculta la contraseña
        self.entry_password.pack(pady=(0, 20))

        # Botón de Ingresar
        self.btn_ingresar = ctk.CTkButton(frame_principal, 
                                          text="Ingresar", 
                                          width=250,
                                          font=ctk.CTkFont(weight="bold"))
        self.btn_ingresar.pack(pady=(20, 10))

        # Mensaje de error (inicialmente vacío)
        self.lbl_mensaje = ctk.CTkLabel(frame_principal, 
                                        text="", 
                                        text_color="red")
        self.lbl_mensaje.pack(pady=(10, 20))
        
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en la interfaz."""
        self.lbl_mensaje.configure(text=mensaje)

    def limpiar_error(self):
        """Limpia el mensaje de error."""
        self.lbl_mensaje.configure(text="")

    def obtener_datos(self):
        """Devuelve el usuario y la contraseña ingresados."""
        return self.entry_usuario.get(), self.entry_password.get()

    def destruir_ventana(self):
        """Cierra esta ventana de login."""
        self.destroy()

# --- Bloque para probar la vista ---
if __name__ == "__main__":
    app = VistaLogin()
    app.mainloop()