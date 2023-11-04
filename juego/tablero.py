class Tablero:
    def __init__(self, palabra_correcta):
        self.num_intentos = 0
        self.matriz = []
        self.palabra_correcta = palabra_correcta
        self.llenar_matriz()

    def llenar_matriz(self):
        for i in range(6):
            self.matriz.append(["_" for _ in range(5)])

    def actualizar_tablero(self, palabra):

        if self.num_intentos < 6:
            if palabra == self.palabra_correcta:
                for i, letra in enumerate(palabra):
                    self.matriz[self.num_intentos][i] = letra
                self.num_intentos = 6
                return
            else:
                for i, letra in enumerate(palabra):
                    if letra == self.palabra_correcta[i]:
                        self.matriz[self.num_intentos][i] = letra
                    elif letra in self.palabra_correcta:
                        self.matriz[self.num_intentos][i] = letra.lower()
                    else:
                        self.matriz[self.num_intentos][i] = letra
                self.num_intentos += 1
