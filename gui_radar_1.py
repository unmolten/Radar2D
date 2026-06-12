import pygame
import math
import serial
import sys

# === CONFIGURACIÓN ===
PUERTO  = 'COM4'
BAUDIOS = 9600
MAX_CM  = 200  # rango máximo del sensor

# === VENTANA Y RADAR ===
ANCHO = 700
ALTO = 600
CX = 350
CY = 400 # centro del radar en pantalla
RADIO = 300 # radio del círculo en píxeles

pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Radar 2D")
reloj   = pygame.time.Clock()
font    = pygame.font.SysFont("Courier New", 13)

# === ABRIR SERIAL ===
try:
    puerto = serial.Serial(PUERTO, BAUDIOS, timeout=0.05)
except Exception as e:
    print(f"Error: {e}")
    sys.exit()

# === CONVERTIR ÁNGULO Y DISTANCIA A PÍXELES ===
def polar_a_px(dist, ang):
    r   = (dist / MAX_CM) * RADIO
    rad = math.radians(ang)
    x   = int(CX + r * math.cos(rad))
    y   = int(CY - r * math.sin(rad))
    return x, y

# === LOOP PRINCIPAL ===
puntos = []   # lista de (x, y) para dibujar

while True:
    # Salir con la X o ESC
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    # Leer serial
    try:
        linea  = puerto.readline().decode('utf-8').strip()
        partes = linea.split(',')
        if len(partes) == 2:
            ang  = int(partes[0])
            dist = float(partes[1])
            if dist < MAX_CM:
                puntos.append(polar_a_px(dist, ang))
    except Exception:
        pass

    # Limpiar pantalla
    ventana.fill((0, 0, 0))

    # Dibujar círculo del radar y líneas de referencia
    pygame.draw.circle(ventana, (0, 60, 15), (CX, CY), RADIO, 2)
    pygame.draw.circle(ventana, (0, 40, 10), (CX, CY), RADIO // 2, 1)
    pygame.draw.line(ventana, (0, 60, 15), (CX - RADIO, CY), (CX + RADIO, CY), 1)

    # Etiquetas de distancia
    ventana.blit(font.render("100cm", True, (0, 120, 30)), (CX + RADIO//2 + 3, CY - 12))
    ventana.blit(font.render("200cm", True, (0, 120, 30)), (CX + RADIO + 3,    CY - 12))

    # Dibujar puntos detectados
    for px, py in puntos:
        pygame.draw.circle(ventana, (0, 255, 70), (px, py), 5)

    # Texto básico
    ventana.blit(font.render(f"Objetos: {len(puntos)}", True, (0, 200, 50)), (10, 10))

    pygame.display.flip()
    reloj.tick(60)
