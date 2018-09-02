'''Python_Shooter 1

Pygame penceresi ve oyun döngüsü
'''

import sys
import pygame

# Global Constants
VERSION = "0.01"
NAME = "Python Shooter " + VERSION
SCREEN_SIZE = (450,600)
FPS = 50

clock = pygame.time.Clock()

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
caption = pygame.display.set_caption(NAME)

# Game Loop
while True:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
        clock.tick(FPS)
        pygame.display.flip()