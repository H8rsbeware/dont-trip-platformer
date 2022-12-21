import pygame

def debugGrid(DISPLAY, WINWIDTH, WINHEIGHT, GAP, colour):
    for x in range(0, WINWIDTH, GAP):
        pygame.draw.line(DISPLAY, colour, (x, 0), (x, WINHEIGHT))

def debugCharacterSize(DISPLAY, colour, GAP, charSizeX, charSizeY, charSprite=False):
    if not charSprite:
        pygame.draw.rect(DISPLAY, (180, 0, 0), pygame.Rect(GAP, GAP, charSizeX, charSizeY))
    pygame.draw.rect(DISPLAY, colour, pygame.Rect(1, GAP + charSizeY, GAP * 2, charSizeY))