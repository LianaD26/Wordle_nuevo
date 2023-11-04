import textwrap
from tkinter import *
import time
import matplotlib.pyplot as plt
from juego.api import WordFetcher
from juego.tablero import Tablero
import requests

class PalabraJuego:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Wordle")
        self.ventana.configure(bg="white")
        self.intentos = 0
        self.api = WordFetcher()

        for i in range(11):
            self.ventana.rowconfigure(i, weight=1)
        for j in range(5):
            self.ventana.columnconfigure(j, weight=1)

        self.palabra_correcta = self.api.get_random_word()
        self.tablero = Tablero(self.palabra_correcta)

        self.etiqueta = Label(ventana, text="WORDLE", font=("Courier", 16))
        self.etiqueta.grid(row=0, column=0, columnspan=5, sticky="nsew")

        self.etiqueta_palabra = Label(ventana, text="Ingresa una palabra de 5 letras en minúsculas:", font=("Courier", 12))
        self.etiqueta_palabra.grid(row=1, column=0, columnspan=5, sticky="nsew")

        self.entrada_palabra = Entry(ventana, font=("Courier", 12))
        self.entrada_palabra.grid(row=2, column=0, columnspan=5, sticky="nsew")

        self.etiqueta_error = Label(ventana, text="", fg="red", font=("Courier", 12))
        self.etiqueta_error.grid(row=4, column=0, columnspan=5, sticky="nsew")

        self.etiqueta_tablero = Label(ventana, text="", font=("Courier", 16))
        self.etiqueta_tablero.grid(row=11, column=0, columnspan=5, sticky="nsew")

        self.tablero_labels = []
        for i in range(6):
            fila_labels = []
            for j in range(5):
                label = Label(ventana, text="", width=2, height=1, font=("Courier", 16),
                              relief="solid", borderwidth=1)
                label.grid(row=i + 5, column=j, sticky="nsew")
                fila_labels.append(label)
            self.tablero_labels.append(fila_labels)

        self.tiempo_inicio = None
        self.cronometro_corriendo = False

        self.etiqueta_cronometro = Label(ventana, text="Tiempo: 00:00", font=("Courier", 12))
        self.etiqueta_cronometro.grid(row=11, column=5, sticky="nsew")

        self.resultado_ventana = None

        self.boton_reiniciar = Button(ventana, text="Reiniciar Juego", command=self.reiniciar_juego, font=("Courier", 12))
        self.boton_reiniciar.grid(row=5, column=5, columnspan=5, sticky="nsew")

        self.boton_salir = Button(ventana, text="Salir", command=ventana.quit, font=("Courier", 12))
        self.boton_salir.grid(row=6, column=5, columnspan=5, sticky="nsew")

        self.boton_adivinar = Button(ventana, text="Adivinar", command=self.adivinar_palabra, font=("Courier", 12))
        self.boton_adivinar.grid(row=3, column=0, columnspan=5, sticky="nsew")

    def reiniciar_juego(self):

        self.palabra_correcta = self.api.get_random_word()
        self.tablero = Tablero(self.palabra_correcta)
        self.entrada_palabra.delete(0, END)
        self.etiqueta_error.config(text="")
        self.etiqueta_tablero.config(text="")
        self.actualizar_tablero()
        self.tiempo_inicio = None
        self.cronometro_corriendo = False
        self.etiqueta_cronometro.config(text="Tiempo: 00:00")
        self.resultado_ventana.destroy() if self.resultado_ventana else None
        self.boton_adivinar.config(state="normal")

    def adivinar_palabra(self):
        palabra = self.entrada_palabra.get()
        if not self.cronometro_corriendo:
            self.iniciar_cronometro()
            self.cronometro_corriendo = True

        valid_words_api_url = "https://random-word-api.herokuapp.com/all"
        valid_words_response = requests.get(valid_words_api_url)

        if valid_words_response.status_code == 200:
            valid_words = valid_words_response.json()

            if palabra in valid_words:
                self.etiqueta_error.config(text="")
                self.tablero.actualizar_tablero(palabra)
                self.actualizar_tablero()

                if palabra == self.palabra_correcta:
                    self.etiqueta_tablero.config(text="¡Has adivinado la palabra!")
                    self.detener_cronometro()
                    self.mostrar_resultados(resultado="Victoria")
                    self.boton_adivinar.config(state="disabled")

                    # Llamar aquí a guardar resultado
                    intentos = self.intentos + 1
                    self.guardar_resultado(self.palabra_correcta, palabra, "Victoria", intentos)
                else:
                    self.intentos += 1
                    if self.tablero.num_intentos == 6:
                        self.etiqueta_tablero.config(
                            text=f"¡Agotaste tus intentos! La palabra correcta era: {self.palabra_correcta}")
                        self.detener_cronometro()
                        self.mostrar_resultados(resultado="Derrota")
                        self.boton_adivinar.config(state="disabled")

                        intentos = 6
                        self.guardar_resultado(self.palabra_correcta, palabra, "Derrota", intentos)
            else:
                self.etiqueta_error.config(
                    text="Por favor, ingresa una palabra válida que exista en la lista de palabras.")
        else:
            self.etiqueta_error.config(text="No se pudo obtener la lista de palabras válidas desde la API.")

    # Resto del método
    def mostrar_resultados(self, resultado):
        intentos = self.tablero.num_intentos
        if self.resultado_ventana:
            self.resultado_ventana.destroy()
        self.resultado_ventana = Toplevel(self.ventana)
        self.resultado_ventana.title("Resultados")

        # Calcula estadísticas
        partidas_jugadas, victorias, racha_actual, mejor_racha = self.calcular_estadisticas()

        # Agrega el resultado actual al historial de juegos solo en caso de victoria
        if resultado == "Victoria":
            self.guardar_resultado(self.palabra_correcta, self.entrada_palabra.get(), resultado, intentos)

        # Obtener el significado de la palabra correcta
        palabra_correcta = self.palabra_correcta
        definition = self.api.get_random_word_with_meaning()

        # Muestra estadísticas en la nueva ventana
        Label(self.resultado_ventana, text=f"Partidas Jugadas: {partidas_jugadas}", font=("Courier", 12)).pack()

        if partidas_jugadas > 0:
            porcentaje_victorias = (victorias / partidas_jugadas) * 100
        else:
            porcentaje_victorias = 0

        Label(self.resultado_ventana, text=f"% Victorias: {porcentaje_victorias:.2f}%", font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"Racha Actual: {racha_actual}", font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"Mejor Racha: {mejor_racha}", font=("Courier", 12)).pack()

        # Muestra el significado de la palabra correcta o un mensaje de error
        if definition == "No se encontró una definición para esta palabra.":
            Label(self.resultado_ventana, text=f"Palabra correcta: {palabra_correcta}", font=("Courier", 12)).pack()
            Label(self.resultado_ventana, text="Significado no encontrado.", font=("Courier", 12)).pack()
        else:
            significado_lineas = "\n".join(
                textwrap.wrap(definition, width=40))  # Ajusta el texto a 40 caracteres por línea
            Label(self.resultado_ventana, text=f"Palabra correcta: {palabra_correcta}", font=("Courier", 12)).pack()
            Label(self.resultado_ventana, text=f"Significado:", font=("Courier", 12)).pack()
            Label(self.resultado_ventana, text=significado_lineas, font=("Courier", 12)).pack()

        self.mostrar_grafico()
    def calcular_estadisticas(self):

        partidas_jugadas, victorias, racha_actual, mejor_racha = 0, 0, 0, 0

        with open("historial_juegos.txt", "r") as file:
            lines = file.readlines()

            for line in lines:
                if "Victoria" in line:
                    victorias += 1
                    racha_actual += 1
                    mejor_racha = max(mejor_racha, racha_actual)
                else:
                    racha_actual = 0

            partidas_jugadas = len(lines)

        return partidas_jugadas, victorias, racha_actual, mejor_racha

    def guardar_resultado(self, palabra_correcta, palabra_ingresada, resultado, intentos):
        historial_juegos_file = "historial_juegos.txt"

        if resultado == "Victoria" and intentos <= 5:
            with open(historial_juegos_file, "a") as file:
                file.write(
                    f"Palabra correcta: {palabra_correcta}, Palabra ingresada: {palabra_ingresada}, Resultado: {resultado}, Intentos: {intentos}\n")
        elif resultado == "Derrota":
            with open(historial_juegos_file, "a") as file:
                file.write(
                    f"Palabra correcta: {palabra_correcta}, Palabra ingresada: {palabra_ingresada}, Resultado: {resultado}, Intentos: 6\n")

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

    def mostrar_grafico(self):
        # Contar la frecuencia de adivinanzas exitosas en cada cantidad de intentos
        exitos_por_intentos = [0] * 6
        with open("historial_juegos.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                if "Victoria" in line:
                    intentos = int(line.split(", Intentos: ")[1])  # Obtener la cantidad de intentos
                    exitos_por_intentos[intentos - 1] += 1  # Restar 1 para ajustar al índice del arreglo

        # Etiquetas para el eje X del gráfico
        labels = [f"{i} intentos" for i in range(1, 7)]

        # Crear el gráfico de barras
        plt.figure(figsize=(10, 6))
        plt.bar(labels, exitos_por_intentos, color='lightblue')
        plt.xlabel('Intentos')
        plt.ylabel('Frecuencia de Adivinanzas Exitosas')
        plt.title('Frecuencia de Adivinanzas Exitosas por Cantidad de Intentos')
        plt.tight_layout()

        # Mostrar el gráfico
        plt.show()