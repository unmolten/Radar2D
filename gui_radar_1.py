import pygame
import math
import serial
import time
import sys

PUERTO  = 'COM4'
BAUDIOS = 9600
MAX_CM  = 150

ANCHO, ALTO = 800, 800
CX, CY      = 400, 400
RADIO   = 340

MARGEN_ANG  = 15
MARGEN_DIST = 30

pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Radar 2D")
reloj = pygame.time.Clock()
font  = pygame.font.SysFont("Courier New", 13)

try:
    puerto = serial.Serial(PUERTO, BAUDIOS, timeout=0.05)
except Exception as e:
    print(f"Error: {e}"); sys.exit()

def polar_a_px(dist, ang):
    r   = (dist / MAX_CM) * RADIO
    rad = math.radians(ang)
    return int(CX + r * math.cos(rad)), int(CY - r * math.sin(rad))

lecturas  = []
ang_actual = 0

def agrupar(lecturas):
    usada   = [False] * len(lecturas)
    objetos = []
    for i, a in enumerate(lecturas):
        if usada[i]:
            continue
        grupo = [a]
        usada[i] = True
        for j, b in enumerate(lecturas):
            if usada[j]:
                continue
            ang_g  = sum(x["ang"]  for x in grupo) / len(grupo)
            dist_g = sum(x["dist"] for x in grupo) / len(grupo)
            if abs(ang_g - b["ang"]) < MARGEN_ANG and abs(dist_g - b["dist"]) < MARGEN_DIST:
                grupo.append(b)
                usada[j] = True

        # Ordenar por tiempo: el más viejo = posición actual, el más nuevo = futuro
        grupo.sort(key=lambda x: x["tiempo"])
        actual = grupo[0]
        futuro = grupo[-1]  # si solo hay uno, actual == futuro

        dt  = futuro["tiempo"] - actual["tiempo"]
        vel = round(abs(futuro["dist"] - actual["dist"]) / dt, 1) if dt > 0 else 0.0

        objetos.append({
            "ang":    actual["ang"],
            "dist":   actual["dist"],
            "ang_f":  futuro["ang"],
            "dist_f": futuro["dist"],
            "vel":    vel,
            "mismo":  actual["tiempo"] == futuro["tiempo"]  # sin movimiento detectado
        })
    return objetos

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    try:
        linea  = puerto.readline().decode('utf-8').strip()
        partes = linea.split(',')
        if len(partes) == 2:
            ang  = int(partes[0])
            dist = float(partes[1])
            ang_actual = ang
            if dist < MAX_CM:
                lecturas.append({"ang": ang, "dist": dist, "tiempo": time.time()})
    except Exception:
        pass

    ahora    = time.time()

    if lecturas and ahora - min(l["tiempo"] for l in lecturas) > 2.0:
        lecturas = []
    else:
        lecturas = [l for l in lecturas if ahora - l["tiempo"] < 2.0]
    objetos  = agrupar(lecturas)

    objetos = objetos[:5]

    ventana.fill((0, 0, 0))

    pygame.draw.circle(ventana, (0, 15, 4),  (CX, CY), RADIO)
    pygame.draw.circle(ventana, (0, 60, 15), (CX, CY), RADIO,      2)
    pygame.draw.circle(ventana, (0, 40, 10), (CX, CY), RADIO // 2, 1)
    pygame.draw.circle(ventana, (0, 40, 10), (CX, CY), RADIO // 4, 1)
    pygame.draw.line(ventana, (0, 60, 15), (CX - RADIO, CY), (CX + RADIO, CY), 1)

    ventana.blit(font.render("50cm",  True, (0, 100, 25)), (CX + RADIO//4 + 3, CY - 12))
    ventana.blit(font.render("100cm", True, (0, 100, 25)), (CX + RADIO//2 + 3, CY - 12))
    ventana.blit(font.render("200cm", True, (0, 100, 25)), (CX + RADIO + 3,    CY - 12))

    rad_sweep = math.radians(ang_actual)
    pygame.draw.line(ventana, (0, 200, 50), (CX, CY),
                     (int(CX + RADIO * math.cos(rad_sweep)),
                      int(CY - RADIO * math.sin(rad_sweep))), 2)

    for obj in objetos:
        px, py = polar_a_px(obj["dist"], obj["ang"])
        pygame.draw.circle(ventana, (0, 255, 70), (px, py), 7)

        if not obj["mismo"]:
            fx, fy = polar_a_px(obj["dist_f"], obj["ang_f"])
            pygame.draw.circle(ventana, (150, 150, 150), (fx, fy), 4)
            pygame.draw.line(ventana, (80, 80, 80), (px, py), (fx, fy), 1)

        label = f"{obj['dist']:.0f}cm | {obj['vel']:.1f}cm/s"
        ventana.blit(font.render(label, True, (255, 220, 0)), (px + 9, py - 7))

    ventana.blit(font.render(f"Angulo:  {ang_actual}°",  True, (0, 200, 50)),    (10, 10))
    ventana.blit(font.render(f"Objetos: {len(objetos)}", True, (0, 200, 50)),    (10, 27))
    ventana.blit(font.render("● verde = objeto",         True, (0, 200, 50)),    (10, 50))
    ventana.blit(font.render("● gris  = pos. futura",    True, (150, 150, 150)), (10, 67))

    pygame.display.flip()
    reloj.tick(60)