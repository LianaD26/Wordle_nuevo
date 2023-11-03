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

    def reiniciar_juego(self):
        self.palabra_correcta = self.get_random_word(5)
        self.tablero = Tablero(self.palabra_correcta)
        self.entrada_palabra.delete(0, tk.END)
        self.etiqueta_error.config(text="")
        self.etiqueta_tablero.config(text="")
        self.actualizar_tablero()
        self.tiempo_inicio = None
        self.cronometro_corriendo = False
        self.etiqueta_cronometro.config(text="Tiempo: 00:00")
        if self.resultado_ventana:
            self.resultado_ventana.destroy()
        self.boton_adivinar.config(state="normal")

    def adivinar_palabra(self):
        palabra = self.entrada_palabra.get()
        if not self.cronometro_corriendo:
            self.iniciar_cronometro()
            self.cronometro_corriendo = True

        if len(palabra) == 5 and palabra.isalpha() and palabra.islower():
            self.etiqueta_error.config(text="")
            self.tablero.actualizar_tablero(palabra)
            self.actualizar_tablero()
            if "".join(self.tablero.matriz[self.tablero.num_intentos - 1]) == self.palabra_correcta:
                self.etiqueta_tablero.config(text="¡Has adivinado la palabra!")
                self.detener_cronometro()
                self.guardar_resultado(self.palabra_correcta, palabra, "Victoria")
                self.mostrar_resultados()
                self.boton_adivinar.config(state="disabled")
            elif self.tablero.num_intentos == 6:
                self.etiqueta_tablero.config(
                    text=f"¡Agotaste tus intentos! La palabra correcta era: {self.palabra_correcta}")
                self.detener_cronometro()
                self.guardar_resultado(self.palabra_correcta, palabra, "Derrota")
                self.mostrar_resultados()
                self.boton_adivinar.config(state="disabled")
        else:
            self.etiqueta_error.config(text="Por favor, ingresa una palabra válida de 5 letras en minúsculas.")

    def mostrar_resultados(self):
        if self.resultado_ventana:
            self.resultado_ventana.destroy()

        self.resultado_ventana = tk.Toplevel(self.ventana)
        self.resultado_ventana.title("Resultados")
        # leer los resultados del juego
        with open(HISTORIAL_JUEGOS_FILE, "r") as file:
            historial = file.readlines()

        # Calcular estadísticas
        partidas_jugadas = len(historial)
        victorias = historial.count("Victoria\n")
        racha_actual = 0
        mejor_racha = 0
        intentos_frecuencia = {}

        tk.Label(self.resultado_ventana, text=f"Partidas Jugadas: {partidas_jugadas}", font=("Courier", 12)).pack()

        if partidas_jugadas > 0:
            porcentaje_victorias = (victorias / partidas_jugadas) * 100
        else:
            porcentaje_victorias = 0

        tk.Label(self.resultado_ventana, text=f"% Victorias: {porcentaje_victorias:.2f}%", font=("Courier", 12)).pack()
        tk.Label(self.resultado_ventana, text=f"Racha Actual: {racha_actual}", font=("Courier", 12)).pack()
        tk.Label(self.resultado_ventana, text=f"Mejor Racha: {mejor_racha}", font=("Courier", 12)).pack()

        # Conteo de los intentos
        for juego in historial:
            intentos = juego.count("_")  # el _ es un intento fallido
            if intentos in intentos_frecuencia:
                intentos_frecuencia[intentos] += 1
            else:
                intentos_frecuencia[intentos] = 1

        if intentos_frecuencia:
            tk.Label(self.resultado_ventana, text="Frecuencia de Intentos:", font=("Courier", 12)).pack()
            for intentos, frecuencia in intentos_frecuencia.items():
                tk.Label(self.resultado_ventana, text=f"{intentos} intentos: {frecuencia}", font=("Courier", 12)).pack()

        if historial:
            last_result = historial[-1]
            last_correct_word = last_result.split(":")[1].strip()
            tk.Label(self.resultado_ventana, text=f"Palabra correcta del último juego: {last_correct_word}",
                     font=("Courier", 12)).pack()

    def guardar_resultado(self, palabra_correcta, palabra_ingresada, resultado):
        resultado_texto = f"Palabra correcta: {palabra_correcta}, Palabra ingresada: {palabra_ingresada}, Resultado: {resultado}, Intentos: {self.tablero.num_intentos}\n"
        with open(HISTORIAL_JUEGOS_FILE, "a") as file:
            file.write(resultado_texto)

    def iniciar_cronometro(self):
        self.tiempo_inicio = time.time()
        self.actualizar_cronometro()
        self.boton_reiniciar.config(state="disabled")
        self.boton_salir.config(state="disabled")

    def detener_cronometro(self):
        self.tiempo_inicio = None
        self.boton_reiniciar.config(state="normal")
        self.boton_salir.config(state="normal")

    def actualizar_cronometro(self):
        if self.tiempo_inicio:
            tiempo_transcurrido = time.time() - self.tiempo_inicio
            minutos = int(tiempo_transcurrido // 60)
            segundos = int(tiempo_transcurrido % 60)
            tiempo_formateado = f"Tiempo: {minutos:02d}:{segundos:02d}"
            self.etiqueta_cronometro.config(text=tiempo_formateado)
            self.ventana.after(1000, self.actualizar_cronometro)

    def actualizar_tablero(self):
        for i in range(6):
            for j in range(5):
                letra = self.tablero.matriz[i][j]
                label = self.tablero_labels[i][j]
                if letra == "_":
                    label.config(text=letra, bg="white")
                elif letra == self.palabra_correcta[j]:
                    label.config(text=letra, bg="green")
                elif letra in self.palabra_correcta:
                    label.config(text=letra, bg="yellow")
                else:
                    label.config(text=letra, bg="white")

    def get_random_word(self, length):
        random_word_api_url = "https://random-word-api.herokuapp.com/word"
        random_word_api_response = requests.get(random_word_api_url, params={"length": length, "lang": "en"})
        random_word = random_word_api_response.json()[0]
        return random_word

    def get_word_definition(self, word):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        return response

if __name__ == "__main__":
    ventana = tk.Tk()
    ventana.configure(bg="white")
    juego = PalabraJuego(ventana)
    ventana.mainloop()
