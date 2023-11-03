import textwrap
import tkinter as tk
import requests
import time

HISTORIAL_JUEGOS_FILE = "historial_juegos.txt"

class Tablero:
    def __init__(self, palabra_correcta):
        self.num_intentos = 0
        self.matriz = [["_" for _ in range(5)] for _ in range(6)]
        self.palabra_correcta = palabra_correcta

    def actualizar_tablero(self, palabra):
        if self.num_intentos < 6:
            if palabra == self.palabra_correcta:
                self.matriz[self.num_intentos] = list(palabra)
                self.num_intentos = 6
            else:
                self.actualizar_matriz(palabra)
                self.num_intentos += 1

    def actualizar_matriz(self, palabra):
        for i, letra in enumerate(palabra):
            if letra == self.palabra_correcta[i]:
                self.matriz[self.num_intentos][i] = letra
            elif letra in self.palabra_correcta:
                self.matriz[self.num_intentos][i] = letra.lower()
            else:
                self.matriz[self.num_intentos][i] = letra

class PalabraJuego:
    def __init__(self, ventana):
        self.ventana = ventana
        self.inicializar_ventana()
        self.palabra_correcta = self.get_random_word(5)
        self.tablero = Tablero(self.palabra_correcta)
        self.resultado_ventana = None
        self.cronometro_corriendo = False

    def inicializar_ventana(self):
        self.ventana.title("Wordle")
        self.ventana.configure(bg="white")
        for i in range(11):
            self.ventana.rowconfigure(i, weight=1)
        for j in range(5):
            self.ventana.columnconfigure(j, weight=1)
        self.crear_interfaz()

    def crear_interfaz(self):
        self.etiqueta = self.crear_label("WORDLE", 0, 0, 5, "nsew", ("Courier", 16))
        self.etiqueta_palabra = self.crear_label("Ingresa una palabra de 5 letras en minúsculas:", 1, 0, 5, "nsew", ("Courier", 12))
        self.entrada_palabra = self.crear_entry(2, 0, 5, "nsew", ("Courier", 12))
        self.etiqueta_error = self.crear_label("", 4, 0, 5, "nsew", ("Courier", 12))
        self.etiqueta_tablero = self.crear_label("", 11, 0, 5, "nsew", ("Courier", 16))
        self.crear_tablero_labels()
        self.etiqueta_cronometro = self.crear_label("Tiempo: 00:00", 11, 5, "nsew", ("Courier", 12))
        self.boton_reiniciar = self.crear_button("Reiniciar Juego", self.reiniciar_juego, 5, 5, 5, "nsew", ("Courier", 12))
        self.boton_salir = self.crear_button("Salir", self.ventana.quit, 6, 5, 5, "nsew", ("Courier", 12))
        self.boton_adivinar = self.crear_button("Adivinar", self.adivinar_palabra, 3, 0, 5, "nsew", ("Courier", 12))

    def crear_label(self, text, row, column, colspan, sticky, font):
        label = tk.Label(self.ventana, text=text, font=font)
        label.grid(row=row, column=column, columnspan=colspan, sticky=sticky)
        return label

    def crear_entry(self, row, column, colspan, sticky, font):
        entry = tk.Entry(self.ventana, font=font)
        entry.grid(row=row, column=column, columnspan=colspan, sticky=sticky)
        return entry

    def crear_button(self, text, command, row, column, colspan, sticky, font):
        button = tk.Button(self.ventana, text=text, command=command, font=font)
        button.grid(row=row, column=column, columnspan=colspan, sticky=sticky)
        return button

    def crear_tablero_labels(self):
        self.tablero_labels = []
        for i in range(6):
            fila_labels = []
            for j in range(5):
                label = tk.Label(self.ventana, text="", width=2, height=1, font=("Courier", 16),
                                 relief="solid", borderwidth=1)
                label.grid(row=i + 5, column=j, sticky="nsew")
                fila_labels.append(label)
            self.tablero_labels.append(fila_labels)

    # Resto del código...

if __name__ == "__main__":
    ventana = tk.Tk()
    ventana.configure(bg="white")
    juego = PalabraJuego(ventana)
    ventana.mainloop()
