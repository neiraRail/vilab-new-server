import time
class Reloj:
    """Clase que permite medir el tiempo de ejecución de un programa y la frecuencia de ejecución de un programa"""
    def __init__(self):
        self.contador = 0
        self.start = time.time_ns()

    def mostrarFrecuencia(self):
        end = time.time_ns()
        if end - self.start == 0:
            return 0

        # Frencuencia en Hz
        frecuencia = self.contador/(end-self.start)
        frecuencia = frecuencia * 10**9

        self.contador = 0
        self.start = time.time_ns()

        print("Frecuencia: ", round(frecuencia))

        return frecuencia
    
    def aumentarContador(self):
        self.contador += 1
