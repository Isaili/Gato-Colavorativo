import multiprocessing
from multiprocessing.managers import BaseManager
import time
import threading

class JuegoGato:
    def __init__(self):
        self.lock = multiprocessing.Lock()
        self.tablero = multiprocessing.Array('i', 9)  # Tablero 3x3 aplanado
        self.turno_actual = multiprocessing.Value('i', 1)  # 1 para X, 2 para O
        self.estado_juego = multiprocessing.Value('i', 0)  # 0: en juego, 1: ganador X, 2: ganador O, 3: empate
        self.jugadores_conectados = multiprocessing.Value('i', 0)
        self.reset()
    
    def reset(self):
        with self.lock:
            for i in range(9):
                self.tablero[i] = 0  # 0 representa vacío
            self.turno_actual.value = 1  # X comienza
            self.estado_juego.value = 0  # En juego
            print("El juego ha sido reiniciado")
    
    def obtener_tablero(self):
        with self.lock:
            return list(self.tablero)
    
    def obtener_turno(self):
        with self.lock:
            return self.turno_actual.value
    
    def obtener_estado(self):
        with self.lock:
            return self.estado_juego.value
    
    def registrar_conexion(self):
        with self.lock:
            self.jugadores_conectados.value += 1
            return self.jugadores_conectados.value
    
    def registrar_desconexion(self):
        with self.lock:
            if self.jugadores_conectados.value > 0:
                self.jugadores_conectados.value -= 1
            return self.jugadores_conectados.value
    
    def obtener_jugadores_conectados(self):
        with self.lock:
            return self.jugadores_conectados.value
    
    def solicitar_reinicio(self):
        with self.lock:
            if self.estado_juego.value != 0:  # Solo reiniciar si el juego ha terminado
                self.reset()
                return True
            return False
    
    def poner_pieza(self, posicion, jugador):
        with self.lock:
            # Verificar si el juego ya terminó
            if self.estado_juego.value != 0:
                return False, "El juego ya ha terminado"
            
            # Verificar si es el turno del jugador
            if jugador != self.turno_actual.value:
                return False, "No es tu turno"
            
            # Verificar si la posición es válida
            if not (0 <= posicion < 9):
                return False, "Posición fuera de rango"
            
            # Verificar si la posición está ocupada
            if self.tablero[posicion] != 0:
                return False, "Esa casilla ya está ocupada"
            
            # Realizar la jugada
            self.tablero[posicion] = jugador
            
            # Verificar si hay ganador
            if self._verificar_ganador():
                self.estado_juego.value = jugador
                print(f"¡Jugador {jugador} ha ganado!")
                return True, "¡Has ganado!"
            
            # Verificar si hay empate
            if self._verificar_empate():
                self.estado_juego.value = 3
                print("¡Empate!")
                return True, "¡Empate!"
            
            # Cambiar turno
            self.turno_actual.value = 3 - self.turno_actual.value  # Alterna entre 1 y 2
            return True, "Jugada realizada"
    
    def _verificar_ganador(self):
        # Líneas de verificación (filas, columnas y diagonales)
        lineas = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
            [0, 4, 8], [2, 4, 6]              # Diagonales
        ]
        
        for linea in lineas:
            if (self.tablero[linea[0]] != 0 and
                self.tablero[linea[0]] == self.tablero[linea[1]] == self.tablero[linea[2]]):
                return True
        return False
    
    def _verificar_empate(self):
        # Verificar si todas las casillas están ocupadas
        for i in range(9):
            if self.tablero[i] == 0:
                return False
        return True

class MonitorJuego(threading.Thread):
    def __init__(self, juego):
        super().__init__()
        self.juego = juego
        self.daemon = True
    
    def run(self):
        while True:
            try:
                estado_actual = self.juego.obtener_estado()
                jugadores = self.juego.obtener_jugadores_conectados()
                
                # Mostrar estado actual del servidor
                estado_str = "En juego"
                if estado_actual == 1:
                    estado_str = "Ganador: X"
                elif estado_actual == 2:
                    estado_str = "Ganador: O"
                elif estado_actual == 3:
                    estado_str = "Empate"
                
                print(f"\rEstado: {estado_str} | Jugadores conectados: {jugadores}", end="")
                
                # Esperar un poco antes de la siguiente actualización
                time.sleep(2)
            except Exception as e:
                print(f"\nError en el monitor: {e}")
                break

# Configurar y iniciar el servidor
def run_server():
    # Inicializar el juego
    juego = JuegoGato()
    
    # Configurar el BaseManager
    BaseManager.register('get_juego', callable=lambda: juego)
    manager = BaseManager(address=('localhost', 50000), authkey=b'gato')
    
    # Iniciar el servidor
    server = manager.get_server()
    print("Servidor iniciado en localhost:50000")
    print("Esperando jugadores...")
    
    # Iniciar monitor en segundo plano
    monitor = MonitorJuego(juego)
    monitor.start()
    
    # Iniciar el servidor (bloquea el hilo principal)
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("\nCerrando el servidor...")
    except Exception as e:
        print(f"\nError en el servidor: {e}")
    finally:
        print("Servidor cerrado")

if __name__ == "__main__":
    run_server()