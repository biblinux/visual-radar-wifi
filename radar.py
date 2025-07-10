import pygame
import pywifi
import time
import math
import random
import threading

pygame.init()
WIDTH, HEIGHT = 800, 800
CENTER = WIDTH // 2, HEIGHT // 2
RADIUS = 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WiFi Radar Scanner")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 14)
GREEN = (0, 255, 0)
RED = (255, 60, 60)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

radar_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

networks = []
sweep_history = []

def scan_wifi():
    global networks
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(2)
    results = iface.scan_results()

    new_networks = []
    for net in results:
        ssid = net.ssid
        signal = max(0, min(100, 100 + net.signal))
        if ssid:
            angle = random.uniform(0, 2 * math.pi)
            new_networks.append({
                'ssid': ssid,
                'signal': signal,
                'angle': angle,
                'last_seen': 0,
                'alpha': 0
            })
    networks = new_networks

def auto_refresh_scan(interval=6.5):
    while running:
        scan_wifi()
        time.sleep(interval)

def draw_radar(sweep_angle):
    screen.fill(BLACK)
    radar_surface.fill((0, 0, 0, 0))
    trail_surface.fill((0, 0, 0, 15))

    for r in range(50, RADIUS + 1, 50):
        pygame.draw.circle(screen, GREEN, CENTER, r, 1)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x = CENTER[0] + RADIUS * math.cos(rad)
        y = CENTER[1] + RADIUS * math.sin(rad)
        pygame.draw.line(screen, GREEN, CENTER, (x, y), 1)

    now = time.time()

    for offset in range(-6, 7):
        alpha = max(0, 180 - abs(offset) * 25)
        aura_color = (0, 255, 0, alpha)
        sweep = sweep_angle + math.radians(offset)
        x = CENTER[0] + RADIUS * math.cos(sweep)
        y = CENTER[1] + RADIUS * math.sin(sweep)
        pygame.draw.line(radar_surface, aura_color, CENTER, (x, y), 2)

    x1 = CENTER[0] + RADIUS * math.cos(sweep_angle)
    y1 = CENTER[1] + RADIUS * math.sin(sweep_angle)
    pygame.draw.line(trail_surface, (0, 255, 0, 40), CENTER, (x1, y1), 2)

    for net in networks:
        angle = net['angle']
        signal = net['signal']
        r = (1 - (signal / 100)) * RADIUS
        nx = CENTER[0] + r * math.cos(angle)
        ny = CENTER[1] + r * math.sin(angle)

        diff = abs((sweep_angle - angle + math.pi * 2) % (math.pi * 2))
        if diff < math.radians(3):
            net['last_seen'] = now
            net['alpha'] = 255

        time_since = now - net['last_seen']
        net['alpha'] = max(0, 255 - int(time_since * 85))

        if net['alpha'] > 0:
            fade_color = (255, 60, 60, net['alpha'])
            pygame.draw.circle(radar_surface, fade_color, (int(nx), int(ny)), 6)
            label = FONT.render(net['ssid'], True, WHITE)
            screen.blit(label, (nx + 6, ny))

    screen.blit(trail_surface, (0, 0))
    screen.blit(radar_surface, (0, 0))

running = True
sweep_angle = 0
scan_wifi()

scan_thread = threading.Thread(target=auto_refresh_scan, daemon=True)
scan_thread.start()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    sweep_angle += 0.02
    if sweep_angle > 2 * math.pi:
        sweep_angle = 0

    draw_radar(sweep_angle)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
