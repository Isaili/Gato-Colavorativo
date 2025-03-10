<h1 align="center">Gato Colavorativo! 👁️</h1>

## Breve Descripción del Juego:
El juego Gato Colaborativo es una implementación del clásico juego de tres en línea (Tic-Tac-Toe) que permite jugar entre dos jugadores utilizando procesos concurrentes en Python. Los jugadores alternan turnos para colocar sus piezas (X y O) en un tablero de 3x3. El juego termina cuando un jugador consigue alinear tres de sus piezas en fila, columna o diagonal, o si todas las casillas están ocupadas sin que haya un ganador (empate).

---

### 🛠 Arquitectura del Proyecto:
El diseño del proyecto sigue una estructura basada en procesos concurrentes usando la librería **multiprocessing** para garantizar que los jugadores operen de manera independiente y el servidor administre correctamente el flujo del juego y la sincronización.

**Estructura General del Proyecto:**
```bash
tinaco2/
  ├── 📁 Gato Colavorativo   # Punto de entrada
    ├── 🗍 Server.py   # L Servidor de contexto, gestiona el estado global del juego.
    ├── 🗍 jugadores.py    # ugadores concurrentes, interactúan con el servidor.
  ├── 🗍 README.md    # Documentación
```

1. **Servidor de Contexto** (server.py):
  El servidor es el proceso central que maneja el estado del juego y coordina las jugadas. Utiliza un BaseManager para permitir que otros procesos (jugadores) interactúen con los datos del juego (tablero, turno, etc.) de manera segura y eficiente.

2. **jugadores**(jugadores.py):
  - Los jugadores son procesos independientes que se conectan al servidor para hacer jugadas y consultar el estado del juego. Cada jugador toma su turno, realiza una jugada y luego espera su siguiente turno.
    
3. **multiprocessing.Manager**:
  -  **Propósito:** Un **Manager** permite crear objetos compartidos entre procesos, como variables, listas o diccionarios.
---
    
  ## 🖍 Primitivas de Sincronización Utilizadas:
  **✨Lock:**

  **Uso:** El **Lock** se utiliza para asegurar que solo un jugador pueda realizar una jugada a la vez. Esto previene condiciones de carrera donde dos jugadores pudieran intentar modificar el tablero al mismo tiempo.
  
  **Justificación:** El acceso concurrente a las jugadas podría generar inconsistencias en el tablero, por lo que el Lock garantiza que las jugadas se realicen en orden, de forma secuencial.
  
  **🧨BaseManager:**

  **Uso:** El **BaseManager** se utiliza para crear y gestionar objetos compartidos entre los procesos (jugadores) y el servidor. En este caso, se registra la clase JuegoGato que contiene el tablero, los turnos y el estado del juego.
  
  **Justificación:** El **BaseManager** facilita la comunicación entre los procesos sin la necesidad de crear y gestionar manualmente los objetos compartidos. Los procesos pueden acceder de manera transparente al estado del juego, lo que simplifica la arquitectura del sistema.

 ---
  ## 🎫 Métodos Expuestos en el Juego:

**🎇poner_pieza(posicion, jugador)**

Este método permite que un jugador coloque su pieza (X o O) en el tablero. Verifica si la posición es válida y si el turno es correcto. Luego, cambia el turno al otro jugador.

**🖍parametros**

 **Posicion:** La casilla donde el jugador desea colocar su pieza (índice 0-8).
 
**jugador:** El jugador que realiza la jugada (0 para "X", 1 para "O").

**🎇checar_ganador()**

Verifica si hay un ganador después de cada jugada. Revisa las combinaciones ganadoras (filas, columnas, diagonales) y determina si alguien ha ganado o si el juego ha terminado en empate.

**🖍Retorno** Devuelve **True** si hay un ganador, o si el juego ha terminado en empate, y actualiza el estado del juego (puede ser "X", "O", o "empate").

---

#### 🔒 Casos Límite y Cómo se Manejan:
1. **Empate:**:
  - El juego puede terminar en empate si todas las casillas están llenas y no hay ganador.
  - **Solución:** Si todas las casillas están ocupadas y no se ha encontrado un ganador, el estado del juego se marca como "empate".

2. **Abandono de Jugador:**:
  - Si uno de los jugadores abandona el juego (por ejemplo, finaliza el proceso del jugador), el juego se detendrá y se puede definir una política para manejar la situación.
  - **Solución:** Este caso no se maneja directamente en la lógica actual, pero se podría agregar un chequeo para detectar procesos muertos o desconectados y declarar automáticamente al jugador restante como ganador o el juego como inconcluso.
    
3. **Jugada Inválida:**:
  - Si un jugador intenta colocar una pieza en una casilla ocupada o fuera de los límites del tablero, la jugada es rechazada.
  - **Solución:** Se notifica al jugador que la jugada es inválida y se le solicita realizar una nueva jugada.
  
---

#### 🏷 Justificación de las Decisiones de Diseño:
1. Uso de **BaseManager**:
  - **Justificación:** Usamos **BaseManager** para gestionar los objetos compartidos entre los procesos (servidor y jugadores). Esta clase proporciona un mecanismo sencillo para compartir el estado del juego (tablero, turno, ganador) entre varios procesos de manera eficiente y sin complicaciones adicionales. No se necesitan mecanismos complejos de IPC (comunicación entre procesos) cuando BaseManager ya proporciona esta funcionalidad de forma directa.
 

2. Uso de **Lock:**:
  - **Justificación:** La sincronización es crítica en un juego de dos jugadores donde ambos procesos intentan modificar el estado del juego. El Lock garantiza que solo un jugador realice su jugada en un momento dado, evitando condiciones de carrera y garantizando que el estado del juego sea consistente.

    
3. **Manejo del Turno:**:
  - **Justificación:** El turno de los jugadores se gestiona mediante la variable **turno_actual**, que se cambia después de cada jugada. El jugador no puede jugar fuera de su turno, ya que la sincronización está asegurada por el **Lock**.
  
---

## 🚀 Instalación y Ejecución

### 1⃣  Clonar el repositorio
```bash
git clone https://github.com/Isaili/Simulaci-n-de-Tinaco-Concurrente.git
```

### 2⃣  Ejecutar la aplicación
```bash
python main.py
```

