import pygame
import time

# Inicializar pygame
pygame.mixer.init()

# Cargar el archivo de audio
pygame.mixer.music.load("./audio/ECCENTRIC_LEVER.wav")

# Reproducir el audio
pygame.mixer.music.play()

# Esperar a que termine (ejemplo de pausa de 10 segundos)
time.sleep(10)

# Detener la reproducción
pygame.mixer.music.stop()

