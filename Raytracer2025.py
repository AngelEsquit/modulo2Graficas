import pygame
from pygame.locals import *
from gl import Renderer
from BMP_Writer import GenerateBMP

width = 256
height = 256

pygame.init()
screen = pygame.display.set_mode((width, height), pygame.SCALED)
pygame.display.set_caption("Simple RayTracer - Esferas (Phong)")
clock = pygame.time.Clock()

rend = Renderer(screen)

isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == QUIT:
            isRunning = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                isRunning = False
            elif event.key == K_r:
                rend.restart_render()

    rend.glRender()

    pygame.display.flip()
    clock.tick(60)

GenerateBMP("output.bmp", width, height, 3, rend.frameBuffer)

pygame.quit()