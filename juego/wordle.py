from tkinter import *
import os
from juego.palabra import PalabraJuego

historial_juegos_file = "historial_juegos.txt"

if not os.path.exists(historial_juegos_file):
    with open(historial_juegos_file, "w") as file:
        pass

ventana = Tk()

if __name__ == "__main__":
    ventana.configure(bg="white")
    juego = PalabraJuego(ventana)
    ventana.mainloop()

