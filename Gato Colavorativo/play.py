import multiprocessing
from multiprocessing.managers import BaseManager
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading

class JugadorGatoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego del Gato Colaborativo")
        self.root.resizable(False, False)
        
        # Variables del juego
        self.conectado = False
        self.nombre = ""
        self.numero_jugador = 0
        self.simbolo = ""
        self.juego = None
        self.manager = None
        
        # Crear frames
        self.frame_conexion = tk.Frame(root, padx=20, pady=20)
        self.frame_juego = tk.Frame(root, padx=20, pady=20)
        
        # Mostrar frame de conexión
        self.setup_conexion_ui()
        self.frame_conexion.pack()
    
    def setup_conexion_ui(self):
        tk.Label(self.frame_conexion, text="Conexión al Juego", font=('Arial', 16)).pack(pady=10)
        
        # Nombre del jugador
        tk.Label(self.frame_conexion, text="Nombre:").pack(anchor='w')
        self.entrada_nombre = tk.Entry(self.frame_conexion, width=30)
        self.entrada_nombre.pack(pady=5, fill='x')
        
        # Selección de jugador
        tk.Label(self.frame_conexion, text="Selecciona jugador:").pack(anchor='w', pady=(10, 0))
        self.var_jugador = tk.IntVar(value=1)
        tk.Radiobutton(self.frame_conexion, text="Jugador 1 (X)", variable=self.var_jugador, value=1).pack(anchor='w')
        tk.Radiobutton(self.frame_conexion, text="Jugador 2 (O)", variable=self.var_jugador, value=2).pack(anchor='w')
        
        # Botón de conexión
        tk.Button(self.frame_conexion, text="Conectar", command=self.conectar_al_servidor).pack(pady=20)
        
        # Estado de conexión
        self.label_estado = tk.Label(self.frame_conexion, text="No conectado", fg="red")
        self.label_estado.pack()
    
    def setup_juego_ui(self):
        # Limpiar frame anterior
        for widget in self.frame_juego.winfo_children():
            widget.destroy()
        
        # Información del jugador
        info_frame = tk.Frame(self.frame_juego)
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(info_frame, text=f"Jugador: {self.nombre} ({self.simbolo})", font=('Arial', 12)).pack(side='left')
        self.label_turno = tk.Label(info_frame, text="", font=('Arial', 12))
        self.label_turno.pack(side='right')
        
        # Tablero de juego
        self.botones = []
        tablero_frame = tk.Frame(self.frame_juego)
        tablero_frame.pack(pady=10)
        
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                btn = tk.Button(tablero_frame, text=" ", font=('Arial', 24, 'bold'), 
                               width=3, height=1, command=lambda pos=idx: self.hacer_jugada(pos))
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.botones.append(btn)
        
        # Estado del juego
        self.label_estado_juego = tk.Label(self.frame_juego, text="", font=('Arial', 12))
        self.label_estado_juego.pack(pady=10)
        
        # Botón para reiniciar
        self.btn_reiniciar = tk.Button(self.frame_juego, text="Nueva Partida", state='disabled', 
                                      command=self.esperar_reinicio)
        self.btn_reiniciar.pack(pady=5)
        
        # Botón para salir
        tk.Button(self.frame_juego, text="Salir", command=self.salir).pack(pady=5)
    
    def conectar_al_servidor(self):
        self.nombre = self.entrada_nombre.get().strip()
        self.numero_jugador = self.var_jugador.get()
        self.simbolo = 'X' if self.numero_jugador == 1 else 'O'
        
        if not self.nombre:
            messagebox.showerror("Error", "Por favor, ingresa tu nombre")
            return
        
        try:
            # Conectar al servidor
            self.manager = BaseManager(address=('localhost', 50000), authkey=b'gato')
            self.manager.register('get_juego')
            self.manager.connect()
            
            # Es importante asegurar que este método existe en el servidor
            self.juego = self.manager.get_juego()
            self.conectado = True
            
            # Actualizar UI
            self.label_estado.config(text="Conectado al servidor", fg="green")
            messagebox.showinfo("Conexión exitosa", 
                               f"Te has conectado como Jugador {self.numero_jugador} ({self.simbolo})")
            
            # Cambiar a la interfaz del juego
            self.frame_conexion.pack_forget()
            self.setup_juego_ui()
            self.frame_juego.pack()
            
            # Iniciar hilo para actualizar el juego
            self.running = True
            self.update_thread = threading.Thread(target=self.actualizar_juego)
            self.update_thread.daemon = True
            self.update_thread.start()
            
        except ConnectionRefusedError:
            messagebox.showerror("Error de conexión", 
                               "No se pudo conectar al servidor. Asegúrate de que esté en ejecución.")
        except AttributeError as e:
            messagebox.showerror("Error de conexión", 
                               f"Error al obtener el juego: {str(e)}\nAsegúrate de que el servidor esté configurado correctamente.")
        except Exception as e:
            messagebox.showerror("Error de conexión", 
                               f"Error desconocido: {str(e)}")
    
    def actualizar_juego(self):
        while self.running:
            try:
                if not self.conectado or not self.juego:
                    break
                
                tablero = self.juego.obtener_tablero()
                estado = self.juego.obtener_estado()
                turno = self.juego.obtener_turno()
                
                # Actualizar tablero
                for i, valor in enumerate(tablero):
                    texto = " "
                    if valor == 1:
                        texto = "X"
                    elif valor == 2:
                        texto = "O"
                    
                    # Evitar errores al cerrar la ventana
                    if hasattr(self, 'botones') and i < len(self.botones):
                        btn_texto_actual = self.botones[i]["text"]
                        if btn_texto_actual != texto:
                            self.root.after(0, lambda b=self.botones[i], t=texto: b.config(text=t))
                
                # Actualizar estado del juego
                if estado == 0:
                    estado_texto = f"Turno de {'X' if turno == 1 else 'O'}"
                    self.root.after(0, lambda t=estado_texto: self.label_estado_juego.config(text=t))
                    
                    # Habilitar/deshabilitar botones según el turno
                    estado_botones = 'normal' if turno == self.numero_jugador else 'disabled'
                    for btn in self.botones:
                        if btn['text'] == " ":  # Solo habilitar casillas vacías
                            self.root.after(0, lambda b=btn, s=estado_botones: b.config(state=s))
                    
                    turno_texto = "Tu turno" if turno == self.numero_jugador else "Esperando al otro jugador"
                    turno_color = "green" if turno == self.numero_jugador else "red"
                    self.root.after(0, lambda t=turno_texto, c=turno_color: self.label_turno.config(text=t, fg=c))
                    
                    self.root.after(0, lambda: self.btn_reiniciar.config(state='disabled'))
                else:
                    # Juego terminado - definir el texto del resultado
                    if estado == 1:
                        estado_texto = "¡Jugador X ha ganado!"
                    elif estado == 2:
                        estado_texto = "¡Jugador O ha ganado!"
                    elif estado == 3:
                        estado_texto = "¡Empate!"
                    else:
                        estado_texto = "Estado desconocido"
                    
                    # Actualizar la interfaz de usuario con el resultado
                    self.root.after(0, lambda t=estado_texto: self.label_estado_juego.config(text=t))
                    
                    # Deshabilitar todos los botones
                    for btn in self.botones:
                        self.root.after(0, lambda b=btn: b.config(state='disabled'))
                    
                    # Habilitar botón de reinicio
                    self.root.after(0, lambda: self.btn_reiniciar.config(state='normal'))
                
                time.sleep(0.5)  # Actualizar cada medio segundo
                
            except Exception as e:
                print(f"Error en la actualización: {e}")
                self.conectado = False
                self.root.after(0, lambda: messagebox.showerror("Error de conexión", 
                                   "Se ha perdido la conexión con el servidor"))
                self.root.after(0, self.volver_a_conexion)
                break
    
    def hacer_jugada(self, posicion):
        try:
            if not self.juego:
                messagebox.showerror("Error", "No hay conexión con el juego")
                return
                
            exito, mensaje = self.juego.poner_pieza(posicion, self.numero_jugador)
            if not exito:
                messagebox.showinfo("Jugada inválida", mensaje)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la jugada: {str(e)}")
    
    def esperar_reinicio(self):
        # Verificar con el usuario si desea esperar reinicio
        respuesta = messagebox.askyesno("Nueva partida", 
                                        "¿Quieres esperar a que se inicie una nueva partida?")
        if respuesta:
            try:
                self.juego.solicitar_reinicio()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reiniciar el juego: {str(e)}")
        else:
            self.salir()
    
    def volver_a_conexion(self):
        self.frame_juego.pack_forget()
        self.frame_conexion.pack()
        self.label_estado.config(text="Desconectado", fg="red")
    
    def salir(self):
        self.running = False
        self.root.destroy()

def run_client_gui():
    root = tk.Tk()
    app = JugadorGatoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_client_gui()